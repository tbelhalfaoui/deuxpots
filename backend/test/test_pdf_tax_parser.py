import warnings
import pytest
from unittest.mock import ANY
from deuxpots.box import Box
from deuxpots.flatbox import FlatBox
from deuxpots.pdf_tax_parser import (
    HOUSEHOLD_STATUS_VALUES, BadTaxPDF, DuplicateFamilyBox, FamilyBoxBadValue, FamilyBoxNotExtracted,
    BadHouseholdStatus, MissingFamilyBox,
    _parse_line, _parse_tax_pdf, _strip_and_check_household_status, _warn_if_empty_boxes, parse_tax_pdf,
)
from deuxpots.valued_box import UnknownBoxCodeWarning, ValuedBox
from deuxpots.warning_error_utils import UserFacingWarning


@pytest.mark.parametrize("text,flatbox", [
    ("8UY Micro-entrepreneur : versements libératoires de l'IR : 500",
     FlatBox(code="8UY", raw_value=500, description="Micro-entrepreneur : versements libératoires de l'IR")),
    ("5HQ BNC professionnels régime micro - Revenus imposables - Déclarant 1 : 8000",
     FlatBox(code="5HQ", raw_value=8000, description="BNC professionnels régime micro - Revenus imposables - Déclarant 1"))
])
def test__parse_line(text, flatbox):
    assert list(_parse_line(text)) == [flatbox]


@pytest.mark.parametrize("box", ["1AJ)", "PAM", "911"])
def test__parse_line_false_positive(box):
    """
    Paragraph "Informations connues de l'administration avant modifications éventuelles par le déclarant"
    """
    assert not list(_parse_line(f"{box} xxxx : 7348"))


@pytest.fixture
def expected_flatboxes():
    return [
        FlatBox(code='0AM', raw_value=1, description=ANY),
        FlatBox(code='8HV', raw_value=2000, description=ANY),
        FlatBox(code='8IV', raw_value=800, description=ANY),
        FlatBox(code='1AJ', raw_value=60000, description=ANY),
        FlatBox(code='1BJ', raw_value=20000, description=ANY),
        FlatBox(code='5HQ', raw_value=500, description=ANY),
        FlatBox(code='0AP', raw_value=1, description=ANY),
        FlatBox(code='0AS', raw_value=1, description=ANY),
        FlatBox(code='0CF', raw_value=2, description=ANY),
        FlatBox(code='0CG', raw_value=1, description=ANY),
        FlatBox(code='0CH', raw_value=2, description=ANY),
        FlatBox(code='0CI', raw_value=1, description=ANY),
        FlatBox(code='0CR', raw_value=2, description=ANY),
        FlatBox(code='0DJ', raw_value=1, description=ANY),
        FlatBox(code='0DN', raw_value=3, description=ANY),
    ]

def test__parse_tax_pdf(tax_sheet_pdf_path, expected_flatboxes, category_coords, box_mapping):
    with tax_sheet_pdf_path.open("rb") as f:
        pdf_content = f.read()
    flatboxes = list(_parse_tax_pdf(pdf_content, category_coords, box_mapping))
    assert sorted(flatboxes) == sorted(expected_flatboxes)


def test__warn_if_empty_boxes():
    with pytest.warns(FamilyBoxNotExtracted):
        _warn_if_empty_boxes([
            FlatBox(code='0AM', raw_value=None),
        ])


@pytest.mark.parametrize('household_status', ['0AM', '0AO'])
def test__strip_and_check_household_status_correct(household_status):
    flatboxes_in = [
        FlatBox(code=household_status, raw_value=1),
        FlatBox(code='8HV', raw_value=2000),
    ]
    flatboxes_expected = [
        FlatBox(code='8HV', raw_value=2000)
    ]
    with warnings.catch_warnings(category=UserFacingWarning):
        warnings.simplefilter("error")
        flatboxes_out = _strip_and_check_household_status(flatboxes_in)
    assert flatboxes_out == flatboxes_expected


def test__strip_and_check_household_status_duplicate():
    flatboxes_in = [
        FlatBox(code='0AM', raw_value=1),
        FlatBox(code='0AO', raw_value=1),
        FlatBox(code='8HV', raw_value=2000),
    ]
    flatboxes_expected = [
        FlatBox(code='8HV', raw_value=2000)
    ]
    with pytest.warns(BadHouseholdStatus):
        flatboxes_out =  _strip_and_check_household_status(flatboxes_in)
    assert flatboxes_out == flatboxes_expected


def test__strip_and_check_household_status_missing():
    flatboxes_in = [
        FlatBox(code='8HV', raw_value=2000),
    ]
    flatboxes_expected = [
        FlatBox(code='8HV', raw_value=2000)
    ]
    with pytest.warns(BadHouseholdStatus):
        flatboxes_out =  _strip_and_check_household_status(flatboxes_in)
    assert flatboxes_out == flatboxes_expected


@pytest.mark.parametrize('household_status', ['0AC', '0AD', '0AV'])
def test__strip_and_check_household_status_single(household_status):
    flatboxes_in = [
        FlatBox(code=household_status, raw_value=1),
        FlatBox(code='8HV', raw_value=2000),
    ]
    flatboxes_expected = [
        FlatBox(code='8HV', raw_value=2000)
    ]
    with pytest.warns(BadHouseholdStatus):
        flatboxes_out =  _strip_and_check_household_status(flatboxes_in)
    assert flatboxes_out == flatboxes_expected


def test_parse_tax_pdf(tax_sheet_pdf_path, expected_flatboxes, category_coords, box_mapping):
    with tax_sheet_pdf_path.open("rb") as f:
        pdf_content = f.read()        
    with warnings.catch_warnings(category=UserFacingWarning):
        warnings.simplefilter("error")
        valboxes = parse_tax_pdf(pdf_content, category_coords, box_mapping)
    assert len(valboxes) == len(expected_flatboxes) - 1  # removed household status
    assert all(isinstance(vb, ValuedBox) for vb in valboxes)


@pytest.mark.parametrize("warning,match", [
    (DuplicateFamilyBox, '0AS'),
    (MissingFamilyBox, '0AS'),
    (FamilyBoxBadValue, '0CF.*z'),
    (FamilyBoxNotExtracted, '0AS, 0CF'),
    (BadHouseholdStatus, 'M, D'),
    (UnknownBoxCodeWarning, '9ZZ'),
])
def test_parse_tax_pdf_with_problems(warning, match, tax_sheet_pdf_path_with_problems,
                                     category_coords, box_mapping):
    with tax_sheet_pdf_path_with_problems.open("rb") as f:
        pdf_content = f.read()
    with pytest.warns(warning, match=match) as w:
        valboxes = parse_tax_pdf(pdf_content, category_coords, box_mapping)
    assert len(w) == 6
    assert ValuedBox(box=Box(code="0AS", reference=ANY, kind=ANY), raw_value=None, attribution=ANY) in valboxes
    assert ValuedBox(box=Box(code="0CF", reference=ANY, kind=ANY), raw_value=None, attribution=ANY) in valboxes


def test_parse_tax_pdf_bad_file(tax_notice_not_sheet, empty_pdf, category_coords, box_mapping):
    with pytest.raises(BadTaxPDF, match="pas un PDF valide"):
        parse_tax_pdf(b"", category_coords, box_mapping)
    with pytest.raises(BadTaxPDF, match="pas le bon"):
        with open(tax_notice_not_sheet, "rb") as f:
            parse_tax_pdf(f.read(), category_coords, box_mapping)
    with pytest.raises(BadTaxPDF, match="pas une déclaration"):
            with open(empty_pdf, "rb") as f:
                parse_tax_pdf(f.read(), category_coords, box_mapping)
