"""Project paths and source-schema configuration."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_FILE = PROJECT_ROOT / "data" / "raw" / "customer_support_tickets.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
EXCEPTION_DIR = PROJECT_ROOT / "data" / "exceptions"

OUTPUT_FILE = PROCESSED_DIR / "support_tickets_clean.csv"
QUALITY_FILE = PROCESSED_DIR / "data_quality_summary.json"
DUPLICATE_FILE = EXCEPTION_DIR / "duplicate_ticket_ids.csv"

NA_VALUES = ["", "NA", "N/A", "NULL", "null", "None"]

REQUIRED_SOURCE_COLUMNS = {
    "ticket_id",
    "customer_name",
    "customer_email",
    "customer_age",
    "customer_gender",
    "product_purchased",
    "date_of_purchase",
    "ticket_type",
    "ticket_subject",
    "ticket_description",
    "ticket_status",
    "resolution",
    "ticket_priority",
    "ticket_channel",
    "first_response_time",
    "time_to_resolution",
    "customer_satisfaction_rating",
}

TEXT_COLUMNS = [
    "customer_name",
    "customer_email",
    "product_purchased",
    "ticket_subject",
    "ticket_description",
    "resolution",
]

CATEGORY_COLUMNS = [
    "customer_gender",
    "ticket_type",
    "ticket_status",
    "ticket_priority",
    "ticket_channel",
]
