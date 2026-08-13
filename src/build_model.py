"""Build, validate, and save the Gold dimensional model."""

import json

import pandas as pd

from src.model_config import (
    DIMENSION_FILES,
    FACT_TICKET_FILE,
    GOLD_DIR,
    GOLD_QUALITY_FILE,
    SILVER_FILE,
)
from src.model_utils import (
    attach_dimension_key,
    build_dimension,
)

from src.validate_model import (
    validate_dimensions,
    validate_fact_ticket,
)


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


def build_date_dimension(
    silver: pd.DataFrame,
) -> pd.DataFrame:
    """Build a continuous calendar covering all valid purchase dates."""
    purchase_dates = (
        pd.to_datetime(
            silver["date_of_purchase"],
            errors="coerce",
        )
        .dropna()
        .dt.normalize()
    )

    if purchase_dates.empty:
        raise ValueError(
            "Cannot build DimDate because "
            "date_of_purchase has no valid dates."
        )

    calendar_dates = pd.date_range(
        start=purchase_dates.min(),
        end=purchase_dates.max(),
        freq="D",
    )

    dimension = pd.DataFrame(
        {
            "date": calendar_dates,
        }
    )

    dimension["date_key"] = (
        dimension["date"]
        .dt.strftime("%Y%m%d")
        .astype("int64")
    )

    dimension["day"] = dimension["date"].dt.day

    dimension["day_of_week_number"] = (
        dimension["date"].dt.dayofweek + 1
    )

    day_name = {
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday",
    }

    dimension["day_name"] = dimension["day_of_week_number"].map(day_name)

    dimension["month_number"] = dimension["date"].dt.month

    month_name = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    }

    dimension["month_name"] = dimension["month_number"].map(month_name)

    dimension["quarter"] = (
        "Q"
        + dimension["date"]
        .dt.quarter
        .astype("string")
    )

    dimension["year"] = dimension["date"].dt.year

    dimension["year_month"] = (
        dimension["date"]
        .dt.strftime("%Y-%m")
    )

    dimension["is_weekend"] = (
        dimension["day_of_week_number"]
        .isin([6, 7])
    )

    dimension = dimension[
        [
            "date_key",
            "date",
            "day",
            "day_of_week_number",
            "day_name",
            "month_number",
            "month_name",
            "quarter",
            "year",
            "year_month",
            "is_weekend",
        ]
    ]

    return dimension


def build_all_dimensions(
    silver: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Build all dimensions used by FactTicket."""
    dimensions = build_business_dimensions(silver)

    dimensions["date"] = build_date_dimension(silver)

    validate_dimensions(dimensions)

    return dimensions


def build_fact_ticket(
    silver: pd.DataFrame,
    dimensions: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Build one FactTicket row per unique Silver ticket."""
    fact = silver.copy()

    fact = attach_dimension_key(
        source=fact,
        dimension=dimensions["customer_profile"],
        attributes=[
            "customer_age",
            "customer_gender",
            "customer_age_band",
        ],
        key_name="customer_profile_key",
    )

    fact = attach_dimension_key(
        source=fact,
        dimension=dimensions["product"],
        attributes=["product_purchased"],
        key_name="product_key",
    )

    fact = attach_dimension_key(
        source=fact,
        dimension=dimensions["issue"],
        attributes=["ticket_type", "ticket_subject"],
        key_name="issue_key",
    )

    fact = attach_dimension_key(
        source=fact,
        dimension=dimensions["channel"],
        attributes=["ticket_channel"],
        key_name="channel_key",
    )

    fact = attach_dimension_key(
        source=fact,
        dimension=dimensions["priority"],
        attributes=["ticket_priority"],
        key_name="priority_key",
    )

    fact = attach_dimension_key(
        source=fact,
        dimension=dimensions["status"],
        attributes=["ticket_status"],
        key_name="status_key",
    )

    purchase_date_dimension = (
        dimensions["date"]
        .rename(
            columns={
                "date_key": "purchase_date_key",
                "date": "date_of_purchase",
            }
        )
    )

    fact = attach_dimension_key(
        source=fact,
        dimension=purchase_date_dimension,
        attributes=["date_of_purchase"],
        key_name="purchase_date_key",
    )

    fact_columns = [
        "ticket_id",
        "customer_profile_key",
        "product_key",
        "issue_key",
        "channel_key",
        "priority_key",
        "status_key",
        "purchase_date_key",
        "first_response_at",
        "resolution_at",
        "resolution_cycle_minutes",
        "customer_satisfaction_rating",
        "is_closed",
        "has_csat",
        "is_low_csat",
        "dq_invalid_age",
        "dq_invalid_csat",
        "dq_invalid_purchase_date",
        "dq_invalid_first_response_at",
        "dq_invalid_resolution_at",
        "dq_negative_resolution_cycle",
    ]

    fact = fact[fact_columns].copy()

    validate_fact_ticket(
        fact=fact,
        expected_row_count=len(silver),
    )

    return fact


def build_gold_quality_summary(
    silver: pd.DataFrame,
    fact: pd.DataFrame,
    dimensions: dict[str, pd.DataFrame],
) -> dict[str, object]:
    """Build an auditable summary of the generated Gold model."""
    foreign_keys = [
        "customer_profile_key",
        "product_key",
        "issue_key",
        "channel_key",
        "priority_key",
        "status_key",
        "purchase_date_key",
    ]

    return {
        "silver_rows": len(silver),
        "fact_ticket_rows": len(fact),
        "fact_ticket_columns": len(fact.columns),
        "unique_ticket_ids": int(fact["ticket_id"].nunique()),
        "missing_foreign_keys": int(
            fact[foreign_keys]
            .isna()
            .sum()
            .sum()
        ),
        "dimension_count": len(dimensions),
        "dimension_rows": {
            name: len(dimension)
            for name, dimension
            in dimensions.items()
        },
        "negative_resolution_cycle_rows": int(
            fact[
                "dq_negative_resolution_cycle"
            ].sum()
        ),
    }


def save_gold_model(
    fact: pd.DataFrame,
    dimensions: dict[str, pd.DataFrame],
    quality_summary: dict[str, object],
) -> None:
    """Write validated Gold tables and their quality summary."""
    GOLD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    fact.to_csv(
        FACT_TICKET_FILE,
        index=False,
        encoding="utf-8",
        date_format="%Y-%m-%d %H:%M:%S",
    )

    for name, dimension in dimensions.items():
        output_file = DIMENSION_FILES[name]

        dimension.to_csv(
            output_file,
            index=False,
            encoding="utf-8",
            date_format="%Y-%m-%d",
        )

    with GOLD_QUALITY_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            quality_summary,
            file,
            indent=2,
            ensure_ascii=False,
        )


def run_gold_pipeline() -> dict[str, object]:
    """Build, validate, and save the complete Gold model."""

    silver = load_silver()

    dimensions = build_all_dimensions(silver)

    fact = build_fact_ticket(
        silver=silver,
        dimensions=dimensions,
    )
    quality_summary = build_gold_quality_summary(
        silver=silver,
        fact=fact,
        dimensions=dimensions,
    )

    save_gold_model(
        fact=fact,
        dimensions=dimensions,
        quality_summary=quality_summary,
    )

    return quality_summary


def main() -> None:
    """Run the Gold pipeline and print its quality report."""
    quality_summary = run_gold_pipeline()

    print("Gold pipeline completed successfully.")

    print(f"Output directory: {GOLD_DIR}")

    print(
        json.dumps(
            quality_summary,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
