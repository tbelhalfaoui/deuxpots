from dataclasses import asdict
import json
import pytest

from deuxpots.box import Box, BoxKind, ReferenceBox
from deuxpots.flatbox import FlatBox
from deuxpots.valued_box import UnknownBoxCodeWarning, ValuedBox


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
    valbox.attribution = .7
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
    valbox.attribution = .6
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
    valbox.attribution = .3
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
    valbox.attribution = 1
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
    valbox.attribution = .8
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
    valbox.attribution = .8
    assert valbox.individualized_value(0) == 0
    assert valbox.individualized_value(1) == 1


def test_valued_box_common_float():
    valbox = ValuedBox(
        box=Box(
            code="0CF",
            reference=ReferenceBox(code="0CF", description="Nombre d'enfants.", type='float'),
            kind=BoxKind.COMMON
        ),
        raw_value=2,
    )
    assert valbox.individualized_value(0) is None
    assert valbox.individualized_value(1) is None
    valbox.attribution = .75
    assert valbox.individualized_value(0) == .5
    assert valbox.individualized_value(1) == 1.5


def test_valued_box_common_float_is_integer():
    valbox = ValuedBox(
        box=Box(
            code="0CF",
            reference=ReferenceBox(code="0CF", description="Nombre d'enfants.", type='float'),
            kind=BoxKind.COMMON
        ),
        raw_value=2,
    )
    assert valbox.individualized_value(0) is None
    assert valbox.individualized_value(1) is None
    valbox.attribution = .5
    assert valbox.individualized_value(0) == 1
    assert isinstance(valbox.individualized_value(0), int)
    assert valbox.individualized_value(1) == 1
    assert isinstance(valbox.individualized_value(1), int)


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


def test_from_flat_box():
    box = Box(
        code="1CC",
        reference=ReferenceBox(code="1AC", description="Salaires et pensions.", type='int'),
        kind=BoxKind.CHILD
    )
    valbox = ValuedBox.from_flat_box(FlatBox(code="1CC", raw_value=1254, attribution=.3, description="dummy"), box_mapping={"1CC": box})
    assert valbox.box == box
    assert valbox.raw_value == 1254
    assert valbox.attribution == .3


def test_from_flat_box_unknown_code():
    with pytest.warns(UnknownBoxCodeWarning):
        valbox = ValuedBox.from_flat_box(FlatBox(code="9ZZ", raw_value=100, description="Une nouvelle case!"), box_mapping={})
    assert valbox.box.code == "9ZZ"
    assert valbox.box.reference.code == "9ZZ"
    assert valbox.box.reference.description == "Une nouvelle case!"
    assert valbox.box.reference.type == "int"
    assert valbox.raw_value == 100


def test_serialize_valued_box():
    valbox = ValuedBox(
        box=Box(
            code="6FL",
            reference=ReferenceBox(code="6FL", description="Deficits globaux.", type='int'),
            kind=BoxKind.PARTNER_0
        ),
        attribution=.7,
        raw_value=800,
    )
    assert json.dumps(asdict(valbox))


def test_valued_box_zero_value_is_attributed():
    valbox = ValuedBox(
        box=Box(
            code="7HB",
            reference=ReferenceBox(code="7HB", description="Services à la personne - réductions d'impôt", type='int'),
            kind=BoxKind.COMMON
        ),
        raw_value=0,
    )
    assert valbox.individualized_value(0) == 0
    assert valbox.individualized_value(1) == 0
