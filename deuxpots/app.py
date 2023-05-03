from dataclasses import asdict
import json
from flask import Flask
from flask import Flask, request

from deuxpots.box import load_box_mapping
from deuxpots.individualize import simulate_and_individualize
from deuxpots.pdf_tax_parser import parse_tax_pdf

BOX_MAPPING = load_box_mapping()

app = Flask("deuxpots")


@app.route('/individualize', methods=['POST'])
def individualize():
    params = json.load(request.files['params'])
    tax_pdf = request.files['tax_pdf'].read()
    parsed_sheeet = parse_tax_pdf(tax_pdf)
    user_ratios = {box['code']: box['ratio_0'] for box in params['boxes']}
    result = simulate_and_individualize(parsed_sheeet, user_ratios, BOX_MAPPING)
    return dict(
        boxes=list(map(serialize_box, result['boxes'])),
        individualized=asdict(result['individualized']) if result.get('individualized') else None
    )

def serialize_box(valbox):
    return dict(
        code=valbox.box.code,
        description=valbox.box.reference.description,
        ratio_0=valbox.ratio_0
    )


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8888, debug=True)
