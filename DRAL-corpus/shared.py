# Mostly constants shared across Python scripts.

from typing import Optional


class MarkupTier:
    tiers_dict = {}

    def __init__(
        self, name: str, track_side_code: Optional[str] = None, remix_dict: Optional[dict] = None
    ) -> None:
        # `name` is the name of the tier entered in ELAN.
        # `track_side_code` is a letter indicating which audio track the tier belongs
        # to: left (`l`), right (`r`).
        # `remix_dict` is a channel remix dictionary to use with pysox functions.
        self.name = name
        self.track_side_code = track_side_code
        self.remix_dict = remix_dict

        MarkupTier.tiers_dict[name] = self


LANG_CODES = ["EN", "ES", "JA", "BN", "FR"]

CONV_CODE_ORIGINAL = "OG"
CONV_CODE_REENACTED = "RE"

MARKUP_TIER_LEFT = MarkupTier("LittleLeft", "l", {1: [1]})
MARKUP_TIER_RIGHT = MarkupTier("LittleRight", "r", {1: [2]})
MARKUP_TIER_BOTH = MarkupTier("Utterance")

MARKUP_TIERS_DICT = MarkupTier.tiers_dict
MARKUP_TIER_PATTERN = "|".join(MarkupTier.tiers_dict.keys())

MARKUP_VAL_RE_PATTERN = r"^#?\d+$"
