from typing import List, Tuple
from dataclasses import dataclass
from deuxpots.tax_calculator import build_income_sheet, compute_tax

from deuxpots.valued_box import ValuedBox, build_valued_box


HOUSEHOLD_STATUSES = ['AM', 'AO', 'AD', 'AC', 'AV']


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


def _check_household_status(income_sheet, box_mapping):
    household_status_ = []
    for status in HOUSEHOLD_STATUSES:
        if income_sheet.get(status):
            household_status_.append(status)
    if len(household_status_) != 1:
        raise HouseholdStatusError(f"Un seul statut du foyer fiscal est possible, mais "
                                   f"{len(household_status_)} détecté(s) : {household_status_}")
    household_status = household_status_[0]
    if household_status not in {'AM', 'AO'}:
        raise HouseholdStatusError(f"La feuille d'impôt à individualiser doit être commune "
                                   f"(marié·e ou pacsé·e). Le statut détecté est : {box_mapping[household_status]}")


def simulate_and_individualize(parsed_sheeet, user_ratios, box_mapping):
    _check_household_status(parsed_sheeet, box_mapping)
    valboxes = [build_valued_box(code=box_code,
                                 raw_value=box_value,
                                 ratio_0=user_ratios.get(box_code),
                                 box_mapping=box_mapping)
                for box_code, box_value in parsed_sheeet.items()
                if box_code not in HOUSEHOLD_STATUSES]

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
