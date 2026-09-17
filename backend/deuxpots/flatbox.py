from dataclasses import dataclass
from typing import List, Optional

from deuxpots.valued_box import ValuedBox


@dataclass
class FlatBox:
    """
    Exchange format of the API.
    
    """
    code: str
    raw_value: int
    type: str = None
    description: str = None
    attribution: Optional[float] = None
    # Cases dont cette case hérite sa répartition par défaut (voir attribution_links).
    attribution_follows: Optional[List[str]] = None

    def __lt__(self, other):
        return self.code < other.code


def flatten(valbox: ValuedBox) -> FlatBox:
    return FlatBox(
        code=valbox.box.code,
        description=valbox.box.reference.description,
        raw_value=valbox.raw_value,
        attribution=valbox.attribution,
        type=valbox.box.reference.type,
    )