from dataclasses import asdict
import json
import logging
from flask import Flask
from flask import Flask, request
import flask
from flask_cors import CORS

from deuxpots import CERFA_VARIABLES_PATH, FAMILY_BOX_COORDS_PATH
from deuxpots.box import load_box_mapping
from deuxpots.individualize import simulate_and_individualize
from deuxpots.pdf_tax_parser import HOUSEHOLD_STATUS_FIELD, HOUSEHOLD_STATUS_VALUES_TOGETHER, load_family_box_coords, parse_tax_pdf

BOX_MAPPING = load_box_mapping(CERFA_VARIABLES_PATH)
FAMILY_BOX_COORDS = load_family_box_coords(FAMILY_BOX_COORDS_PATH)


app = Flask("deuxpots")
CORS(app, CORS_ALLOW_HEADERS="*")


@app.route('/parse', methods=['POST'])
def parse():
    tax_pdf = request.files['tax_pdf'].read()
    valboxes = parse_tax_pdf(tax_pdf, FAMILY_BOX_COORDS, BOX_MAPPING)
    return dict(
        boxes=[asdict(valbox) for valbox in valboxes]
    )


@app.route('/individualize', methods=['POST'])
def individualize():
    user_boxes = json.loads(request.form['boxes'])
    result = simulate_and_individualize(user_boxes, BOX_MAPPING)
    return dict(
        individualized=asdict(result)
    )

def toto():
    print("***** hello")
    logging.info('**** This is an info')
    logging.warning('**** This is a warning')
    logging.error('**** This is an error')
    assert False


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8888, debug=True)
