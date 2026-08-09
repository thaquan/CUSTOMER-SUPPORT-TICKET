"""Schema and data-quality checks for the Silver pipeline."""

from collections.abc import Mapping

import pandas as pd

from src.config import REQUIRED_SOURCE_COLUMNS


def validate_source_schema(df: pd.DataFrame) -> None:
    """Fail early when the raw dataset does not contain the expected fields."""
    missing_columns = sorted(REQUIRED_SOURCE_COLUMNS - set(df.columns))
    if missing_columns:
        raise ValueError(f"Missing required source columns: {missing_columns}")


def validate_silver(df: pd.DataFrame) -> None:
    """Enforce the business-key and clean-value invariants of the Silver table."""
    if df["ticket_id"].isna().any():
        raise ValueError("ticket_id contains missing values.")

    if not df["ticket_id"].is_unique:
        raise ValueError("ticket_id must be unique in the Silver table.")

    clean_csat = df["customer_satisfaction_rating"].dropna()
    if not clean_csat.isin([1, 2, 3, 4, 5]).all():
        raise ValueError("Clean CSAT values must belong to the scale 1-5.")


def build_quality_summary(
    df: pd.DataFrame,
    *,
    raw_row_count: int,
    raw_column_count: int,
    exact_duplicate_count: int,
    duplicate_ticket_id_rows: int,
) -> Mapping[str, int]:
    """Build auditable row counts for the pipeline output."""
    return {
        "raw_rows": raw_row_count,
        "raw_columns": raw_column_count,
        "clean_rows": len(df),
        "clean_columns": len(df.columns),
        "exact_duplicates_removed": exact_duplicate_count,
        "duplicate_ticket_id_rows": duplicate_ticket_id_rows,
        "invalid_age_rows": int(df["dq_invalid_age"].sum()),
        "invalid_csat_rows": int(df["dq_invalid_csat"].sum()),
        "invalid_purchase_date_rows": int(df["dq_invalid_purchase_date"].sum()),
        "invalid_first_response_at_rows": int(
            df["dq_invalid_first_response_at"].sum()
        ),
        "invalid_resolution_at_rows": int(df["dq_invalid_resolution_at"].sum()),
        "negative_resolution_cycle_rows": int(
            df["dq_negative_resolution_cycle"].sum()
        ),
    }
