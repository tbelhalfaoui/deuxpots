import pytest
from deuxpots.flatbox import FlatBox
from deuxpots.individualize import (
    IndividualResult, IndividualizedResults,
    _individualize, simulate_and_individualize
)
from deuxpots.pdf_tax_parser import HouseholdStatusError
from deuxpots.tax_calculator import SimulatorResult
from deuxpots.valued_box import ValuedBox


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
        FlatBox(code='1BJ', raw_value=20000, attribution=1),
        FlatBox(code='1AJ', raw_value=40000, attribution=0),
        FlatBox(code='2DC', raw_value=350, attribution=1),
        FlatBox(code='8HV', raw_value=700, attribution=.1),
        FlatBox(code='8IV', raw_value=7000, attribution=.9),
        FlatBox(code='8HW', raw_value=600, attribution=0),
    ]
    valboxes = [ValuedBox.from_flat_box(flatbox, box_mapping) for flatbox in user_boxes]
    result = simulate_and_individualize(valboxes)
    assert result.partners[0].remains_to_pay > 1000
    assert result.partners[1].remains_to_pay < 4000


def test_simulate_and_individualize_missing_attribution(box_mapping):
    user_boxes = [
        FlatBox(code='2DC', raw_value=3, attribution=None)
    ]
    valboxes = [ValuedBox.from_flat_box(flatbox, box_mapping) for flatbox in user_boxes]
    with pytest.raises(AssertionError):
        simulate_and_individualize(valboxes)
