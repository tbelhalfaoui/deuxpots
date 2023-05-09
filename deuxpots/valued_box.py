from dataclasses import dataclass
from typing import Optional
from deuxpots.box import Box, BoxKind


DEFAUT_RATIO_FROM_KIND = {
    BoxKind.PARTNER_0: 0,
    BoxKind.PARTNER_1: 1,
}


class UnknownBoxCode(KeyError):
    pass


@dataclass
class ValuedBox:
    box: Box
    raw_value: int = None
    ratio: float = None

    def __post_init__(self):
        """
        Automatically set the ratio for PARTNER_i boxes.
        For CHILD and COMMON boxes, let the user decide (return None).

        The ratio for the second partner (partner 1).
        Example:
            * ratio = 0 means "100% for partner 0".
            * ratio = 1 means "100% for partner 1".
            * ratio = .2 means "20% for partner 1 and 80% for partner 0".
        
        """
        
        if self.ratio is None:
            self.ratio = DEFAUT_RATIO_FROM_KIND.get(self.box.kind)
    
    def individualized_value(self, partner_idx) -> Optional[int]:
        assert partner_idx in {0, 1}
        if self.ratio is None:
            return
        if partner_idx == 0:
            return round(self.raw_value * (1 - self.ratio))
        if partner_idx == 1:
            return round(self.raw_value * self.ratio)


def build_valued_box(code, raw_value, box_mapping, ratio=None):
    try:
        box = box_mapping[code]
    except KeyError:
        raise UnknownBoxCode(f"La case {code}, trouvée dans la déclaration, est inconnue.")
    return ValuedBox(box, raw_value=raw_value, ratio=ratio)
