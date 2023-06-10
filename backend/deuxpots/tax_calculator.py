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

def handle_half_children(income_sheet: IncomeSheet) -> IncomeSheet:
    """
    Trick to handle non-integer number of children (only works with 0.5 increments).
    Treat them artificially as if in alternating custody.
    """
    CHILDREN_BOX_MAP = {
        '0CF': '0CH',  # Number of children -> number of alternating custody children
        '0CG': '0CI',  # Same but with disabled children
    }
    for box_from, box_to in CHILDREN_BOX_MAP.items():
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
    return income_sheet
