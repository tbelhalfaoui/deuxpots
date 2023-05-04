from dataclasses import asdict

import pytest
from deuxpots.box import load_box_mapping
from deuxpots.individualize import HouseholdStatusError, IndividualResult, IndividualizedResults, _individualize, simulate_and_individualize
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


def test_simulate_and_individualize():
    parsed_sheeet = {
        'AM': 1,
        'AC': 0,
        '1AJ': 40000,
        '1BJ': 20000,
        # '1CJ': 300,
        # '1DJ': 400,
        '2DC': 350,
        '8HV': 700, 
        '8IV': 7000,
        '8HW': 600,
    }
    user_ratios = {
        '2DC': 0,
        # '1CJ': 0,
        # '1DJ': .3,
    }
    box_mapping = load_box_mapping()
    result = simulate_and_individualize(parsed_sheeet, user_ratios, box_mapping)
    assert result['individualized'].partners[0].remains_to_pay > 1000
    assert result['individualized'].partners[1].remains_to_pay < 4000


def test_simulate_and_individualize_user_input_needed():
    parsed_sheeet = {
        'AO': 1,
        '1AJ': 40000,
        '1BJ': 20000,
        '2DC': 350,
    }
    box_mapping = load_box_mapping()
    result = simulate_and_individualize(parsed_sheeet, {}, box_mapping)
    assert not result.get('individualized')


@pytest.mark.parametrize('parsed_sheeet', [{}, {'AD': 1}, {'AC': 1}, {'AV': 1}, {'AM': 1, 'AO': 1}])
def test_simulate_and_individualize_bad_household_status(parsed_sheeet):
    parsed_sheeet = {}
    box_mapping = load_box_mapping()
    with pytest.raises(HouseholdStatusError):
        simulate_and_individualize(parsed_sheeet, {}, box_mapping)
