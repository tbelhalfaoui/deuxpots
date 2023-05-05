from typing import Tuple
from dataclasses import dataclass
from deuxpots.pdf_tax_parser import HOUSEHOLD_STATUS_FIELD, HOUSEHOLD_STATUS_VALUES_TOGETHER
from deuxpots.tax_calculator import build_income_sheet, compute_tax

from deuxpots.valued_box import build_valued_box


@dataclass
class IndividualResult:
    tax_if_single: int = None
    proportion: int = None
    total_tax: int = None
    already_paid: int = None
    remains_to_pay: int = None


@dataclass
class IndividualizedResults:
    total_tax_single: int = None
    total_tax_together: int = None
    tax_gain: int = None
    partners: Tuple[IndividualResult, IndividualResult] = None


def _individualize(simu_partner_0, simu_partner_1, simu_together):
    res = IndividualizedResults(
        total_tax_single=simu_partner_0.total_tax + simu_partner_1.total_tax,
        total_tax_together=simu_together.total_tax,
        partners=(
            IndividualResult(
                tax_if_single=simu_partner_0.total_tax,
                already_paid=simu_partner_0.already_paid
            ),
            IndividualResult(
                tax_if_single=simu_partner_1.total_tax,
                already_paid=simu_partner_1.already_paid
            )
        )
    )
    for pix in [0, 1]:
        partner = res.partners[pix]
        partner.proportion = partner.tax_if_single / res.total_tax_single
        partner.total_tax = partner.proportion * res.total_tax_together
        partner.remains_to_pay = partner.total_tax - partner.already_paid
    res.tax_gain = res.total_tax_single - res.total_tax_together
    return res


class HouseholdStatusError(BaseException):
    pass


def _check_and_strip_household_status(income_sheet, box_mapping):
    status = income_sheet.get(HOUSEHOLD_STATUS_FIELD, 'aucun')
    if status not in HOUSEHOLD_STATUS_VALUES_TOGETHER:
        raise HouseholdStatusError(f"La feuille d'impôt à individualiser doit être commune "
                                   f"(marié·e ou pacsé·e). Le statut détecté est : {status}.")
    del income_sheet[HOUSEHOLD_STATUS_FIELD]


def simulate_and_individualize(parsed_sheeet, user_ratios, box_mapping):
    _check_and_strip_household_status(parsed_sheeet, box_mapping)
    valboxes = [build_valued_box(code=box_code,
                                 raw_value=box_value,
                                 ratio_0=user_ratios.get(box_code),
                                 box_mapping=box_mapping)
                for box_code, box_value in parsed_sheeet.items()]

    simu_results = {}
    for pix in [0, 1, None]:
        income_sheet = build_income_sheet(valboxes, individualize=pix)
        if income_sheet is None:
            break
        simu_results[pix] = compute_tax(income_sheet)
    if len(simu_results) != 3:
        return dict(boxes=valboxes)
    
    results = _individualize(simu_partner_0=simu_results[0],
                            simu_partner_1=simu_results[1],
                            simu_together=simu_results[None])
    return dict(
        boxes=valboxes,
        individualized=results
    )
