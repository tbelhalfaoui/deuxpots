import re
import fitz

from deuxpots.tax_calculator import IncomeSheet


def _parse_tax_pdf(line):
    REGEX_BOX = re.compile(r'\s*([0-9][A-Z]{2})\s+([^:]+):\s([0-9]+)')
    match = REGEX_BOX.search(line)
    if match:
        box_code, _, box_value = match.groups()
        yield box_code, int(box_value)


def _read_pdf_lines(pdf_content):
    with fitz.open(stream=pdf_content) as doc:
        for page in doc:
            for line in page.get_text().split('\n'):
                yield line


def parse_tax_pdf(pdf_content):
    income_sheet = IncomeSheet()
    for line in _read_pdf_lines(pdf_content):
        for box_code, box_value in _parse_tax_pdf(line):
            income_sheet[box_code] = box_value
    return income_sheet
