from typing import Tuple
from dataclasses import dataclass
from deuxpots.tax_calculator import build_income_sheet, compute_tax, handle_children_split


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
        if res.total_tax_single == 0:
            partner.proportion == None
            partner.total_tax = 0
        else:
            partner.proportion = partner.tax_if_single / res.total_tax_single
            partner.total_tax = partner.proportion * res.total_tax_together
        partner.remains_to_pay = partner.total_tax - partner.already_paid
    res.tax_gain = res.total_tax_single - res.total_tax_together
    return res


def simulate_and_individualize(valboxes):
    simu_results = {}
    for pix in [0, 1, None]:
        income_sheet = build_income_sheet(valboxes, individualize=pix)
        income_sheet = handle_children_split(income_sheet)
        simu_results[pix] = compute_tax(income_sheet)
    return _individualize(simu_partner_0=simu_results[0],
                          simu_partner_1=simu_results[1],
                          simu_together=simu_results[None])
