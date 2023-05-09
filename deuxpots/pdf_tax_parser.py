import json
import re
import fitz
from deuxpots.flatbox import FlatBox, flatten

from deuxpots.tax_calculator import IncomeSheet
from deuxpots.valued_box import ValuedBox

HOUSEHOLD_STATUS_FIELD = "pre_situation_famille"
HOUSEHOLD_STATUS_VALUES = ['M', 'O', 'D', 'C', 'V']
HOUSEHOLD_STATUS_VALUES_TOGETHER = {'M', 'O'}  # marriage or civil union


class TaxSheetParsingError(BaseException):
    pass


class HouseholdStatusError(BaseException):
    pass


def load_family_box_coords(json_path):
    rectangles = {}
    with open(json_path) as f:
        annotations = json.load(f)
        for shape in annotations['shapes']:
            assert shape["shape_type"] == "rectangle"
            rectangles[shape["label"]] = shape["points"]
    return rectangles


def _extract_family_boxes_text(fitz_doc, family_box_coords):
    """
    Extract family boxes from PDF (2nd page of the tax sheet).
    Values are booleans (checkboxes) and small integers (e.g. number of children).
    """
    family_page = fitz_doc[1]
    for box_code, ((x0, y0), (x1, y1)) in family_box_coords.items():
        rect = fitz.Rect(x0, y0, x1, y1)
        box_text = family_page.get_textbox(rect).strip()
        if not box_text:
            continue
        if box_text.lower() == "x":
            yield box_code, 1
        else:
            yield box_code, int(box_text)


def _agregate_household_status(income_sheet):
    status_boxes = []
    for status in HOUSEHOLD_STATUS_VALUES:
        if income_sheet.get(status):
            status_boxes.append(status)
            del income_sheet[status]
    if len(status_boxes) != 1:
        raise TaxSheetParsingError(f"La déclaration d'impôts doit comporter exactement une case cochée "
                                   f"pour le statut du foyer fiscal, mais {len(status_boxes)} cases "
                                   f"a/ont été détectée(s) : {status_boxes}")
    income_sheet[HOUSEHOLD_STATUS_FIELD] = status_boxes[0]


def _parse_line(line):
    REGEX_BOX = re.compile(r'\s*([0-9][A-Z]{2})\s+([^:]+):\s([0-9]+)')
    match = REGEX_BOX.search(line)
    if match:
        box_code, _, box_value = match.groups()
        yield box_code, int(box_value)


def _extract_income_fields(fitz_doc):
    """
    Extract income boxes from PDF text (starting on 3rd page of the tax sheet).
    Values are integers (money amounts).
    """
    for page_number in range(2, fitz_doc.page_count):
        page = fitz_doc[page_number]
        for line in page.get_text().split('\n'):
            yield from _parse_line(line)


def _check_and_strip_household_status(income_sheet, box_mapping):
    status = income_sheet.get(HOUSEHOLD_STATUS_FIELD)
    if status not in HOUSEHOLD_STATUS_VALUES_TOGETHER:
        raise HouseholdStatusError(f"La feuille d'impôt à individualiser doit être commune (marié·e ou pacsé·e). "
                                   f"Le statut détecté est : {box_mapping.get(status, 'aucun')}.")
    del income_sheet[HOUSEHOLD_STATUS_FIELD]


def _parse_tax_pdf(pdf_content, family_box_coords):
    income_sheet = IncomeSheet()
    with fitz.open(stream=pdf_content) as fitz_doc:
        for box_code, box_value in _extract_income_fields(fitz_doc):
            income_sheet[box_code] = box_value
        for box_code, box_value in _extract_family_boxes_text(fitz_doc, family_box_coords):
            income_sheet[box_code] = box_value
    _agregate_household_status(income_sheet)
    return income_sheet


def parse_tax_pdf(pdf_content, family_box_coords, box_mapping):
    parsed_sheet = _parse_tax_pdf(pdf_content, family_box_coords)
    _check_and_strip_household_status(parsed_sheet, box_mapping)
    return [ValuedBox.from_flat_box(FlatBox(code=box_code, raw_value=box_value),
                                        box_mapping=box_mapping)
            for box_code, box_value in parsed_sheet.items()]
