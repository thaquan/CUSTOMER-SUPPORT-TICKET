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


def validate_dimension(
    dimension: pd.DataFrame,
    key_name: str,
    attributes: list[str],
) -> None:
    """Validate a dimension's surrogate key and declared grain."""
    required_columns = {
        key_name,
        *attributes,
    }

    missing_columns = sorted(
        required_columns
        - set(dimension.columns)
    )

    if missing_columns:
        raise ValueError(
            f"{key_name} dimension is missing columns: "
            f"{missing_columns}"
        )

    if dimension.empty:
        raise ValueError(
            f"{key_name} dimension is empty."
        )

    if dimension[key_name].isna().any():
        raise ValueError(
            f"{key_name} dimension contains missing surrogate key values."
        )

    if not dimension[key_name].is_unique:
        raise ValueError(
            f"{key_name} dimension must contain one row per surrogate key."
        )

    if dimension.duplicated(subset=attributes).any():
        raise ValueError(
            f"{key_name} dimension violates its grain: {attributes}"
        )

    missing_attributes = (
        dimension[attributes]
        .isna()
        .sum()
    )

    invalid_attributes = missing_attributes[
        missing_attributes > 0
    ]

    if not invalid_attributes.empty:
        raise ValueError(
            f"{key_name} dimension contains "
            f"missing attributes: "
            f"{invalid_attributes.to_dict()}"
        )


def validate_dimensions(
    dimensions: dict[str, pd.DataFrame],
) -> None:
    """Validate every dimension required by FactTicket."""
    specifications = {
        "customer_profile": {
            "key": "customer_profile_key",
            "attributes": [
                "customer_age",
                "customer_gender",
                "customer_age_band",
            ],
        },
        "product": {
            "key": "product_key",
            "attributes": [
                "product_purchased",
            ],
        },
        "issue": {
            "key": "issue_key",
            "attributes": [
                "ticket_type",
                "ticket_subject",
            ],
        },
        "channel": {
            "key": "channel_key",
            "attributes": [
                "ticket_channel",
            ],
        },
        "priority": {
            "key": "priority_key",
            "attributes": [
                "ticket_priority",
            ],
        },
        "status": {
            "key": "status_key",
            "attributes": [
                "ticket_status",
            ],
        },
        "date": {
            "key": "date_key",
            "attributes": [
                "date",
            ],
        },
    }

    missing_dimensions = sorted(
        set(specifications)
        - set(dimensions)
    )

    if missing_dimensions:
        raise ValueError(
            "Missing required dimensions: "
            f"{missing_dimensions}"
        )

    for name, specification in specifications.items():
        validate_dimension(
            dimension=dimensions[name],
            key_name=specification["key"],
            attributes=specification["attributes"],
        )
