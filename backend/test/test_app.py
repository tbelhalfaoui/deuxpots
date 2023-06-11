import pytest
from deuxpots.app import app
from deuxpots.warning_error_utils import UserFacingWarning


app.config['TESTING'] = True


def test_parse(tax_sheet_pdf_path):
    with app.test_client() as test_client:
        res = test_client.post('/parse', data=dict(
            tax_pdf=tax_sheet_pdf_path.open('rb')
        )) # multipart/form-data request
        assert res.status_code == 200
        for flatbox in res.json['boxes']:
            assert flatbox['code']
            assert flatbox['description']
            assert flatbox['raw_value']
            assert 'attribution' in flatbox  # can be None
            assert not res.json['warnings']


def test_parse_with_warnings(tax_sheet_pdf_path_with_problems):
    with app.test_client() as test_client:
        with pytest.warns(UserFacingWarning):
            res = test_client.post('/parse', data=dict(
                tax_pdf=tax_sheet_pdf_path_with_problems.open('rb')
            ))
        assert res.status_code == 200
        for flatbox in res.json['boxes']:
            assert flatbox['code']
            assert flatbox['description']
            assert 'attribution' in flatbox  # can be None
            warnings = res.json['warnings']
            assert len(warnings) == 3
            assert any('0AS, 0CF' in w for w in warnings)
            assert any('M, D' in w for w in warnings)
            assert any('9ZZ' in w for w in warnings)

def test_parse_demo():
    with app.test_client() as test_client:
        res = test_client.post('/parse?demo=true') 
        assert res.status_code == 200
        for flatbox in res.json['boxes']:
            assert flatbox['code']
            assert flatbox['description']
            assert flatbox['raw_value']
            assert 'attribution' in flatbox  # can be None


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
        assert 'partners_proportional_split' in res.json['individualized']
        assert 'partners_equal_split' in res.json['individualized']


def test_full_scenario(tax_sheet_pdf_path):
    with app.test_client() as test_client:
        # 1. Parse
        res = test_client.post('/parse', data=dict(
            tax_pdf=tax_sheet_pdf_path.open('rb')
        )) # multipart/form-data request
        assert res.status_code == 200

        # 2. Simulate user actions
        flatboxes = res.json['boxes']
        for flatbox in flatboxes:
            flatbox['attribution'] = 0

        # 3. Individualize
        res = test_client.post('/individualize',
                               json=dict(boxes=flatboxes))
        assert res.status_code == 200
        assert res.json['individualized']
        assert 'partners_proportional_split' in res.json['individualized']
        assert 'partners_equal_split' in res.json['individualized']