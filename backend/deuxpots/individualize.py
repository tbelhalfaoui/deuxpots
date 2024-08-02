from typing import Tuple
from dataclasses import dataclass
from deuxpots.tax_calculator import build_income_sheet, compute_tax, handle_children_split


@dataclass
class IndividualResult:
    tax_if_single: int = 0
    total_tax: int = 0
    tax_gain: int = 0
    already_paid: int = 0
    remains_to_pay: int = 0
    remains_to_pay_to_tax_office: int = 0
    remains_to_pay_to_partner: int = 0


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
        )._individualize().round()

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

        for partners in (self.partners_proportional_split, self.partners_equal_split):
            if partners[0].remains_to_pay * partners[1].remains_to_pay > 0:
                for partner in partners:
                    partner.remains_to_pay_to_tax_office = partner.remains_to_pay
            else:
                for this_partner, other_partner in zip(partners, partners[::-1]):
                    if this_partner.remains_to_pay > 0:
                        this_partner.remains_to_pay_to_tax_office = this_partner.remains_to_pay \
                                                                    + other_partner.remains_to_pay
                        this_partner.remains_to_pay_to_partner = -other_partner.remains_to_pay
                        other_partner.remains_to_pay_to_partner = other_partner.remains_to_pay
        return self

    def round(self):
        self.total_tax_single = round(self.total_tax_single)
        self.total_tax_together = round(self.total_tax_together)
        self.total_tax_gain = round(self.total_tax_gain)
        for partners in (self.partners_proportional_split, self.partners_equal_split):
            for partner in partners:
                partner.tax_if_single = round(partner.tax_if_single)
                partner.total_tax = round(partner.total_tax)
                partner.tax_gain = round(partner.tax_gain)
                partner.already_paid = round(partner.already_paid)
                partner.remains_to_pay = round(partner.remains_to_pay)
                partner.remains_to_pay_to_tax_office = round(partner.remains_to_pay_to_tax_office)
                partner.remains_to_pay_to_partner = round(partner.remains_to_pay_to_partner)
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
