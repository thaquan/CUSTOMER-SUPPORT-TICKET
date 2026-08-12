"""Quality gates for the Gold dimensional model."""

import pandas as pd


def validate_fact_ticket(
    fact: pd.DataFrame,
    expected_row_count: int,
) -> None:
    """Validate FactTicket grain and required foreign keys."""

    if len(fact) != expected_row_count:
        raise ValueError(
            "FactTicket row count does not match Silver. "
            f"Expected {expected_row_count}, received {len(fact)}."
        )

    if fact["ticket_id"].isna().any():
        raise ValueError(
            "FactTicket contains missing ticket_id values."
        )

    if not fact["ticket_id"].is_unique:
        raise ValueError(
            "FactTicket must contain one row per ticket_id."
        )

    foreign_keys = [
        "customer_profile_key",
        "product_key",
        "issue_key",
        "channel_key",
        "priority_key",
        "status_key",
        "purchase_date_key",
    ]

    missing_foreign_keys = (
        fact[foreign_keys]
        .isna()
        .sum()
    )

    invalid_foreign_keys = (
        missing_foreign_keys[
            missing_foreign_keys > 0
        ]
    )

    if not invalid_foreign_keys.empty:
        raise ValueError(
            "FactTicket contains missing foreign keys: "
            f"{invalid_foreign_keys.to_dict()}"
        )

    forbidden_columns = {
        "customer_name",
        "customer_email",
        "customer_key",
        "ticket_description",
        "resolution",
    }

    present_forbidden_columns = sorted(
        forbidden_columns
        & set(fact.columns)
    )

    if present_forbidden_columns:
        raise ValueError(
            "FactTicket contains forbidden public fields: "
            f"{present_forbidden_columns}"
        )
