from dataclasses import dataclass
from typing import Optional
from deuxpots.box import Box, BoxKind


DEFAUT_ATTRIBUTION_FROM_KIND = {
    BoxKind.PARTNER_0: 0,
    BoxKind.PARTNER_1: 1,
}


class UnknownBoxCode(KeyError):
    pass


@dataclass
class ValuedBox:
    box: Box
    raw_value: int = None
    attribution: float = None

    def __post_init__(self):
        """
        Automatically set the attribution for PARTNER_i boxes.
        For CHILD and COMMON boxes, let the user decide (return None).

        The attribution for the second partner (partner 1).
        Example:
            * attribution = 0 means "100% for partner 0".
            * attribution = 1 means "100% for partner 1".
            * attribution = .2 means "20% for partner 1 and 80% for partner 0".
        
        """
        
        if self.attribution is None:
            self.attribution = DEFAUT_ATTRIBUTION_FROM_KIND.get(self.box.kind)
    
    def individualized_value(self, partner_idx) -> Optional[int]:
        assert partner_idx in {0, 1}
        if self.attribution is None:
            return
        if partner_idx == 0:
            return round(self.raw_value * (1 - self.attribution))
        if partner_idx == 1:
            return round(self.raw_value * self.attribution)


def build_valued_box(code, raw_value, box_mapping, attribution=None):
    try:
        box = box_mapping[code]
    except KeyError:
        raise UnknownBoxCode(f"La case {code}, trouvée dans la déclaration, est inconnue.")
    return ValuedBox(box, raw_value=raw_value, attribution=attribution)
