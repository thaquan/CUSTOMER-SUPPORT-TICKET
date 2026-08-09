"""Reusable helpers for building Gold dimensions."""

import pandas as pd


def build_dimension(
    source: pd.DataFrame,
    attributes: list[str],
    key_name: str,
) -> pd.DataFrame:
    """Build one dimension row per unique attribute combination."""
    dimension = (
        source[attributes]
        .drop_duplicates()
        .sort_values(attributes)
        .reset_index(drop=True)
    )

    dimension.insert(
        0, 
        key_name,
        range(1, len(dimension) + 1),
    )

    return dimension
