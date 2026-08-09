"""Reusable text and identifier helpers."""

import hashlib
import re

import pandas as pd


def to_snake_case(value: str) -> str:
    """Convert a source column name to stable snake_case."""
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def normalize_text(series: pd.Series) -> pd.Series:
    """Trim text, collapse whitespace, and retain proper missing values."""
    cleaned = series.astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
    return cleaned.mask(cleaned.eq(""), pd.NA)


def canonical_category(series: pd.Series) -> pd.Series:
    """Standardize category capitalization without filling missing values."""
    return normalize_text(series).str.lower().str.title()


def _has_value(value: object) -> bool:
    """Return True only for a non-missing, non-blank scalar value."""
    return bool(pd.notna(value)) and bool(str(value).strip())


def stable_customer_key(
    email: object,
    customer_name: object,
    ticket_id: object,
) -> str:
    """Create a deterministic pseudonymous customer identifier."""
    if _has_value(email) and _has_value(customer_name):
        normalized_email = str(email).strip().lower()
        normalized_customer_name = str(customer_name).strip().lower()
        token = f"{normalized_email}|{normalized_customer_name}"
    else:
        token = f"missing_identity:{ticket_id}"

    return hashlib.sha256(token.encode("utf-8")).hexdigest()[:16]
