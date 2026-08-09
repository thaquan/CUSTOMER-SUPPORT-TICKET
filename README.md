# E-commerce Customer Support Analytics

An end-to-end Data Analyst portfolio project that transforms raw customer-support ticket data into a validated analytical dataset, then prepares it for SQL dimensional modeling and Power BI reporting.

## Business Context

This project assumes the role of a Data Analyst supporting the Customer Experience team of an online technology retailer. The analysis is designed to answer questions such as:

- How large is the current support workload and backlog?
- Which ticket types, subjects, products, priorities, and channels generate the most demand?
- Where are low customer-satisfaction scores concentrated?
- Which operational segments require further investigation?

The project does not claim that the data belongs to a real retailer or marketplace.

## Dataset

- Source: [Customer Support Ticket Dataset by Suraj on Kaggle](https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset)
- License: CC0 — Public Domain
- Kaggle Usability: 10.00
- Grain: one row per support ticket
- Raw size used by the pipeline: 8,469 rows and 17 columns

The CSV files are intentionally excluded from this repository. Download `customer_support_tickets.csv` from Kaggle and place it at:

```text
data/raw/customer_support_tickets.csv
```

## Architecture

```text
Kaggle CSV
    ↓
Bronze: immutable raw CSV
    ↓
Python cleaning and validation
    ↓
Silver: support_tickets_clean.csv
    ↓
Gold: dimensional model (planned)
    ↓
SQL analytical layer (planned)
    ↓
Power BI semantic model and report (planned)
```

## Current Project Structure

```text
CUSTOMER-SUPPORT-TICKET/
├── data/
│   ├── raw/                  # Local raw CSV; not committed
│   ├── processed/            # Generated Silver CSV; not committed
│   │   └── data_quality_summary.json
│   └── exceptions/           # Conflicting records; not committed
├── src/
│   ├── clean.py              # Pipeline entry point and file I/O
│   ├── config.py             # Paths, expected schema, column groups
│   ├── transform.py          # Cleaning and feature engineering
│   ├── utils.py              # Reusable text and key helpers
│   └── validate.py           # Source and Silver quality gates
├── tests/
│   └── test_cleaning.py
├── .gitignore
├── requirements.txt
└── README.md
```

## Silver Pipeline

The Python pipeline performs:

- column-name normalization to `snake_case`;
- exact-duplicate removal;
- conflicting `ticket_id` detection and exception handling;
- whitespace and categorical-value standardization;
- age and CSAT type validation;
- date and timestamp parsing;
- invalid and negative temporal-cycle flags;
- analytical flags such as `is_closed`, `has_csat`, and `is_low_csat`;
- customer age bands;
- deterministic pseudonymous `customer_key` creation;
- pre-export validation gates;
- CSV and JSON quality-report generation.

## Data Quality Results

The current pipeline run produced:

| Check | Result |
|---|---:|
| Raw rows | 8,469 |
| Clean rows | 8,469 |
| Clean columns | 29 |
| Exact duplicates removed | 0 |
| Duplicate ticket IDs | 0 |
| Invalid ages | 0 |
| Invalid CSAT values | 0 |
| Invalid purchase dates | 0 |
| Invalid first-response timestamps | 0 |
| Invalid resolution timestamps | 0 |
| Negative resolution cycles | 1,365 |

Negative resolution cycles are not converted with `abs()` or silently corrected. They remain visible through `dq_negative_resolution_cycle`, while `resolution_cycle_minutes` is left missing for those records.

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run the Pipeline

Run from the repository root:

```powershell
python -m src.clean
```

Generated artifacts:

```text
data/processed/support_tickets_clean.csv
data/processed/data_quality_summary.json
```

## Run the Tests

```powershell
python -m unittest discover -s tests -v
```

The test suite covers helper functions, exact duplicates, invalid fractional CSAT, negative resolution cycles, and an end-to-end CSV/JSON integration test.

## Important Limitations

- The published schema has no explicit `ticket_created_at` field.
- `Date of Purchase` must not be interpreted as ticket creation date.
- The two operational time fields contain timestamps in the downloaded file, despite their source labels suggesting durations.
- `resolution_cycle_minutes` measures the interval from first response to resolution; it is not first-response duration.
- The dataset has no agent, SLA target, order revenue, or explicit support-cost fields.
- Customer name and email are retained only in the local Silver audit layer and must not be included in a public Power BI model.

## Roadmap

- [x] Raw data audit
- [x] Reproducible Python Silver pipeline
- [x] Automated unit and integration tests
- [x] Data-quality summary
- [ ] Gold star schema
- [ ] PostgreSQL tables and analytical queries
- [ ] Power BI semantic model and DAX measures
- [ ] Multi-page Power BI report
- [ ] Power BI Service deployment

