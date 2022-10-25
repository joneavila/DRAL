# _elan_funcs.py    October 19, 2022    Jonathan Avila

from pympi import Eaf
import pandas as pd
from pathlib import Path


def read_eaf_into_df(eaf_path: Path) -> pd.DataFrame:
    # Read all tier annotation data in the Elan file at `eaf_path` into a pandas
    # DataFrame with the columns: value, tier_name, time_start, time_end.

    eaf = Eaf(eaf_path)
    markup = []

    # For each tier.
    for tier_name, tier_data in eaf.tiers.items():

        # For each annotation append (value, tier name, time start, time end) to a list.
        aligned_annotations, _, _, _ = tier_data
        for annotation in aligned_annotations.values():
            ts_start, ts_end, value, _ = annotation
            time_start = eaf.timeslots[ts_start]
            time_end = eaf.timeslots[ts_end]
            markup.append((value, tier_name, time_start, time_end))

    # Convert the list into a pandas Dataframe.
    df_markup = pd.DataFrame(
        markup, columns=["value", "tier_name", "time_start", "time_end"]
    )
    return df_markup
