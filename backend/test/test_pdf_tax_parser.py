import pytest
from deuxpots.pdf_tax_parser import HouseholdStatusError, _check_and_strip_household_status, _parse_line, _parse_tax_pdf, parse_tax_pdf
from deuxpots.tax_calculator import IncomeSheet
from deuxpots.valued_box import ValuedBox


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


@pytest.fixture
def expected_parsed_raw_values():
    return {
            'pre_situation_famille': 'M',
            '8HV': 2000,
            '8IV': 800,
            '1AJ': 60000,
            '1BJ': 20000,
            '5HQ': 500,
            '0AP': 1,
            '0AS': 1,
            '0DJ': 1,
            '0DN': 3,
            '0CF': 2,
            '0CG': 1,
            '0CH': 2,
            '0CI': 1, 
            '0CR': 2,
    }


@pytest.fixture
def expected_parsed_attributions():
    return {
            'pre_situation_famille': 'M',
            '8HV': 1,
            '8IV': 0,
            '1AJ': 0,
            '1BJ': 1,
            '5HQ': 0,
            '0AP': 0,
            '0AS': None,
            '0DJ': None,
            '0DN': None,
            '0CF': None,
            '0CG': None,
            '0CH': None,
            '0CI': None, 
            '0CR': None,
    }


def test__parse_tax_pdf(tax_sheet_pdf_path, expected_parsed_raw_values, family_box_coords):
    with tax_sheet_pdf_path.open("rb") as f:
        pdf_content = f.read()
    parsed_sheet = _parse_tax_pdf(pdf_content, family_box_coords)
    assert parsed_sheet == IncomeSheet(expected_parsed_raw_values)


def test_parse_tax_pdf(tax_sheet_pdf_path, expected_parsed_raw_values, expected_parsed_attributions,
                       family_box_coords, box_mapping):
    with tax_sheet_pdf_path.open("rb") as f:
        pdf_content = f.read()
    valboxes = parse_tax_pdf(pdf_content, family_box_coords, box_mapping)
    for valbox in valboxes:
        valbox.raw_value == expected_parsed_raw_values[valbox.box.code]
        valbox.attribution == expected_parsed_attributions[valbox.box.code]


@pytest.mark.parametrize('status', ['O', 'M'])
def test__check_and_strip_household_status(status, box_mapping):
    income_sheet = {'pre_situation_famille': status}
    _check_and_strip_household_status(income_sheet, box_mapping) 
    assert income_sheet == {}


@pytest.mark.parametrize('status', ['AD', 'AC', 'AV', 'AM', 'AO', None])
def test__check_and_strip_household_status_bad_status(status, box_mapping):
    with pytest.raises(HouseholdStatusError):
        _check_and_strip_household_status({'pre_situation_famille': status}, box_mapping)
