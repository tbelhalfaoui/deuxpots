from dataclasses import dataclass
from typing import Optional
from deuxpots.box import Box, BoxKind


DEFAUT_RATIO_FROM_KIND = {
    BoxKind.PARTNER_0: 1.,
    BoxKind.PARTNER_1: 0.,
}


class UnknownBoxCode(KeyError):
    pass


@dataclass
class ValuedBox:
    box: Box
    raw_value: int = None
    ratio_0: float = None

    def __post_init__(self):
        # The ratio for partner 0.
        # E.g. ratio_0 = .8 means "80% assigned to partner 0 and 20% to partner 1".
        if self.ratio_0 is None:
            self.ratio_0 = self._auto_set_ratio()

    def _auto_set_ratio(self):
        """
        Automatically set the ratio for PARTNER_i boxes.
        For CHILD and COMMON boxes, let the user decide (return None).
        """
        return DEFAUT_RATIO_FROM_KIND.get(self.box.kind)
    
    def individualized_value(self, partner_idx) -> Optional[int]:
        assert partner_idx in {0, 1}
        if self.ratio_0 is None:
            return
        if partner_idx == 0:
            return round(self.raw_value * self.ratio_0)
        if partner_idx == 1:
            return round(self.raw_value * (1 - self.ratio_0))


def build_valued_box(code, raw_value, box_mapping, ratio_0=None):
    try:
        box = box_mapping[code]
    except KeyError:
        raise UnknownBoxCode(f"La case {code}, trouvée dans la déclaration, est inconnue.")
    return ValuedBox(box, raw_value=raw_value, ratio_0=ratio_0)
