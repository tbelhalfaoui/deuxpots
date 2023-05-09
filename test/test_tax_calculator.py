import pytest
import requests as rq
from deuxpots.box import Box, BoxKind, ReferenceBox
from deuxpots.tax_calculator import (
    SIMULATOR_URL, SimulatorError, SimulatorResult,
    _format_simulator_results, _simulator_api, build_income_sheet, compute_tax
)
from deuxpots.valued_box import ValuedBox


@pytest.fixture
def sheet_single_notax():
    return {
        '0DA': '1950',
        'pre_situation_famille': 'C',
        'pre_situation_residence': 'M',
        '1AJ': 8000,
    }


def test__simulator_api(sheet_single_notax):
    results = _simulator_api(sheet_single_notax)
    for field in ["RASTXFOYER", "IINETIR", "IINET", "IREST"]:
        assert field in results


@pytest.mark.parametrize("simulator_results,expected", [
    ({
        "IINETIR": "  10000 ",    # Impôt sur le revenu net
        "IINET": "  3000 ",       # Impôt restant à payer
        "IREST": "  0 ",          # Montant qui sera remboursé
    },
    SimulatorResult(
        total_tax=10000, already_paid=7000, remains_to_pay=3000
    )),
    ({
        "IINETIR": " 2000",
        "IINET": " 0  ",
        "IREST": " 500",
    },
    SimulatorResult(
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


def test_compute_tax_error():
    with pytest.raises(SimulatorError) as e:
        compute_tax({
            '0DA': '1950',
            'pre_situation_famille': 'C',   # Should be O or M (not single)
            'pre_situation_residence': 'M',
            '1AJ': 50000,
            '1BJ': 30000,
        })
        assert len(e.value.args[0]) > 80


@pytest.fixture
def valboxes():
    return [
        ValuedBox(
            box=Box(
                code="1BC",
                reference=ReferenceBox(code="1AC", description="Salaires et pensions.", type="int"),
                kind=BoxKind.PARTNER_1
            ),
            raw_value=200,
            ratio=1,
        ),
        ValuedBox(
            box=Box(
                code="1AC",
                reference=ReferenceBox(code="1AC", description="Salaires et pensions.", type="int"),
                kind=BoxKind.PARTNER_0
            ),
            raw_value=100,
            ratio=0,
        ),
        ValuedBox(
            box=Box(
                code="6FL",
                reference=ReferenceBox(code="6FL", description="Deficits globaux.", type="int"),
                kind=BoxKind.COMMON
            ),
            raw_value=1000,
            ratio=.55
        ),
        ValuedBox(
            box=Box(
                code="1CC",
                reference=ReferenceBox(code="1AC", description="Salaires et pensions.", type="int"),
                kind=BoxKind.CHILD
            ),
            raw_value=100,
            ratio=.8
        ),
        ValuedBox(
            box=Box(
                code="1DC",
                reference=ReferenceBox(code="1AC", description="Salaires et pensions.", type="int"),
                kind=BoxKind.CHILD
            ),
            raw_value=400,
            ratio=.4
        ),
        ValuedBox(
            box=Box(
                code="AS",
                reference=ReferenceBox(code="AS", description="Titulaire d'une pension militaire.", type='bool'),
                kind=BoxKind.COMMON
            ),
            raw_value=1,
            ratio=1,
        )
    ]


def test_build_income_sheet_missing_ratio():
    with pytest.raises(AssertionError):
        build_income_sheet([
            ValuedBox(
                box=Box(
                    code="6FL",
                    reference=ReferenceBox(code="6FL", description="Deficits globaux.", type="int"),
                    kind=BoxKind.COMMON
                ),
                raw_value=1000
            )
        ], individualize=0)


def test_build_income_sheet_partner_0(valboxes):
    income_sheet = build_income_sheet(valboxes, individualize=0)
    assert income_sheet == {
        'pre_situation_famille': 'C',
        'pre_situation_residence': 'M',
        '0DA': '1950',
        '1AC': 360,  # 100 + .2 * 100 + .6 * 400
        '6FL': 450,  # .45 * 1000,
        'AS': 0,
    }
    assert isinstance(income_sheet['1AC'], int)
    assert isinstance(income_sheet['6FL'], int)


def test_build_income_sheet_partner_1(valboxes):
    income_sheet = build_income_sheet(valboxes, individualize=1)
    assert income_sheet == {
        'pre_situation_famille': 'C',
        'pre_situation_residence': 'M',
        '0DA': '1950',
        '1AC': 440,  # 200 + .8 * 100 + .4 * 400
        '6FL': 550,  # .55 * 1000
        'AS': 1,
    }
    assert isinstance(income_sheet['1AC'], int)
    assert isinstance(income_sheet['6FL'], int)


def test_build_income_sheet_together(valboxes):
    income_sheet = build_income_sheet(valboxes, individualize=None)
    assert income_sheet == {
        'pre_situation_famille': 'O',
        'pre_situation_residence': 'M',
        '0DA': '1950',
        '0DB': '1950',
        '1AC': 100,
        '1BC': 200,
        '1CC': 100,
        '1DC': 400,
        '6FL': 1000,
        'AS': 1,
    }
    for box in ['1AC', '1BC', '1CC', '1DC', '6FL']:
        assert isinstance(income_sheet[box], int)
