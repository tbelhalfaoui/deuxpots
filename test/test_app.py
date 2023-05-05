import json
from deuxpots.app import app


app.config['TESTING'] = True


def test_app_individualize(tax_sheet_pdf_path):
    # 1. First call with a tax sheet olnly
    with app.test_client() as test_client:
        res = test_client.post('/individualize', data={
            "boxes": "{}",
            "tax_pdf": tax_sheet_pdf_path.open('rb'),
        })
        assert res.status_code == 200
        boxes = res.json['boxes']
    
    # 2. Simulate a user setting ratios
    for box in boxes:
        if box['ratio_0'] is None:
            box['ratio_0'] = 1
    
    # 3. Second call with user ratios
    with app.test_client() as test_client:
        res = test_client.post('/individualize', data={
            "boxes": json.dumps(boxes),
            "tax_pdf": tax_sheet_pdf_path.open('rb'),
        })
        assert res.status_code == 200
        assert res.json['boxes']
        assert 'partners' in res.json['individualized']
