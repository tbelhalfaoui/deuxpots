from collections import defaultdict
import json
import logging
import re
from warnings import warn
from typing import Dict, Iterator, List, Optional, Tuple
import fitz
from deuxpots.warning_error_utils import UserFacingError, UserFacingWarning
from deuxpots.flatbox import FlatBox
from deuxpots.valued_box import ValuedBox

HOUSEHOLD_STATUS_FIELD = "pre_situation_famille"
HOUSEHOLD_STATUS_VALUES = {'0AM', '0AO', '0AD', '0AC', '0AV'}
HOUSEHOLD_STATUS_VALUES_TOGETHER = {'M', 'O'}  # marriage or civil union

MAX_BOX_HEIGHT = 10.25
BOX_WIDTH_BY_CATEGORY = {'A': 13, 'C': 40, 'D': 25}


class DuplicateFamilyBox(Warning):
    pass


class FamilyBoxBadValue(Warning):
    pass


class MissingFamilyBox(Warning):
    pass


class FamilyBoxNotExtracted(UserFacingWarning):
    def __init__(self, box_codes):
        self.box_codes = box_codes
    
    def __str__(self):
        return (f"Certaines cases concernant la situation du foyer fiscal et les personnes à charge "
                f"n'ont pas bien été détectées ({', '.join(self.box_codes)}). "
                f"Merci de les renseigner manuellement.")


class BadHouseholdStatus(UserFacingWarning):
    def __init__(self, statuses):
        self.statuses = statuses

    def __str__(self):
        if len(self.statuses) == 1:
            return (f"Il semble que la déclaration que vous avez soumise ne concerne qu'une seule personne "
                    f"({self.statuses[0]}) : elle est donc déjà individualisée... "
                    f"Dans ce cas, merci de recommencer avec une déclaration commune (marié·e·s ou pacsé·e·s).")
        return (f"La case \"situation du foyer fiscal\" n'a pas été correctement détectée ({', '.join(self.statuses)}). "
               f"Merci de vérifier qu'il s'agit bien une déclaration commune (marié·e·s ou pacsé·e·s).")


class BadTaxPDF(UserFacingError):
    MESSAGES = {
        "not_a_pdf": "Le fichier que vous avez sélectionné n'est pas un PDF valide.",
        "avis_impot": ("Le fichier que vous avez sélectionné n'est pas le bon : vous devez "
                       "utiliser votre déclaration de revenus et non pas votre avis d'impôt."),
        "other_pdf": "Le fichier que vous avez sélectionné n'est pas une déclaration d'impôt."
    }

    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return self.MESSAGES[self.reason]


def load_category_coords(json_path) -> Dict[str, Tuple[float, float, float, float]]:
    rectangles = {}
    with open(json_path) as f:
        annotations = json.load(f)
        for shape in annotations['shapes']:
            assert shape["shape_type"] == "rectangle"
            rectangles[shape["label"]] = shape["points"][0] + shape["points"][1]
    return rectangles


def _family_box_codes(box_mapping, category_label=''):
    return [code for code in box_mapping.keys()
            if code.startswith('0' + category_label) and code != '0XX']


def _generate_family_box_coords(page, category_coords, box_mapping
                                ) -> Dict[str, List[Tuple[float, float, float, float]]]:
    """
    Automatically detect the box given its letter (e.g. V for 0AV box in category A
    or G for 0CG box in category C). Then, generate the corresponding coordinates 
    where each value can be found.

    For each box, return a list of possible coordinates (duplicated will be handled later on).
    """
    family_box_coords = defaultdict(list)
    for cat_label, cat_coords in category_coords.items():
        box_letters = {code[-1] for code in _family_box_codes(box_mapping, cat_label)}
        category_rect = fitz.Rect(*cat_coords)

        for item in page.get_text("words", clip=category_rect):
            box_letter = item[4].strip()
            if box_letter not in box_letters:
                continue
            x0, y0, x1, y1 = item[0:4]
            if y1 - y0 > MAX_BOX_HEIGHT:
                continue
            box_code = '0' + cat_label + box_letter
            width = BOX_WIDTH_BY_CATEGORY[cat_label]
            box_coords = (x1 + 2, (y0 + y1) / 2 - 2,
                          x1 + 2 + width, (y0 + y1) / 2)
            family_box_coords[box_code].append(box_coords)
    return family_box_coords


def _strip_duplicate_family_box_coords(family_box_coords
                                       : Dict[str, List[Tuple[float, float, float, float]]]
                                       ) -> Dict[str, Tuple[float, float, float, float]]:
    family_box_coords_dedup = {}
    for box_code, coords_list in family_box_coords.items():
        if len(coords_list) == 1:
            family_box_coords_dedup[box_code] = coords_list[0]
        else:
            # If duplicate, then unsure: remove from the list and let the user fill it .
            warn(DuplicateFamilyBox(box_code, coords_list))
    return family_box_coords_dedup


def _extract_family_boxes(fitz_doc, family_box_coords, box_mapping
                          ) -> Iterator[Optional[ValuedBox]]: 
    """
    Extract family boxes from PDF (2nd page of the tax sheet).
    Values are booleans (checkboxes) and small integers (e.g. number of children).
    If the extraction fails, return a box with `None` value, that will be filtered later on,
    but counted to issue a user warning.
    """
    for box_code in _family_box_codes(box_mapping):
        try:
            box_coords = family_box_coords[box_code]
        except KeyError:
            warn(MissingFamilyBox(box_code))
            # If the box has not been found, return an empty one, so that the user can fill it.
            yield FlatBox(code=box_code, raw_value=None)
            continue

        rect = fitz.Rect(*box_coords)
        box_text = fitz_doc[1].get_textbox(rect).strip()
        if not box_text:
            # The box if correctly detected but empty: skip it.
            continue
        elif box_text.lower() == "x":
            yield FlatBox(code=box_code, raw_value=1)
        else:
            try:
                yield FlatBox(code=box_code, raw_value=int(box_text))
            except Exception:
                # The box value cannot be parsed: return an empty box, so that the user can fill it.
                logging.exception(box_code)
                warn(FamilyBoxBadValue(box_code, box_text, box_coords))
                yield FlatBox(code=box_code, raw_value=None)


def _strip_and_check_household_status(flatboxes) -> Tuple[List[FlatBox], List[str]]:
    statuses = [box.code[-1] for box in flatboxes if box.code in HOUSEHOLD_STATUS_VALUES and box.raw_value]
    flatboxes_filtered = [box for box in flatboxes if box.code not in HOUSEHOLD_STATUS_VALUES]
    if len(statuses) != 1:
        warn(BadHouseholdStatus(statuses))
    elif len(statuses) == 1:
        status = statuses[0]
        if status not in HOUSEHOLD_STATUS_VALUES_TOGETHER:
            warn(BadHouseholdStatus(statuses))
    return flatboxes_filtered


def _warn_if_empty_boxes(flatboxes) -> List[str]:
    empty_boxes = [box for box in flatboxes if box.raw_value is None]
    if empty_boxes:
        warn(FamilyBoxNotExtracted([box.code for box in empty_boxes]))


def _parse_line(line: str) -> Iterator[FlatBox]:
    REGEX_BOX = re.compile(r'\s*([0-9][A-Z]{2})\s+(.+):\s([0-9]+)')
    match = REGEX_BOX.search(line)
    if match:
        box_code, box_description, box_value = match.groups()
        yield FlatBox(
            code=box_code,
            raw_value=int(box_value),
            description=box_description.strip()
        )


def _extract_income_fields(fitz_doc) -> Iterator[FlatBox]:
    """
    Extract income boxes from PDF text (starting on 3rd page of the tax sheet).
    Values are integers (money amounts).
    """
    for page_number in range(2, fitz_doc.page_count):
        page = fitz_doc[page_number]
        for line in page.get_text().split('\n'):
            yield from _parse_line(line)


def _parse_tax_pdf(pdf_content, category_coords, box_mapping) -> Iterator[FlatBox]:
    with fitz.open(stream=pdf_content) as fitz_doc:
        yield from _extract_income_fields(fitz_doc)
        family_box_coords = _generate_family_box_coords(fitz_doc[1], category_coords, box_mapping)
        family_box_coords = _strip_duplicate_family_box_coords(family_box_coords)
        yield from _extract_family_boxes(fitz_doc, family_box_coords, box_mapping)


def _tax_pdf_safety_check(pdf_content):
    try:
        with fitz.open(stream=pdf_content) as fitz_doc:
            text_page0 = re.sub('\s', '', fitz_doc[0].get_text()).lower()
    except fitz.FileDataError:
        raise BadTaxPDF("not_a_pdf")
    if "avisdesituationdéclarative" in text_page0 or "avis_ir_rg" in text_page0:
        raise BadTaxPDF("avis_impot")
    if not "10330" in text_page0 or not "2042" in text_page0:
        raise BadTaxPDF("other_pdf")


def parse_tax_pdf(pdf_content, category_coords, box_mapping) -> List[ValuedBox]:
    _tax_pdf_safety_check(pdf_content)
    flatboxes = list(_parse_tax_pdf(pdf_content, category_coords, box_mapping))
    _warn_if_empty_boxes(flatboxes)
    flatboxes = _strip_and_check_household_status(flatboxes)
    valboxes = [ValuedBox.from_flat_box(box, box_mapping=box_mapping) for box in flatboxes]
    return valboxes
