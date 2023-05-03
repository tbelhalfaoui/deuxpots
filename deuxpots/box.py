import json
from enum import Enum

from dataclasses import dataclass

CERFA_VARIABLES_PATH = "cerfa_variables.json"


class BoxKind(Enum):
    COMMON = 1
    PARTNER_0 = 2
    PARTNER_1 = 3
    CHILD = 4


@dataclass
class ReferenceBox:
    code: str
    description: str


@dataclass
class Box:
    code: str
    reference: ReferenceBox
    kind: BoxKind


def _generate_boxes(cerfa_variable):
    box_codes = cerfa_variable['boxes']
    ref = ReferenceBox(
        code=box_codes[0],
        description=cerfa_variable['description']
    )
    if len(box_codes) == 1:
        yield Box(
            code=ref.code,
            reference=ref,
            kind=BoxKind.COMMON
        )
    elif len(box_codes) >= 2:
        yield Box(
            code=box_codes[0],
            reference=ref,
            kind=BoxKind.PARTNER_0
        )
        yield Box(
            code=box_codes[1],
            reference=ref,
            kind=BoxKind.PARTNER_1
        )
        for box_code in sorted(box_codes[2:]):
            yield Box(
                code=box_code,
                reference=ref,
                kind=BoxKind.CHILD
            )


def build_box_mapping(cerfa_variables):
    return {box.code: box
            for var in cerfa_variables
            for box in _generate_boxes(var)}        


def load_box_mapping(cerfa_variables_path=CERFA_VARIABLES_PATH):
    with open(cerfa_variables_path) as f:
        cerfa_variables = json.load(f)
    return build_box_mapping(cerfa_variables)
