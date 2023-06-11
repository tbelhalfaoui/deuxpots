from typing import Tuple
from dataclasses import dataclass
from deuxpots.tax_calculator import build_income_sheet, compute_tax, handle_children_split


@dataclass
class IndividualResult:
    tax_if_single: int = None
    total_tax: int = None
    tax_gain: int = None
    already_paid: int = None
    remains_to_pay: int = None


@dataclass
class IndividualizedResults:
    total_tax_single: int = None
    total_tax_together: int = None
    total_tax_gain: int = None
    partners_proportional_split: Tuple[IndividualResult, IndividualResult] = None
    partners_equal_split: Tuple[IndividualResult, IndividualResult] = None

    @staticmethod
    def from_simulations(simu_partner_0, simu_partner_1, simu_together):
        def _default_partner_results():
            return (
                IndividualResult(
                    tax_if_single=simu_partner_0.total_tax,
                    already_paid=simu_partner_0.already_paid
                ),
                IndividualResult(
                    tax_if_single=simu_partner_1.total_tax,
                    already_paid=simu_partner_1.already_paid
                )
            )
        return IndividualizedResults(
            total_tax_single=simu_partner_0.total_tax + simu_partner_1.total_tax,
            total_tax_together=simu_together.total_tax,
            partners_proportional_split=_default_partner_results(),
            partners_equal_split=_default_partner_results(),
        )._individualize()

    def _individualize(self):
        self.total_tax_gain = self.total_tax_single - self.total_tax_together
        for pix in [0, 1]:
            partner_proportional = self.partners_proportional_split[pix]
            partner_even = self.partners_equal_split[pix]
            if self.total_tax_single == 0:
                partner_proportion = 0
            else:
                partner_proportion = partner_proportional.tax_if_single / self.total_tax_single
            partner_proportional.tax_gain = self.total_tax_gain * partner_proportion
            partner_even.tax_gain = self.total_tax_gain / 2
            for partner in (partner_proportional, partner_even):
                partner.total_tax = partner.tax_if_single - partner.tax_gain
                partner.remains_to_pay = partner.total_tax - partner.already_paid
        return self


def simulate_and_individualize(valboxes):
    simu_results = {}
    for pix in [0, 1, None]:
        income_sheet = build_income_sheet(valboxes, individualize=pix)
        income_sheet = handle_children_split(income_sheet)
        simu_results[pix] = compute_tax(income_sheet)
    return IndividualizedResults.from_simulations(
        simu_partner_0=simu_results[0],
        simu_partner_1=simu_results[1],
        simu_together=simu_results[None]
    )
