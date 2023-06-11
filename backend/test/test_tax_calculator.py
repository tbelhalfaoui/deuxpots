import pytest
import requests as rq
from deuxpots.box import Box, BoxKind, ReferenceBox
from deuxpots.tax_calculator import (
    SIMULATOR_URL, SimulatorError, SimulatorResult,
    _format_simulator_results, _simulator_api, build_income_sheet, compute_tax, handle_children_split
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


def test_compute_tax_single_with_child():
    income_sheet = {
        '0DA': '1950',
        'pre_situation_famille': 'C',
        'pre_situation_residence': 'M',
        '1AJ': 50000
    }
    res_without_child = compute_tax(income_sheet)
    res_with_child = compute_tax({
        '0CF': 1,
        **income_sheet
    })
    assert res_with_child.total_tax < res_without_child.total_tax


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
            attribution=1,
        ),
        ValuedBox(
            box=Box(
                code="1AC",
                reference=ReferenceBox(code="1AC", description="Salaires et pensions.", type="int"),
                kind=BoxKind.PARTNER_0
            ),
            raw_value=100,
            attribution=0,
        ),
        ValuedBox(
            box=Box(
                code="6FL",
                reference=ReferenceBox(code="6FL", description="Deficits globaux.", type="int"),
                kind=BoxKind.COMMON
            ),
            raw_value=1000,
            attribution=.55
        ),
        ValuedBox(
            box=Box(
                code="1CC",
                reference=ReferenceBox(code="1AC", description="Salaires et pensions.", type="int"),
                kind=BoxKind.CHILD
            ),
            raw_value=100,
            attribution=.8
        ),
        ValuedBox(
            box=Box(
                code="1DC",
                reference=ReferenceBox(code="1AC", description="Salaires et pensions.", type="int"),
                kind=BoxKind.CHILD
            ),
            raw_value=400,
            attribution=.4
        ),
        ValuedBox(
            box=Box(
                code="0AS",
                reference=ReferenceBox(code="0AS", description="Titulaire d'une pension militaire.", type='bool'),
                kind=BoxKind.COMMON
            ),
            raw_value=1,
            attribution=1,
        )
    ]


def test_build_income_sheet_missing_attribution():
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
    

def test_build_income_sheet_raw_value_empty():
    income_sheet = build_income_sheet([
        ValuedBox(
            box=Box(
                code="6FL",
                reference=ReferenceBox(code="6FL", description="Deficits globaux.", type="int"),
                kind=BoxKind.COMMON
            ),
            raw_value=0
        )
    ], individualize=0)
    assert income_sheet == {
        '0DA': '1950',
        'pre_situation_famille': 'C',
        'pre_situation_residence': 'M'
    }


def test_build_income_sheet_partner_0(valboxes):
    income_sheet = build_income_sheet(valboxes, individualize=0)
    assert income_sheet == {
        'pre_situation_famille': 'C',
        'pre_situation_residence': 'M',
        '0DA': '1950',
        '1AC': 360,  # 100 + .2 * 100 + .6 * 400
        '6FL': 450,  # .45 * 1000,
        '0AS': 0,
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
        '0AS': 1,
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
        '0AS': 1,
    }
    for box in ['1AC', '1BC', '1CC', '1DC', '6FL']:
        assert isinstance(income_sheet[box], int)

@pytest.mark.parametrize("sheet_in,sheet_expected", [
    # Convert number of children (including disabled)
    ({'0CF': 2.5,}, {'0CF': 2, '0CH': 1}),
    ({'0CF': .5, '0CG': .5}, {'0CH': 1, '0CI': 1}),
    ({'0CF': 1.5, '0CG': 1}, {'0CF': 1, '0CH': 1, '0CG': 1}),
    # Convert child care cost
    ({'0CF': .5, '7GA': 1000}, {'0CH': 1, '7GE': 1000}),
    ({'0CF': 1.5, '7GB': 1000}, {'0CF': 1, '0CH': 1, '7GE': 1000}),
    ({'0CF': 2.5, '7GC': 1000}, {'0CF': 2, '0CH': 1, '7GE': 1000}),
    # Squash child care costs for all children
    ({'0CF': 1, '7GA': 100, '7GB': 200, '7GC': 300}, {'0CF': 1, '7GA': 600}),
    ({'0CF': 1, '7GE': 100, '7GF': 200, '7GG': 300}, {'0CF': 1, '7GE': 600}),
    # Keep original boxes
    ({'9ZZ': 333}, {'9ZZ': 333}),
    ({'0CF': .5, '0CH': 1, '7GA': 400, '7GE': 500}, {'0CH': 2, '7GE': 900}),
])
def test_handle_half_children(sheet_in, sheet_expected):
    sheet_out = handle_children_split(sheet_in)
    sheet_out = {k: v for k, v in sheet_out.items() if v}
    sheet_expected =  {k: v for k, v in sheet_expected.items() if v}
    assert sheet_out == sheet_expected

