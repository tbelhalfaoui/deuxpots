import pytest
from deuxpots.pdf_tax_parser import _parse_line, parse_tax_pdf
from deuxpots.tax_calculator import IncomeSheet


@pytest.mark.parametrize("box", ["1BJ", "8UY"])
def test__parse_line(box):
    assert list(_parse_line(f"{box} xxxx : 7348")) == [(box, 7348)]


@pytest.mark.parametrize("box", ["911", "PAM"])
def test__parse_line_false_positive(box):
    assert not list(_parse_line(f"{box} xxxx : 7348"))


@pytest.mark.parametrize("box", ["1AJ)", "PAM"])
def test__parse_line_false_positive(box):
    """
    Paragraph "Informations connues de l'administration avant modifications éventuelles par le déclarant"
    """
    assert not list(_parse_line(f"{box} xxxx : 7348"))


def test_parse_tax_pdf(tax_sheet_pdf_path, family_box_coords):
    with tax_sheet_pdf_path.open("rb") as f:
        pdf_content = f.read()
    parsed_sheet = parse_tax_pdf(pdf_content, family_box_coords)
    assert parsed_sheet == IncomeSheet({
        'pre_situation_famille': 'M',
        '8HV': 2000,
        '8IV': 800,
        '1AJ': 60000,
        '1BJ': 20000,
        '5HQ': 500,
        'AP': 1,
        'AS': 1,
        'DJ': 1,
        'DN': 1,
        'CF': 2,
        'CG': 1,
        'CH': 1,
        'CI': 1, 
        'CR': 2,
})
