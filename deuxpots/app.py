from dataclasses import asdict
import json
from flask import Flask
from flask import Flask, request
from flask_cors import CORS

from deuxpots import CERFA_VARIABLES_PATH, FAMILY_BOX_COORDS_PATH
from deuxpots.box import load_box_mapping
from deuxpots.flatbox import FlatBox, flatten
from deuxpots.individualize import simulate_and_individualize
from deuxpots.pdf_tax_parser import load_family_box_coords, parse_tax_pdf
from deuxpots.valued_box import ValuedBox

BOX_MAPPING = load_box_mapping(CERFA_VARIABLES_PATH)
FAMILY_BOX_COORDS = load_family_box_coords(FAMILY_BOX_COORDS_PATH)


app = Flask("deuxpots")
CORS(app, CORS_ALLOW_HEADERS="*")


@app.route('/parse', methods=['POST'])
def parse():
    tax_pdf = request.files['tax_pdf'].read()
    valboxes = parse_tax_pdf(tax_pdf, FAMILY_BOX_COORDS, BOX_MAPPING)
    return dict(
        boxes=[asdict(flatten(valbox)) for valbox in valboxes]
    )


@app.route('/individualize', methods=['POST'])
def individualize():
    user_boxes = [FlatBox(code=box['code'],
                          raw_value=box['raw_value'],
                          attribution=box['attribution'])
                  for box in request.json['boxes']]
    valboxes = [ValuedBox.from_flat_box(flatbox, BOX_MAPPING)
                for flatbox in user_boxes]
    result = simulate_and_individualize(valboxes)
    return dict(
        individualized=asdict(result)
    )


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8888, debug=True)
