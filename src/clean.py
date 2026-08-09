"""Command-line entry point for building the customer-support Silver table."""

import json
from pathlib import Path

import pandas as pd

from src.config import (
    DUPLICATE_FILE,
    NA_VALUES,
    OUTPUT_FILE,
    QUALITY_FILE,
    RAW_FILE,
)
from src.transform import (
    find_duplicate_ticket_rows,
    normalize_column_names,
    remove_exact_duplicates,
    transform_silver,
)
from src.validate import build_quality_summary, validate_silver, validate_source_schema


def run_pipeline(
    raw_file: Path = RAW_FILE,
    output_file: Path = OUTPUT_FILE,
    quality_file: Path = QUALITY_FILE,
    duplicate_file: Path = DUPLICATE_FILE,
) -> tuple[pd.DataFrame, dict[str, int]]:
    """Read raw tickets, build the Silver table, validate it, and save artifacts."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    quality_file.parent.mkdir(parents=True, exist_ok=True)
    duplicate_file.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(raw_file, na_values=NA_VALUES)
    raw_row_count = len(df)
    raw_column_count = len(df.columns)

    df = normalize_column_names(df)
    validate_source_schema(df)
    df, exact_duplicate_count = remove_exact_duplicates(df)

    duplicate_rows = find_duplicate_ticket_rows(df)
    if not duplicate_rows.empty:
        duplicate_rows.to_csv(duplicate_file, index=False, encoding="utf-8")
        raise ValueError(
            f"Conflicting duplicate ticket IDs detected. Inspect {duplicate_file}."
        )

    df = transform_silver(df)
    validate_silver(df)

    summary = dict(
        build_quality_summary(
            df,
            raw_row_count=raw_row_count,
            raw_column_count=raw_column_count,
            exact_duplicate_count=exact_duplicate_count,
            duplicate_ticket_id_rows=len(duplicate_rows),
        )
    )

    with quality_file.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)

    df.to_csv(
        output_file,
        index=False,
        encoding="utf-8",
        date_format="%Y-%m-%d %H:%M:%S",
    )
    return df, summary


def main() -> None:
    """Run the pipeline and print a concise execution report."""
    _, summary = run_pipeline()
    print("Cleaning pipeline completed successfully.")
    print(f"Output: {OUTPUT_FILE}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
