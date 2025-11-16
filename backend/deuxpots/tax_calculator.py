from collections import defaultdict
from dataclasses import dataclass
import logging

from bs4 import BeautifulSoup
import requests as rq

from deuxpots import SIMULATOR_URL
from deuxpots.warning_error_utils import UserFacingError


class IncomeSheet(dict):
    """
    An income sheet is a dictionary with keys being the box codes
    and values being the value in the box.
    It is used as input data for the tax simulator.

    """
    pass


@dataclass
class SimulatorResult:
    total_tax: int               # Impôt total (net)
    already_paid: int            # Montant déjà payé
    remains_to_pay: int          # Reste à payer


class SimulatorError(UserFacingError):
    pass


def _simulator_api(income_sheet):
    resp = rq.post(SIMULATOR_URL, data=income_sheet)
    try:
        resp.raise_for_status()
    except rq.HTTPError:
        logging.error(f"Simulator API error for income sheet {income_sheet}")
        raise
    soup = BeautifulSoup(resp.text, features="html.parser")
    inputs = soup.select('input[type=hidden]')
    error_p = soup.select_one('p.margin-left-30px')
    return {
        "error": error_p.text if error_p else None,
        **{input['name']: input['value'] for input in inputs}
    }


def _format_simulator_results(results):
    try:
        INETIR = int(results.get("IINETIR", 0))
        IINET = int(results['IINET'])
        IREST = int(results['IREST'])
    except KeyError:
        raise SimulatorError(results["error"])
    remains_to_pay = IINET - IREST
    return SimulatorResult(
        total_tax=INETIR,
        already_paid=INETIR - remains_to_pay,
        remains_to_pay=remains_to_pay,
    )

def compute_tax(income_sheet: IncomeSheet) -> SimulatorResult:
    results = _simulator_api(income_sheet)
    return _format_simulator_results(results)


def build_income_sheet(valboxes, individualize=None):
    valboxes = [valbox for valbox in valboxes if valbox.raw_value]
    assert all(valbox.attribution is not None for valbox in valboxes)
    if individualize is None:
        sheet = IncomeSheet({
            '0DA': '1950',
            '0DB': '1950',
            'pre_situation_famille': 'O',
            'pre_situation_residence': 'M',
            **{valbox.box.code: valbox.raw_value for valbox in valboxes}
        })
    else:
        sheet = defaultdict(int)
        for valbox in valboxes:
            sheet[valbox.box.reference.code] += valbox.individualized_value(individualize)
    return {
        '0DA': '1950',
        'pre_situation_famille': 'C',
        'pre_situation_residence': 'M',
        **sheet
    }

def handle_children_split(income_sheet: IncomeSheet) -> IncomeSheet:
    # 1. Use a trick for "half-children": "convert" them artificially to alternating custody children
    # (0.5 child = 1 alternating custody child).

    NUM_CHILDREN_BOXES = [
        ('0CF', '0CH'),  # Number of children -> number of alternating custody children
                         # (Must be filled out if any of the below is filled out)
        ('0CG', '0CI'),  # Same but with disabled children
        ('7EA', '7EB'),  # Number of children in "college"
        ('7EC', '7ED'),  # Same for "lycée"
        ('7EF', '7EG'),  # Same for "enseignement supérieur"
    ]
    made_conversion = False
    for box_from, box_to in NUM_CHILDREN_BOXES:
        value = income_sheet.get(box_from)
        if not value:
            continue
        if int(value * 10) % 5:
            # If not 0.5 increment
            raise ValueError(f"Bad value {value} for box {box_from}.")
        if int(value * 10) % 10:
            # If not an integer (i.e. ends with ".5")
            income_sheet[box_from] = round(income_sheet[box_from] - .5)
            income_sheet[box_to] = income_sheet.get(box_to, 0) + 1
            if box_from == '0CF':
                made_conversion = True

    # 2. For boxes that are specific for the index of the child (1st, 2nd, etc.), transfer
    # everything to the box of the 1st child (since it does not make a difference).
    CHILDREN_CARE_BOXES = [
        ('7GA', '7GE'),  # Child care cost for 1st child
        ('7GB', '7GF'),  # Child care cost for 2nd child
        ('7GC', '7GG'),  # Child care cost for 3rd child
    ]
    for boxes in zip(*CHILDREN_CARE_BOXES):
        income_sheet[boxes[0]] = sum([income_sheet.get(box, 0) for box in boxes])
        for box in boxes[1:]:
            income_sheet[box] = 0

    # 3. For boxes that are specific to the type of custody (standard or alternating), if a
    # "half-child" has been converted to alternating custody, then also convert all amounts to
    # their alternating custody equivalent.

    if made_conversion:
        for box_from, box_to in CHILDREN_CARE_BOXES:
            income_sheet[box_to] = income_sheet.get(box_to, 0) + income_sheet.get(box_from, 0)
            income_sheet[box_from] = 0

    return income_sheet
