import json
from deuxpots.app import app, toto


app.config['TESTING'] = True


def test_parse(tax_sheet_pdf_path):
    with app.test_client() as test_client:
        res = test_client.post('/parse', data=dict(
            tax_pdf=tax_sheet_pdf_path.open('rb')
        )) # multipart/form-data request
        assert res.status_code == 200
        for valbox in res.json['boxes']:
            assert valbox['box']['code']
            assert valbox['box']['reference']['description']
            assert valbox['raw_value']
            assert 'ratio' in valbox  # can be None


def test_individualize():
    user_boxes = [
        {'code': '1AJ', 'raw_value': 40000, 'ratio': .2},
        {'code': '1BJ', 'raw_value': 20000, 'ratio': .6},
    ]
    with app.test_client() as test_client:
        res = test_client.post('/individualize',
                               data=dict(boxes=json.dumps(user_boxes)))
        assert res.status_code == 200
        assert res.json['individualized']
        assert 'partners' in res.json['individualized']
