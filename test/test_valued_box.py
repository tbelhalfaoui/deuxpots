from pytest import approx
import pytest

from deuxpots.box import Box, BoxKind, ReferenceBox
from deuxpots.tax_calculator import build_income_sheet
from deuxpots.valued_box import ValuedBox, build_valued_box


def test_valued_box_partner_0():
    valbox = ValuedBox(
        box=Box(
            code="1AC",
            reference=ReferenceBox(code="1AC", description="Salaires et pensions.", type='int'),
            kind=BoxKind.PARTNER_0
        ),
        raw_value=300,
    )
    assert valbox.individualized_value(0) == 300
    assert valbox.individualized_value(1) == 0
    valbox.ratio_0 = .3
    assert valbox.individualized_value(0) == 90
    assert valbox.individualized_value(1) == 210

def test_valued_box_partner_1():
    valbox = ValuedBox(
        box=Box(
            code="1AC",
            reference=ReferenceBox(code="1AC", description="Salaires et pensions.", type='int'),
            kind=BoxKind.PARTNER_1
        ),
        raw_value=1000,
    )
    assert valbox.individualized_value(0) == 0
    assert valbox.individualized_value(1) == 1000
    valbox.ratio_0 = .4
    assert valbox.individualized_value(0) == 400
    assert valbox.individualized_value(1) == 600


def test_valued_box_common():
    valbox = ValuedBox(
        box=Box(
            code="6FL",
            reference=ReferenceBox(code="6FL", description="Deficits globaux.", type='int'),
            kind=BoxKind.COMMON
        ),
        raw_value=800,
    )
    assert valbox.individualized_value(0) is None
    assert valbox.individualized_value(1) is None
    valbox.ratio_0 = .7
    assert valbox.individualized_value(0) == 560
    assert valbox.individualized_value(1) == 240


def test_valued_box_child():
    valbox = ValuedBox(
        box=Box(
            code="1CC",
            reference=ReferenceBox(code="1AC", description="Salaires et pensions.", type='int'),
            kind=BoxKind.CHILD
        ),
        raw_value=73229,
    )
    assert valbox.individualized_value(0) is None
    assert valbox.individualized_value(1) is None
    valbox.ratio_0 = 0
    assert valbox.individualized_value(0) == 0
    assert valbox.individualized_value(1) == 73229


def test_valued_box_partner_0_boolean():
    valbox = ValuedBox(
        box=Box(
            code="AP",
            reference=ReferenceBox(code="AP", description="Titulaire d'une pension invalidité.", type='bool'),
            kind=BoxKind.PARTNER_0
        ),
        raw_value=1,
    )
    assert valbox.individualized_value(0) == 1
    assert valbox.individualized_value(1) == 0
    valbox.ratio_0 = .2
    assert valbox.individualized_value(0) == 0
    assert valbox.individualized_value(1) == 1


def test_valued_box_common_boolean():
    valbox = ValuedBox(
        box=Box(
            code="AS",
            reference=ReferenceBox(code="AS", description="Titulaire d'une pension militaire.", type='bool'),
            kind=BoxKind.COMMON
        ),
        raw_value=1,
    )
    assert valbox.individualized_value(0) is None
    assert valbox.individualized_value(1) is None
    valbox.ratio_0 = .2
    assert valbox.individualized_value(0) == 0
    assert valbox.individualized_value(1) == 1


def test_individualize_wrong_partner_id():
    valbox = ValuedBox(
        box=Box(
            code="1CC",
            reference=ReferenceBox(code="1AC", description="Salaires et pensions.", type='int'),
            kind=BoxKind.CHILD
        ),
        raw_value=73229,
    )
    with pytest.raises(AssertionError):
        valbox.individualized_value(3)


def test_build_valued_box():
    box = Box(
        code="1CC",
        reference=ReferenceBox(code="1AC", description="Salaires et pensions.", type='int'),
        kind=BoxKind.CHILD
    )
    valbox = build_valued_box(code="1CC", raw_value=1254, box_mapping={"1CC": box}, ratio_0=.3)
    assert valbox.box == box
    assert valbox.raw_value == 1254
    assert valbox.ratio_0 == .3
