import json
import re
import fitz

from deuxpots.tax_calculator import IncomeSheet


def _read_pdf_lines(pdf_content):
    with fitz.open(stream=pdf_content) as doc:
        for page in doc:
            for line in page.get_text().split('\n'):
                yield line


def _parse_line(line):
    REGEX_BOX = re.compile(r'\s*([0-9][A-Z]{2})\s+([^:]+):\s([0-9]+)')
    match = REGEX_BOX.search(line)
    if match:
        box_code, _, box_value = match.groups()
        yield box_code, int(box_value)


def _load_family_box_coords(json_path):
    rectangles = {}
    with open(json_path) as f:
        annotations = json.load(f)
        for shape in annotations['shapes']:
            assert shape["shape_type"] == "rectangle"
            rectangles[shape["label"]] = shape["points"]
    return rectangles


def _extract_family_boxes_text(pdf_content, family_box_coords):
    with fitz.open(stream=pdf_content) as doc:
        family_page = doc[1]
        for box_code, ((x0, y0), (x1, y1)) in family_box_coords.items():
            rect = fitz.Rect(x0, y0, x1, y1)
            box_text = family_page.get_textbox(rect).strip()
            if box_text.lower() == "x":
                box_text = 1
            if box_text:
                yield box_code, box_text


def parse_tax_pdf(pdf_content, family_box_coords):
    income_sheet = IncomeSheet()
    for line in _read_pdf_lines(pdf_content):
        for box_code, box_value in _parse_line(line):
            income_sheet[box_code] = box_value
    for box_code, box_value in _extract_family_boxes_text(pdf_content, family_box_coords):
        income_sheet[box_code] = box_value
    return income_sheet
