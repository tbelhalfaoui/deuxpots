from dataclasses import asdict
import json
from flask import Flask
from flask import Flask, request
import flask
from deuxpots import CERFA_VARIABLES_PATH, FAMILY_BOX_COORDS_PATH

from deuxpots.box import load_box_mapping
from deuxpots.individualize import simulate_and_individualize
from deuxpots.pdf_tax_parser import load_family_box_coords, parse_tax_pdf

BOX_MAPPING = load_box_mapping(CERFA_VARIABLES_PATH)
FAMILY_BOX_COORDS = load_family_box_coords(FAMILY_BOX_COORDS_PATH)


app = Flask("deuxpots")


@app.route('/individualize', methods=['POST'])
def individualize():
    user_boxes = json.loads(request.form['boxes'])
    tax_pdf = request.files['tax_pdf'].read()
    parsed_sheeet = parse_tax_pdf(tax_pdf, FAMILY_BOX_COORDS)
    user_ratios = {box['code']: box['ratio_0'] for box in user_boxes}
    result = simulate_and_individualize(parsed_sheeet, user_ratios, BOX_MAPPING)
    response = dict(
        boxes=list(map(serialize_box, result['boxes'])),
        individualized=asdict(result['individualized']) if result.get('individualized') else None
    )
    response = flask.jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

def serialize_box(valbox):
    return dict(
        code=valbox.box.code,
        description=valbox.box.reference.description,
        raw_value=valbox.raw_value,
        ratio_0=valbox.ratio_0,
    )


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8888, debug=True)
