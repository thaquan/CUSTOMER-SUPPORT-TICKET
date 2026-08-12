"""Builders for the Gold dimensional model."""

import pandas as pd

from src.model_config import SILVER_FILE
from src.model_utils import build_dimension


def load_silver() -> pd.DataFrame:
    """Load the validated Silver ticket table for Gold modeling."""
    return pd.read_csv(
        SILVER_FILE,
        parse_dates=[
            "date_of_purchase",
            "first_response_at",
            "resolution_at",
        ],
    )


def build_product_dimension(silver: pd.DataFrame) -> pd.DataFrame:
    """Build one row per purchased product."""
    return build_dimension(
        source=silver,
        attributes=["product_purchased"],
        key_name="product_key",
    )


def build_issue_dimension(silver: pd.DataFrame) -> pd.DataFrame:
    """Build one row per ticket-type and ticket-subject combination."""
    return build_dimension(
        source=silver,
        attributes=["ticket_type", "ticket_subject"],
        key_name="issue_key",
    )


def build_channel_dimension(silver: pd.DataFrame) -> pd.DataFrame:
    """Build one row per support channel."""
    return build_dimension(
        source=silver,
        attributes=["ticket_channel"],
        key_name="channel_key",
    )


def build_priority_dimension(silver: pd.DataFrame) -> pd.DataFrame:
    """Build one row per ticket priority."""
    return build_dimension(
        source=silver,
        attributes=["ticket_priority"],
        key_name="priority_key",
    )


def build_status_dimension(silver: pd.DataFrame) -> pd.DataFrame:
    """Build one row per ticket status."""
    return build_dimension(
        source=silver,
        attributes=["ticket_status"],
        key_name="status_key",
    )


def build_customer_profile_dimension(silver: pd.DataFrame) -> pd.DataFrame:
    """Build one row per analytical demographic profile."""
    return build_dimension(
        source=silver,
        attributes=[
            "customer_age",
            "customer_gender",
            "customer_age_band",
        ],
        key_name="customer_profile_key",
    )


def build_business_dimensions(
    silver: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Build all non-date dimensions used by FactTicket."""
    return {
        "customer_profile": build_customer_profile_dimension(silver),
        "product": build_product_dimension(silver),
        "issue": build_issue_dimension(silver),
        "channel": build_channel_dimension(silver),
        "priority": build_priority_dimension(silver),
        "status": build_status_dimension(silver),
    }
