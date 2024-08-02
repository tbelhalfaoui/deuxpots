from unittest.mock import ANY
import pytest
from deuxpots.flatbox import FlatBox
from deuxpots.individualize import (
    IndividualResult, IndividualizedResults,
    simulate_and_individualize
)
from deuxpots.tax_calculator import SimulatorResult
from deuxpots.valued_box import ValuedBox


def test__individualize_both_pay_to_tax_office():
    results = IndividualizedResults.from_simulations(
        simu_partner_0=SimulatorResult(total_tax=6000, already_paid=1000, remains_to_pay=5000),
        simu_partner_1=SimulatorResult(total_tax=4000, already_paid=500, remains_to_pay=3500),
        simu_together=SimulatorResult(total_tax=8000, already_paid=None, remains_to_pay=None)  # None because unused here
    )
    assert results == IndividualizedResults(
        total_tax_single=10000,
        total_tax_together=8000,
        total_tax_gain=2000,
        partners_proportional_split=(
            IndividualResult(
                tax_if_single=6000,
                tax_gain=1200,   # .6 * 2000
                total_tax=4800,
                already_paid=1000,
                remains_to_pay=3800,  # 4800 - 1000
                remains_to_pay_to_tax_office=3800,
                remains_to_pay_to_partner=0,
            ),
            IndividualResult(
                tax_if_single=4000,
                tax_gain=800,   # .4 * 2000
                total_tax=3200,
                already_paid=500,
                remains_to_pay=2700,  # 3200 - 500
                remains_to_pay_to_tax_office=2700,
                remains_to_pay_to_partner=0,
            )
        ),
        partners_equal_split=(
            IndividualResult(
                tax_if_single=6000,
                tax_gain=1000,   # 2000 / 2
                total_tax=5000,  # 6000 - 1000
                already_paid=1000,
                remains_to_pay=4000,
                remains_to_pay_to_tax_office=4000,
                remains_to_pay_to_partner=0,
            ),
            IndividualResult(
                tax_if_single=4000,
                tax_gain=1000,   # 2000 / 2
                total_tax=3000,  # 4000 - 1000
                already_paid=500,
                remains_to_pay=2500,
                remains_to_pay_to_tax_office=2500,
                remains_to_pay_to_partner=0,
            )
        )
    )


def test__individualize_get_back_from_partner():
    results = IndividualizedResults.from_simulations(
        simu_partner_0=SimulatorResult(total_tax=6000, already_paid=1000, remains_to_pay=5000),
        simu_partner_1=SimulatorResult(total_tax=4000, already_paid=3900, remains_to_pay=100),
        simu_together=SimulatorResult(total_tax=8000, already_paid=None, remains_to_pay=None)  # None because unused here
    )
    assert results == IndividualizedResults(
        total_tax_single=10000,
        total_tax_together=8000,
        total_tax_gain=2000,
        partners_proportional_split=(
            IndividualResult(
                tax_if_single=6000,
                tax_gain=1200,   # .6 * 2000
                total_tax=4800,
                already_paid=1000,
                remains_to_pay=3800,  # 4800 - 1000
                remains_to_pay_to_tax_office=3100,
                remains_to_pay_to_partner=700,
            ),
            IndividualResult(
                tax_if_single=4000,
                tax_gain=800,   # .4 * 2000
                total_tax=3200,
                already_paid=3900,
                remains_to_pay=-700,  # 3200 - 3900
                remains_to_pay_to_tax_office=0,
                remains_to_pay_to_partner=-700,
            )
        ),
        partners_equal_split=(
            IndividualResult(
                tax_if_single=6000,
                tax_gain=1000,   # 2000 / 2
                total_tax=5000,  # 6000 - 1000
                already_paid=1000,
                remains_to_pay=4000,
                remains_to_pay_to_tax_office=3100,
                remains_to_pay_to_partner=900,
            ),
            IndividualResult(
                tax_if_single=4000,
                tax_gain=1000,   # 2000 / 2
                total_tax=3000,  # 4000 - 1000
                already_paid=3900,
                remains_to_pay=-900,
                remains_to_pay_to_tax_office=0,
                remains_to_pay_to_partner=-900,
            )
        )
    )


def test__individualize_both_get_back_money():
    results = IndividualizedResults.from_simulations(
        simu_partner_0=SimulatorResult(total_tax=0, already_paid=100, remains_to_pay=0),
        simu_partner_1=SimulatorResult(total_tax=0, already_paid=200, remains_to_pay=0),
        simu_together=SimulatorResult(total_tax=0, already_paid=None, remains_to_pay=None)  # None because unused here
    )
    assert results == IndividualizedResults(
        total_tax_single=0,
        total_tax_together=0,
        total_tax_gain=0,
        partners_proportional_split=(
            IndividualResult(
                tax_if_single=0,
                total_tax=0,
                tax_gain=0,
                already_paid=100,
                remains_to_pay=-100,
                remains_to_pay_to_tax_office=-100,
                remains_to_pay_to_partner=0,
            ),
            IndividualResult(
                tax_if_single=0,
                total_tax=0,
                tax_gain=0,
                already_paid=200,
                remains_to_pay=-200,
                remains_to_pay_to_tax_office=-200,
                remains_to_pay_to_partner=0,
            )
        ),
        partners_equal_split=(
            IndividualResult(
                tax_if_single=0,
                total_tax=0,
                tax_gain=0,
                already_paid=100,
                remains_to_pay=-100,
                remains_to_pay_to_tax_office=-100,
                remains_to_pay_to_partner=0,
            ),
            IndividualResult(
                tax_if_single=0,
                total_tax=0,
                tax_gain=0,
                already_paid=200,
                remains_to_pay=-200,
                remains_to_pay_to_tax_office=-200,
                remains_to_pay_to_partner=0,
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
        FlatBox(code='8HW', raw_value=600, attribution=0),
    ]
    valboxes = [ValuedBox.from_flat_box(flatbox, box_mapping) for flatbox in user_boxes]
    result = simulate_and_individualize(valboxes)
    assert result.partners_proportional_split[0].remains_to_pay > 500
    assert result.partners_proportional_split[1].remains_to_pay < 4000
    assert result.partners_equal_split[0].remains_to_pay > 500
    assert result.partners_equal_split[1].remains_to_pay < 4000


def test_simulate_and_individualize_missing_attribution(box_mapping):
    user_boxes = [
        FlatBox(code='2DC', raw_value=3, attribution=None)
    ]
    valboxes = [ValuedBox.from_flat_box(flatbox, box_mapping) for flatbox in user_boxes]
    with pytest.raises(AssertionError):
        simulate_and_individualize(valboxes)
