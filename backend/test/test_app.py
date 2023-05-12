import json
from deuxpots.app import app


app.config['TESTING'] = True


def test_parse(tax_sheet_pdf_path):
    with app.test_client() as test_client:
        res = test_client.post('/parse', data=dict(
            tax_pdf=tax_sheet_pdf_path.open('rb')
        )) # multipart/form-data request
        assert res.status_code == 200
        for valbox in res.json['boxes']:
            assert valbox['code']
            assert valbox['description']
            assert valbox['raw_value']
            assert 'attribution' in valbox  # can be None


def test_individualize():
    user_boxes = [
        {'code': '1AJ', 'raw_value': 40000, 'attribution': .2},
        {'code': '1BJ', 'raw_value': 20000, 'attribution': .6},
    ]
    with app.test_client() as test_client:
        res = test_client.post('/individualize',
                               json=dict(boxes=user_boxes))
        assert res.status_code == 200
        assert res.json['individualized']
        assert 'partners' in res.json['individualized']