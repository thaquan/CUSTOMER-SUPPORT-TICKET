# Customer Support Analytics - Data Dictionary

## Purpose

This document describes the public Gold, SQL Server, and Power BI analytical model. It excludes the local Silver audit fields `customer_name` and `customer_email` by design.

## Model summary

| Property | Value |
|---|---|
| Fact grain | One row per validated support ticket |
| Fact rows | 8,469 |
| Fact columns | 21 |
| Dimensions | 7 |
| Relationships | 7 many-to-one relationships from `FactTicket` |
| Measures | 35 explicit DAX measures in `_Measures` |
| Storage mode | Import |
| Power BI source | SQL Server `CustomerSupportAnalytics`, schema `analytics` |
| Privacy | Customer name and email excluded; customer analysis uses demographic profiles |

## Relationship map

```text
DimCustomerProfile -- customer_profile_key --+
DimProduct         -- product_key ----------+
DimIssue           -- issue_key ------------+
DimChannel         -- channel_key ----------+--> FactTicket
DimPriority        -- priority_key ---------+
DimStatus          -- status_key -----------+
DimDate            -- date_key -------------+    (purchase_date_key)
```

All relationships are single-direction, many-to-one relationships from the fact table to a unique dimension key.

## FactTicket

Grain: one row per support ticket after Silver cleaning and Gold validation.

| Column | SQL type | Meaning | Notes |
|---|---|---|---|
| `ticket_id` | `INT` | Source business identifier for the ticket | Primary key; hidden in Power BI |
| `customer_profile_key` | `INT` | Customer demographic profile key | FK to `DimCustomerProfile` |
| `product_key` | `INT` | Purchased product key | FK to `DimProduct` |
| `issue_key` | `INT` | Ticket type/subject key | FK to `DimIssue` |
| `channel_key` | `INT` | Support channel key | FK to `DimChannel` |
| `priority_key` | `INT` | Ticket priority key | FK to `DimPriority` |
| `status_key` | `INT` | Ticket status key | FK to `DimStatus` |
| `purchase_date_key` | `INT` | Product purchase date key | FK to `DimDate`; not a ticket-created date |
| `first_response_at` | `DATETIME2(0)` | Recorded first-response timestamp | Nullable |
| `resolution_at` | `DATETIME2(0)` | Recorded resolution timestamp | Nullable |
| `resolution_cycle_minutes` | `DECIMAL(12,2)` | Minutes from first response to resolution | Blank for invalid or negative cycles; not first-response time |
| `customer_satisfaction_rating` | `DECIMAL(2,1)` | Valid source CSAT rating | Nullable; valid values 1-5 |
| `is_closed` | `BIT` | Ticket status is Closed | Technical measure input |
| `has_csat` | `BIT` | A valid CSAT value is present | Technical measure input |
| `is_low_csat` | `BIT` | Valid CSAT is 1 or 2 | Technical measure input |
| `dq_invalid_age` | `BIT` | Customer age failed validation | Quality flag |
| `dq_invalid_csat` | `BIT` | CSAT failed validation | Quality flag |
| `dq_invalid_purchase_date` | `BIT` | Purchase date failed parsing/validation | Quality flag |
| `dq_invalid_first_response_at` | `BIT` | First-response timestamp failed parsing | Quality flag |
| `dq_invalid_resolution_at` | `BIT` | Resolution timestamp failed parsing | Quality flag |
| `dq_negative_resolution_cycle` | `BIT` | Resolution occurs before first response | 1,365 rows in the validated project run |

## Dimensions

### DimCustomerProfile

Grain: one row per unique validated combination of age, gender, and age band. Current row count: 159.

| Column | SQL type | Meaning |
|---|---|---|
| `customer_profile_key` | `INT` | Surrogate primary key |
| `customer_age` | `SMALLINT` | Validated customer age, constrained to 18-100 |
| `customer_gender` | `NVARCHAR(50)` | Standardized gender category |
| `customer_age_band` | `VARCHAR(20)` | Derived reporting band: 18-24, 25-34, 35-44, 45-54, 55-64, or 65+ |

This dimension represents demographic profiles, not unique people. Names and email addresses are excluded.

### DimProduct

Grain: one row per standardized purchased product. Current row count: 42.

| Column | SQL type | Meaning |
|---|---|---|
| `product_key` | `INT` | Surrogate primary key |
| `product_purchased` | `NVARCHAR(255)` | Purchased product associated with the ticket |

Ticket volume by product is support demand, not a defect rate, because product sales volume is unavailable.

### DimIssue

Grain: one row per standardized ticket type and subject combination. Current row count: 80.

| Column | SQL type | Meaning |
|---|---|---|
| `issue_key` | `INT` | Surrogate primary key |
| `ticket_type` | `NVARCHAR(100)` | High-level support-request category |
| `ticket_subject` | `NVARCHAR(255)` | Detailed subject used for issue analysis |

### DimChannel

Grain: one row per standardized support channel. Current row count: 4.

| Column | SQL type | Meaning |
|---|---|---|
| `channel_key` | `INT` | Surrogate primary key |
| `ticket_channel` | `NVARCHAR(100)` | Channel through which support was contacted |

### DimPriority

Grain: one row per standardized ticket priority. Current row count: 4.

| Column | SQL type | Meaning |
|---|---|---|
| `priority_key` | `INT` | Surrogate primary key |
| `ticket_priority` | `NVARCHAR(50)` | Operational urgency: Critical, High, Medium, or Low |

### DimStatus

Grain: one row per standardized ticket status. Current row count: 3.

| Column | SQL type | Meaning |
|---|---|---|
| `status_key` | `INT` | Surrogate primary key |
| `ticket_status` | `NVARCHAR(100)` | Current lifecycle state of the ticket |

### DimDate

Grain: one row per continuous calendar date. Current row count: 730.

| Column | SQL type | Meaning |
|---|---|---|
| `date_key` | `INT` | Integer surrogate key |
| `date` | `DATE` | Product purchase date |
| `day` | `TINYINT` | Day of month |
| `day_of_week_number` | `TINYINT` | Numeric weekday sort order |
| `day_name` | `VARCHAR(20)` | Weekday label |
| `month_number` | `TINYINT` | Numeric month sort order |
| `month_name` | `VARCHAR(20)` | Month label |
| `quarter` | `CHAR(2)` | Q1-Q4 |
| `year` | `SMALLINT` | Calendar year |
| `year_month` | `CHAR(7)` | Chronological year-month label |
| `is_weekend` | `BIT` | Date falls on Saturday or Sunday |

The Power BI model also defines a `Purchase Date` hierarchy: Year > Quarter > Month > Date. This dimension must not be used to claim ticket-arrival trends because the source has no `ticket_created_at` field.

## DAX measure catalog

### Ticket Volume

| Measure | Logic | Interpretation |
|---|---|---|
| `Total Tickets` | `COUNTROWS(FactTicket)` | Ticket count in the current filter context |
| `Closed Tickets` | Total tickets filtered to `is_closed = TRUE` | Closed workload |
| `Backlog Tickets` | Total Tickets - Closed Tickets | Non-closed workload |
| `Resolution Rate` | Closed Tickets / Total Tickets | Share of tickets currently closed |
| `Critical High Backlog` | Backlog filtered to Critical or High priority | Higher-urgency unresolved workload |
| `Backlog Rate` | Backlog Tickets / Total Tickets | Share of tickets not closed |
| `Critical High Share of Backlog` | Critical High Backlog / Backlog Tickets | Urgent share of unresolved workload |

### Customer Experience

| Measure | Logic | Interpretation |
|---|---|---|
| `CSAT Responses` | Count of nonblank valid CSAT values | Survey sample size |
| `CSAT Response Rate` | CSAT Responses / Total Tickets | Survey coverage across all tickets |
| `Average CSAT` | Average valid rating | Mean score on the 1-5 scale |
| `Low CSAT Tickets` | Tickets where valid CSAT is 1 or 2 | Count of low ratings |
| `Low CSAT Rate` | Low CSAT Tickets / CSAT Responses | Low-score rate among respondents, not all tickets |

### Resolution Cycle and Data Quality

| Measure | Logic | Interpretation |
|---|---|---|
| `Valid Resolution Cycles` | Count of nonblank `resolution_cycle_minutes` | Validated duration sample size |
| `Average Resolution Cycle Minutes` | Average validated cycle | Mean first-response-to-resolution duration |
| `Median Resolution Cycle Minutes` | Median validated cycle | Robust typical duration |
| `Valid Resolution Cycle Rate` | Valid Resolution Cycles / Closed Tickets | Duration coverage among closed tickets |
| `Negative Resolution Cycle Rows` | Tickets flagged with a negative cycle | Invalid temporal records excluded from duration KPIs |
| `Negative Resolution Cycle Rate` | Negative cycle rows / Closed Tickets | Data-quality issue rate among closed tickets |

### Purchase-cohort comparison

| Measure | Logic | Interpretation |
|---|---|---|
| `Latest Purchase Cohort Year` | Maximum selected purchase year | Current comparison cohort |
| `Latest Cohort Total Tickets` | Total tickets for latest selected purchase year | Latest purchase-cohort workload |
| `Prior Cohort Total Tickets` | Total tickets for the previous purchase year | Comparison workload |
| `Total Tickets Cohort YoY %` | Change from prior to latest total tickets | Purchase-cohort change, not ticket-arrival growth |
| `Latest Cohort Backlog Tickets` | Backlog for latest purchase year | Latest cohort unresolved workload |
| `Prior Cohort Backlog Tickets` | Backlog for prior purchase year | Comparison unresolved workload |
| `Backlog Tickets Cohort YoY %` | Change from prior to latest backlog | Cohort backlog change; lower is better |
| `Latest Cohort Backlog Rate` | Latest cohort backlog / total | Latest cohort backlog share |
| `Latest Cohort Resolution Rate` | Resolution rate for latest purchase year | Latest cohort closure performance |
| `Prior Cohort Resolution Rate` | Resolution rate for prior purchase year | Comparison closure performance |
| `Resolution Rate Cohort Delta pp` | Latest rate - prior rate, multiplied by 100 | Percentage-point change; higher is better |
| `Latest Cohort Average CSAT` | Average CSAT for latest purchase year | Latest cohort satisfaction |
| `Prior Cohort Average CSAT` | Average CSAT for prior purchase year | Comparison satisfaction |
| `Average CSAT Cohort Delta` | Latest CSAT - prior CSAT | Change in score points; higher is better |
| `Latest Cohort Median Resolution Cycle Minutes` | Median valid cycle for latest purchase year | Latest cohort typical cycle |
| `Prior Cohort Median Resolution Cycle Minutes` | Median valid cycle for prior purchase year | Comparison typical cycle |
| `Median Resolution Cycle Cohort YoY %` | Change from prior to latest median cycle | Cohort duration change; lower is better |

## Quality rules

- Ticket IDs must be unique and non-null at the fact grain.
- Every fact foreign key must resolve to exactly one dimension row.
- Ages must be whole numbers between 18 and 100.
- CSAT must be an integer-equivalent value from 1 to 5 or blank.
- Negative resolution cycles are flagged and excluded, never converted with `abs()`.
- `resolution_cycle_minutes` is nonnegative or blank.
- Customer name and email may exist only in the local Silver audit layer.
- Product ticket volume must not be interpreted as a product defect rate.
- Channel and segment comparisons are descriptive associations, not causal effects.

## Validation evidence

The repository includes:

- 21 Python unit/integration tests;
- 34 SQL Server model-validation checks;
- `data/processed/data_quality_summary.json` for Silver evidence;
- `data/gold/gold_quality_summary.json` for Gold evidence;
- PBIR validation and rendered screenshots for all five report pages.
