import pytest
from deuxpots.individualize import (
    IndividualResult, IndividualizedResults,
    _individualize, simulate_and_individualize
)
from deuxpots.pdf_tax_parser import HouseholdStatusError
from deuxpots.tax_calculator import SimulatorResult


def test__individualize():
    results = _individualize(
        simu_partner_0=SimulatorResult(total_tax=6000, already_paid=1000, remains_to_pay=5000),
        simu_partner_1=SimulatorResult(total_tax=4000, already_paid=3900, remains_to_pay=100),
        simu_together=SimulatorResult(total_tax=8000, already_paid=None, remains_to_pay=None)  # None because unused here
    )
    assert results == IndividualizedResults(
        total_tax_single=10000,
        total_tax_together=8000,
        tax_gain=2000,
        partners=(
            IndividualResult(
                tax_if_single=6000,
                proportion=.6,
                total_tax=4800,  # .6 * 12000
                already_paid=1000,
                remains_to_pay=3800,  # 4800 - 1000
            ),
            IndividualResult(
                tax_if_single=4000,
                proportion=.4,
                total_tax=3200,  # .4 * 8000
                already_paid=3900,
                remains_to_pay=-700,  # 3200 - 3900
            )
        )
    )


def test_simulate_and_individualize(box_mapping):
    user_boxes = [
        {'code': '1AJ', 'raw_value': 40000, 'ratio_0': 1},
        {'code': '1BJ', 'raw_value': 20000, 'ratio_0': 0},
        {'code': '2DC', 'raw_value': 350, 'ratio_0': 0},
        {'code': '8HV', 'raw_value': 700, 'ratio_0': .9},
        {'code': '8IV', 'raw_value': 7000, 'ratio_0': .1},
        {'code': '8HW', 'raw_value': 600, 'ratio_0': 1},
    ]
    result = simulate_and_individualize(user_boxes, box_mapping)
    assert result.partners[0].remains_to_pay > 1000
    assert result.partners[1].remains_to_pay < 4000


def test_simulate_and_individualize_missing_ratio(box_mapping):
    user_boxes = [
        {'code': '2DC', 'raw_value': 3, 'ratio_0': None},
    ]
    with pytest.raises(AssertionError):
        simulate_and_individualize(user_boxes, box_mapping)
