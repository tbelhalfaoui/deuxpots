from collections import defaultdict
import json
import logging
import re
from warnings import warn
from typing import Dict, Iterator, List, Optional, Tuple
import fitz
from deuxpots.warning_utils import UserFacingWarning
from deuxpots.flatbox import FlatBox
from deuxpots.valued_box import ValuedBox

HOUSEHOLD_STATUS_FIELD = "pre_situation_famille"
HOUSEHOLD_STATUS_VALUES = {'0AM', '0AO', '0AD', '0AC', '0AV'}
HOUSEHOLD_STATUS_VALUES_TOGETHER = {'M', 'O'}  # marriage or civil union

MAX_BOX_HEIGHT = 10.25
BOX_WIDTH_BY_CATEGORY = {'A': 13, 'C': 40, 'D': 25}


class FamilyBoxExtractionWarning(UserFacingWarning):
    pass


class HouseholdStatusWarning(UserFacingWarning):
    pass


class DuplicateFamilyBox(Warning):
    pass


class FamilyBoxBadValue(Warning):
    pass


class MissingFamilyBox(Warning):
    pass


def load_category_coords(json_path) -> Dict[str, Tuple[float, float, float, float]]:
    rectangles = {}
    with open(json_path) as f:
        annotations = json.load(f)
        for shape in annotations['shapes']:
            assert shape["shape_type"] == "rectangle"
            rectangles[shape["label"]] = shape["points"][0] + shape["points"][1]
    return rectangles


def _family_box_codes(box_mapping, category_label=''):
    return [code for code in box_mapping.keys() if code.startswith('0' + category_label)]


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
            warn(f"{box_code}: {coords_list}", DuplicateFamilyBox)
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
            warn(box_code, MissingFamilyBox)
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
                warn(f"{box_code}: {box_text}", FamilyBoxBadValue)
                yield FlatBox(code=box_code, raw_value=None)


def _strip_and_check_household_status(flatboxes) -> Tuple[List[FlatBox], List[str]]:
    statuses = [box.code[-1] for box in flatboxes if box.code in HOUSEHOLD_STATUS_VALUES and box.raw_value]
    flatboxes_filtered = [box for box in flatboxes if box.code not in HOUSEHOLD_STATUS_VALUES]
    if len(statuses) != 1:
        warn(f"La case \"situation du foyer fiscal\" n'a pas été correctement détectée "
             f"({', '.join(statuses)}). "
             f"Merci de vous assurer que la déclaration d'impôt que vous avez utilisée est "
             f"bien une déclaration commune (marié·e·s ou pacsé·e·s).", HouseholdStatusWarning)
    elif len(statuses) == 1:
        status = statuses[0]
        if status not in HOUSEHOLD_STATUS_VALUES_TOGETHER:
            warn(f"Il semble que la déclaration que vous avez soumise ne concerne qu'une seule personne "
                 f"({status}) : elle est donc déjà individualisée... "
                 f"Dans ce cas, merci de recommencer avec une déclaration commune (marié·e·s ou pacsé·e·s).", HouseholdStatusWarning)
    return flatboxes_filtered


def _warn_if_empty_boxes(flatboxes) -> List[str]:
    empty_boxes = [box for box in flatboxes if box.raw_value is None]
    if empty_boxes:
        warn(f"Certaines cases concernant la situation du foyer fiscal et les personnes à charge "
             f"n'ont pas bien été détectées ({', '.join([box.code for box in empty_boxes])}). "
             f"Merci de les renseigner manuellement.", FamilyBoxExtractionWarning)


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


def parse_tax_pdf(pdf_content, category_coords, box_mapping) -> List[ValuedBox]:
    flatboxes = list(_parse_tax_pdf(pdf_content, category_coords, box_mapping))
    _warn_if_empty_boxes(flatboxes)
    flatboxes = _strip_and_check_household_status(flatboxes)
    valboxes = [ValuedBox.from_flat_box(box, box_mapping=box_mapping) for box in flatboxes]
    return valboxes
