from pytest import approx
import pytest

from deuxpots.box import Box, BoxKind, ReferenceBox
from deuxpots.tax_calculator import build_income_sheet
from deuxpots.valued_box import ValuedBox, build_valued_box


def test_valued_box_partner_0():
    valbox = ValuedBox(
        box=Box(
            code="1AC",
            reference=ReferenceBox(code="1AC", description="Salaires et pensions."),
            kind=BoxKind.PARTNER_0
        ),
        raw_value=300,
    )
    assert valbox.individualized_value(0) == approx(300)
    assert valbox.individualized_value(1) == 0
    valbox.ratio_0 = .3
    assert valbox.individualized_value(0) == approx(90)
    assert valbox.individualized_value(1) == approx(210)

def test_valued_box_partner_1():
    valbox = ValuedBox(
        box=Box(
            code="1AC",
            reference=ReferenceBox(code="1AC", description="Salaires et pensions."),
            kind=BoxKind.PARTNER_1
        ),
        raw_value=1000,
    )
    assert valbox.individualized_value(0) == 0
    assert valbox.individualized_value(1) == approx(1000)
    valbox.ratio_0 = .4
    assert valbox.individualized_value(0) == approx(400)
    assert valbox.individualized_value(1) == approx(600)


def test_valued_box_common():
    valbox = ValuedBox(
        box=Box(
            code="6FL",
            reference=ReferenceBox(code="6FL", description="Deficits globaux."),
            kind=BoxKind.COMMON
        ),
        raw_value=800,
    )
    assert valbox.individualized_value(0) is None
    assert valbox.individualized_value(1) is None
    valbox.ratio_0 = .7
    assert valbox.individualized_value(0) == approx(560)
    assert valbox.individualized_value(1) == approx(240)


def test_valued_box_child():
    valbox = ValuedBox(
        box=Box(
            code="1CC",
            reference=ReferenceBox(code="1AC", description="Salaires et pensions."),
            kind=BoxKind.CHILD
        ),
        raw_value=73229,
    )
    assert valbox.individualized_value(0) is None
    assert valbox.individualized_value(1) is None
    valbox.ratio_0 = 0
    assert valbox.individualized_value(0) == 0
    assert valbox.individualized_value(1) == 73229


def test_individualize_wrong_partner_id():
    valbox = ValuedBox(
        box=Box(
            code="1CC",
            reference=ReferenceBox(code="1AC", description="Salaires et pensions."),
            kind=BoxKind.CHILD
        ),
        raw_value=73229,
    )
    with pytest.raises(ValueError):
        valbox.individualized_value(3)


def test_build_valued_box():
    box = Box(
        code="1CC",
        reference=ReferenceBox(code="1AC", description="Salaires et pensions."),
        kind=BoxKind.CHILD
    )
    valbox = build_valued_box(code="1CC", raw_value=1254, box_mapping={"1CC": box}, ratio_0=.3)
    assert valbox.box == box
    assert valbox.raw_value == 1254
    assert valbox.ratio_0 == .3
