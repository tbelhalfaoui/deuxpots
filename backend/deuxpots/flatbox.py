from dataclasses import dataclass
from typing import Optional

from deuxpots.valued_box import ValuedBox


@dataclass
class FlatBox:
    """
    Exchange format of the API.
    
    """
    code: str
    raw_value: int
    description: str = None
    attribution: Optional[float] = None

    def __lt__(self, other):
        return self.code < other.code


def flatten(valbox: ValuedBox) -> FlatBox:
    return FlatBox(
        code=valbox.box.code,
        description=valbox.box.reference.description,
        raw_value=valbox.raw_value,
        attribution=valbox.attribution
    )