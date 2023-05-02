import json
from flask import Flask
from flask import Flask, request

from deuxpots.box import build_box_mapping
from deuxpots.pdf_tax_parser import parse_tax_pdf
from deuxpots.tax_calculator import compute_tax
from deuxpots.valued_box import build_valued_box


CERFA_VARIABLES_PATH = "cerfa_variables.json"
with open(CERFA_VARIABLES_PATH) as f:
    cerfa_variables = json.load(f)

BOX_MAPPING = build_box_mapping(cerfa_variables)

app = Flask("deuxpots")


@app.route('/individualize', methods=['POST'])
def individualize():
    params = json.load(request.files['params'])
    tax_pdf = request.files['tax_pdf'].read()
    box_data = parse_tax_pdf(tax_pdf)
    user_ratios = {box['code']: box['ratio_0'] for box in params['boxes']}
    valboxes = [build_valued_box(code=box_code,
                                 raw_value=box_value,
                                 ratio_0=user_ratios.get(box_code),
                                 box_mapping=BOX_MAPPING)
                for box_code, box_value in box_data.items()]

    # if all(valbox.ratio_0 is not None for valbox in valboxes):
    #     for valbox in valboxes:
    #         tax_result_0 = compute_tax({valbox.box.reference.code: valbox.individualized_value(0) for valbox in valboxes})
    #         tax_result_1 = compute_tax({valbox.box.reference.code: valbox.individualized_value(1) for valbox in valboxes})
    #         tax_result_01 = compute_tax({valbox.box.code: valbox.individualized_value(1) for valbox in valboxes})
    #         rate_0 = tax_result_0.total_tax / (tax_result_0.total_tax + tax_result_1.total_tax)
    #         rate_1 = tax_result_1.total_tax / (tax_result_0.total_tax + tax_result_1.total_tax)
    #         rate_0 * results[-1]['Impôt total'] - tax_result_0.already_paid
    #         rate_1 * results[-1]['Impôt total'] - tax_result_1.already_paid
    #         tax_result_0.total_tax / (tax_result_0.total_tax + tax_result_1.total_tax)

    return dict(
        boxes=[serialize_box(valbox) for valbox in valboxes],
        individualized={}
    )


def serialize_box(valbox):
    return dict(
        code=valbox.box.code,
        description=valbox.box.reference.description,
        ratio_0=valbox.ratio_0
    )


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8888, debug=True)
