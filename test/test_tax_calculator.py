import pytest
import requests as rq
from difflib import SequenceMatcher
from deuxpots.tax_calculator import SIMULATOR_URL, SimulatorResult, _format_simulator_results, _simulator_api, compute_tax


@pytest.fixture
def data_single_notax():
    return {
        '0DA': '1950',
        'pre_situation_famille': 'C',
        'pre_situation_residence': 'M',
        '1AJ': 8000,
    }


def test__simulator_api(data_single_notax):
    results = _simulator_api(data_single_notax)
    for field in ["RASTXFOYER", "IINETIR", "IINET", "IREST"]:
        assert field in results


@pytest.mark.parametrize("simulator_results,expected", [
    ({
        "RASTXFOYER": "  19.0 ",  # Taux prélèvement à la source
        "IINETIR": "  10000 ",    # Impôt sur le revenu net
        "IINET": "  3000 ",       # Impôt restant à payer
        "IREST": "  0 ",          # Montant qui sera remboursé
    },
    SimulatorResult(
        rate=0.19, total_tax=10000, already_paid=7000, remains_to_pay=3000
    )),
    ({
        "RASTXFOYER": "  19.0 ",
        "IINETIR": " 2000",
        "IINET": " 0  ",
        "IREST": " 500",
    },
    SimulatorResult(rate=0.19,
        total_tax=2000,
        already_paid=2500,
        remains_to_pay=-500
    ))
])
def test__format_simulator_results(simulator_results, expected):
    res = _format_simulator_results(simulator_results)
    assert res == expected


@pytest.mark.parametrize("income,min_expected_tax,max_expected_tax", [
    (8000, 0, 0),
    (40000, 3000, 5000)
])
def test_compute_tax_single(income, min_expected_tax, max_expected_tax):
    res = compute_tax({
        '0DA': '1950',
        'pre_situation_famille': 'C',
        'pre_situation_residence': 'M',
        '1AJ': income,
    })
    assert min_expected_tax <= res.total_tax <= max_expected_tax
    assert res.remains_to_pay == res.total_tax


def test_compute_tax_single_overpaid():
    res = compute_tax({
        '0DA': '1950',
        'pre_situation_famille': 'C',
        'pre_situation_residence': 'M',
        '1AJ': 50000,
        '8HW': 10000
    })
    assert res.remains_to_pay < 0
