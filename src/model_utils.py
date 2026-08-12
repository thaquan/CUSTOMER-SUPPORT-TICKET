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


def attach_dimension_key(
    source: pd.DataFrame,
    dimension: pd.DataFrame,
    attributes: list[str],
    key_name: str,
) -> pd.DataFrame:
    """Attach a surrogate key through a validated many-to-one lookup."""

    lookup_columns = [
        key_name,
        *attributes,
    ]

    lookup = dimension[lookup_columns]

    result = source.merge(
        lookup,
        on=attributes,
        how="left",
        validate="many_to_one",
        indicator="_dimension_match",
    )

    unmatched_mask = result["_dimension_match"].eq("left_only")

    if unmatched_mask.any():
        unmatched_count = int(unmatched_mask.sum())

        unmatched_examples = (
            result.loc[
                unmatched_mask,
                attributes,
            ]
            .drop_duplicates()
            .head(5)
            .to_dict("records")
        )

        raise ValueError(
            f"{unmatched_count} rows could not map "
            f"to {key_name}. "
            f"Examples: {unmatched_examples}"
        )

    return result.drop(columns="_dimension_match")
