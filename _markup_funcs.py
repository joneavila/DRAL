# _markup_funcs.py    October 19, 2022    Jonathan Avila

class MarkupTier:
    all_tiers = {}

    def __init__(
        self, name: str, short_name: str = None, remix_dict: dict = None
    ) -> None:
        # `name` is the name of the tier entered in ELAN.
        # `short_name` is a custom abbreviated name.
        # `remix_dict` is a channel remix dictionary to use with pysox functions.
        self.name = name
        self.short_name = short_name
        self.remix_dict = remix_dict

        MarkupTier.all_tiers[name] = self
