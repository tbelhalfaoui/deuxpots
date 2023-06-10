from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

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
    total_tax: int                      # Impôt total (net)
    remains_to_pay: int                 # Reste à payer
    household_size: float               # Nombre de parts
    taxable_income: int                 # Revenu net imposable
    already_paid: Optional[int] = None  # Montant déjà payé


class SimulatorError(UserFacingError):
    pass


def _simulator_api(income_sheet):
    resp = rq.post(SIMULATOR_URL, data=income_sheet)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, features="html.parser")
    inputs = soup.select('input[type=hidden]')
    error_p = soup.select_one('p.margin-left-30px')
    return {
        "error": error_p.text if error_p else None,
        **{input['name']: input['value'] for input in inputs}
    }


def _format_simulator_results(results):
    try:
        res = SimulatorResult(
            total_tax=int(results.get("IINETIR", 0)),
            remains_to_pay=int(results['IINET']) - int(results['IREST']),
            household_size=float(results['NBPT']),
            taxable_income=int(results['RNICOL']),
        )
    except KeyError:
        raise SimulatorError(results["error"])
    res.already_paid=res.total_tax - res.remains_to_pay,
    return res

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
