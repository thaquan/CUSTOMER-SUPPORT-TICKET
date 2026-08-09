"""Transformation functions for the customer-support Silver table."""

import pandas as pd

from src.config import CATEGORY_COLUMNS, TEXT_COLUMNS
from src.utils import canonical_category, normalize_text, stable_customer_key, to_snake_case


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with normalized source headers."""
    result = df.copy()
    result.columns = [to_snake_case(column) for column in result.columns]
    return result


def remove_exact_duplicates(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Remove only rows that are identical across every column."""
    duplicate_count = int(df.duplicated().sum())
    return df.drop_duplicates().copy(), duplicate_count


def find_duplicate_ticket_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Return conflicting rows that share the ticket business key."""
    mask = df["ticket_id"].duplicated(keep=False)
    return df.loc[mask].sort_values("ticket_id").copy()


def standardize_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize free text separately from controlled categories."""
    result = df.copy()

    for column in TEXT_COLUMNS:
        result[column] = normalize_text(result[column])

    for column in CATEGORY_COLUMNS:
        result[column] = canonical_category(result[column])

    return result


def clean_age(df: pd.DataFrame) -> pd.DataFrame:
    """Parse age and flag non-numeric or out-of-range source values."""
    result = df.copy()
    raw = result["customer_age"]
    parsed = pd.to_numeric(raw, errors="coerce")

    result["dq_invalid_age"] = raw.notna() & (
        parsed.isna() | ~parsed.between(18, 100)
    )
    result["customer_age"] = parsed.where(
        ~result["dq_invalid_age"]
    ).astype("Int64")
    return result


def clean_csat(df: pd.DataFrame) -> pd.DataFrame:
    """Parse CSAT and accept only the discrete survey scale 1, 2, 3, 4, 5."""
    result = df.copy()
    raw = result["customer_satisfaction_rating"]
    parsed = pd.to_numeric(raw, errors="coerce")
    allowed_values = [1, 2, 3, 4, 5]

    result["dq_invalid_csat"] = raw.notna() & (
        parsed.isna() | ~parsed.isin(allowed_values)
    )
    result["customer_satisfaction_rating"] = parsed.where(
        ~result["dq_invalid_csat"]
    ).astype("Float64")
    return result


def clean_dates_and_times(df: pd.DataFrame) -> pd.DataFrame:
    """Parse source dates/timestamps and derive a validated resolution cycle."""
    result = df.copy()

    purchase_raw = result["date_of_purchase"]
    first_response_raw = result["first_response_time"]
    resolution_raw = result["time_to_resolution"]

    result["date_of_purchase"] = pd.to_datetime(purchase_raw, errors="coerce")
    result["first_response_at"] = pd.to_datetime(
        first_response_raw, errors="coerce"
    )
    result["resolution_at"] = pd.to_datetime(resolution_raw, errors="coerce")

    result["dq_invalid_purchase_date"] = (
        purchase_raw.notna() & result["date_of_purchase"].isna()
    )
    result["dq_invalid_first_response_at"] = (
        first_response_raw.notna() & result["first_response_at"].isna()
    )
    result["dq_invalid_resolution_at"] = (
        resolution_raw.notna() & result["resolution_at"].isna()
    )

    cycle_minutes = (
        result["resolution_at"] - result["first_response_at"]
    ).dt.total_seconds() / 60

    result["dq_negative_resolution_cycle"] = (cycle_minutes < 0).fillna(False)
    result["resolution_cycle_minutes"] = cycle_minutes.where(cycle_minutes >= 0)

    return result.drop(columns=["first_response_time", "time_to_resolution"])


def add_analytical_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add reusable flags, age bands, and a pseudonymous customer key."""
    result = df.copy()

    result["is_closed"] = result["ticket_status"].str.lower().eq("closed")
    result["has_csat"] = result["customer_satisfaction_rating"].notna()
    result["is_low_csat"] = (
        result["customer_satisfaction_rating"].le(2).fillna(False)
    )
    result["customer_age_band"] = pd.cut(
        result["customer_age"],
        bins=[17, 24, 34, 44, 54, 64, 100],
        labels=["18-24", "25-34", "35-44", "45-54", "55-64", "65+"],
    )
    result["customer_key"] = [
        stable_customer_key(email, ticket_id)
        for email, ticket_id in zip(result["customer_email"], result["ticket_id"])
    ]
    return result


def transform_silver(df: pd.DataFrame) -> pd.DataFrame:
    """Apply semantic cleaning and feature engineering in pipeline order."""
    result = standardize_strings(df)
    result = clean_age(result)
    result = clean_csat(result)
    result = clean_dates_and_times(result)
    return add_analytical_features(result)
