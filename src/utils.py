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
    return (
        series.astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .replace({"": pd.NA})
    )


def canonical_category(series: pd.Series) -> pd.Series:
    """Standardize category capitalization without filling missing values."""
    return normalize_text(series).str.lower().str.title()


def stable_customer_key(email: object, ticket_id: object) -> str:
    """Create a deterministic pseudonymous customer identifier."""
    if pd.notna(email):
        token = str(email).strip().lower()
    else:
        token = f"missing_email:{ticket_id}"

    return hashlib.sha256(token.encode("utf-8")).hexdigest()[:16]
