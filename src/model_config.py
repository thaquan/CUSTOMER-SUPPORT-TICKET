"""Output paths for the Gold dimensional model."""

from src.config import (
    OUTPUT_FILE as SILVER_FILE,
    PROJECT_ROOT,
)

GOLD_DIR = PROJECT_ROOT / "data" / "gold"

FACT_TICKET_FILE = GOLD_DIR / "fact_ticket.csv"

DIM_CUSTOMER_PROFILE_FILE = (
    GOLD_DIR / "dim_customer_profile.csv"
)

DIM_PRODUCT_FILE = GOLD_DIR / "dim_product.csv"
DIM_ISSUE_FILE = GOLD_DIR / "dim_issue.csv"
DIM_CHANNEL_FILE = GOLD_DIR / "dim_channel.csv"
DIM_PRIORITY_FILE = GOLD_DIR / "dim_priority.csv"
DIM_STATUS_FILE = GOLD_DIR / "dim_status.csv"
DIM_DATE_FILE = GOLD_DIR / "dim_date.csv"
GOLD_QUALITY_FILE = (
    GOLD_DIR / "gold_quality_summary.json"
)

DIMENSION_FILES = {
    "customer_profile": DIM_CUSTOMER_PROFILE_FILE,
    "product": DIM_PRODUCT_FILE,
    "issue": DIM_ISSUE_FILE,
    "channel": DIM_CHANNEL_FILE,
    "priority": DIM_PRIORITY_FILE,
    "status": DIM_STATUS_FILE,
    "date": DIM_DATE_FILE,
}