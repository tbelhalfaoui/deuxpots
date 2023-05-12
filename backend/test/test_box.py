from deuxpots.box import Box, BoxKind, ReferenceBox, _generate_boxes, build_box_mapping


def test__generate_boxes_partner():
    cerfa_variable = {
        "boxes": ["5HG", "5IG"],
        "type": "int",
        "description": "Plus-values à long terme."
    }
    boxes = list(_generate_boxes(cerfa_variable))
    assert boxes == [
        Box(
            code="5HG",
            reference=ReferenceBox(code="5HG", description="Plus-values à long terme.", type="int"),
            kind=BoxKind.PARTNER_0
        ),
        Box(
            code="5IG",
            reference=ReferenceBox(code="5HG", description="Plus-values à long terme.", type="int"),
            kind=BoxKind.PARTNER_1
        )
    ]


def test__generate_boxes_partner_and_children():
    cerfa_variable = {
        "boxes": ["1AC", "1BC", "1CC", "1DC"],
        "type": "int",
        "description": "Salaires et pensions."
    }
    boxes = list(_generate_boxes(cerfa_variable))
    assert boxes == [
        Box(
            code="1AC",
            reference=ReferenceBox(code="1AC", description="Salaires et pensions.", type="int"),
            kind=BoxKind.PARTNER_0
        ),
        Box(
            code="1BC",
            reference=ReferenceBox(code="1AC", description="Salaires et pensions.", type="int"),
            kind=BoxKind.PARTNER_1
        ),
        Box(
            code="1CC",
            reference=ReferenceBox(code="1AC", description="Salaires et pensions.", type="int"),
            kind=BoxKind.CHILD
        ),
        Box(
            code="1DC",
            reference=ReferenceBox(code="1AC", description="Salaires et pensions.", type="int"),
            kind=BoxKind.CHILD
        ),
    ]


def test__generate_boxes_common():
    cerfa_variable = {
        "boxes": ["6FL"],
        "type": "int",
        "description": "Deficits globaux."
    }
    boxes = list(_generate_boxes(cerfa_variable))
    assert boxes == [
        Box(
            code="6FL",
            reference=ReferenceBox(code="6FL", description="Deficits globaux.", type="int"),
            kind=BoxKind.COMMON
        )
    ]


def test_build_box_mapping():
    cerfa_variable = {
        "boxes": ["6FL"],
        "type": "int",
        "description": "Deficits globaux."
    }
    mapping = build_box_mapping([cerfa_variable])
    assert isinstance(mapping["6FL"], Box)
