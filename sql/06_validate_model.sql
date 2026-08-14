-- Validate the typed SQL Server analytics model without changing its data.
USE CustomerSupportAnalytics;
GO

SET NOCOUNT ON;
GO

DROP TABLE IF EXISTS #validation_results;

CREATE TABLE #validation_results (
    check_group VARCHAR(50) NOT NULL,
    check_name VARCHAR(150) NOT NULL,
    failed_rows BIGINT NOT NULL,
    details NVARCHAR(500) NULL
);

-- Reconcile every analytics table with its staging source.
DECLARE @row_counts TABLE (
    table_name VARCHAR(100) NOT NULL,
    staging_count BIGINT NOT NULL,
    analytics_count BIGINT NOT NULL
);

INSERT INTO @row_counts (table_name, staging_count, analytics_count)
SELECT
    'fact_ticket',
    (SELECT COUNT_BIG(*) FROM staging.fact_ticket),
    (SELECT COUNT_BIG(*) FROM analytics.fact_ticket)
UNION ALL
SELECT
    'dim_customer_profile',
    (SELECT COUNT_BIG(*) FROM staging.dim_customer_profile),
    (SELECT COUNT_BIG(*) FROM analytics.dim_customer_profile)
UNION ALL
SELECT
    'dim_product',
    (SELECT COUNT_BIG(*) FROM staging.dim_product),
    (SELECT COUNT_BIG(*) FROM analytics.dim_product)
UNION ALL
SELECT
    'dim_issue',
    (SELECT COUNT_BIG(*) FROM staging.dim_issue),
    (SELECT COUNT_BIG(*) FROM analytics.dim_issue)
UNION ALL
SELECT
    'dim_channel',
    (SELECT COUNT_BIG(*) FROM staging.dim_channel),
    (SELECT COUNT_BIG(*) FROM analytics.dim_channel)
UNION ALL
SELECT
    'dim_priority',
    (SELECT COUNT_BIG(*) FROM staging.dim_priority),
    (SELECT COUNT_BIG(*) FROM analytics.dim_priority)
UNION ALL
SELECT
    'dim_status',
    (SELECT COUNT_BIG(*) FROM staging.dim_status),
    (SELECT COUNT_BIG(*) FROM analytics.dim_status)
UNION ALL
SELECT
    'dim_date',
    (SELECT COUNT_BIG(*) FROM staging.dim_date),
    (SELECT COUNT_BIG(*) FROM analytics.dim_date);

INSERT INTO #validation_results (
    check_group,
    check_name,
    failed_rows,
    details
)
SELECT
    'row_count',
    CONCAT(table_name, '_matches_staging'),
    CASE WHEN staging_count = analytics_count THEN 0 ELSE 1 END,
    CONCAT('staging=', staging_count, '; analytics=', analytics_count)
FROM @row_counts;

INSERT INTO #validation_results
SELECT
    'row_count',
    'fact_ticket_is_not_empty',
    CASE WHEN COUNT_BIG(*) > 0 THEN 0 ELSE 1 END,
    CONCAT('analytics rows=', COUNT_BIG(*))
FROM analytics.fact_ticket;

-- Primary keys must remain unique even if constraints change later.
INSERT INTO #validation_results
SELECT
    'uniqueness',
    'duplicate_ticket_id',
    COUNT_BIG(*),
    'ticket_id must uniquely identify one support ticket'
FROM (
    SELECT ticket_id
    FROM analytics.fact_ticket
    GROUP BY ticket_id
    HAVING COUNT(*) > 1
) AS duplicates;

INSERT INTO #validation_results
SELECT
    'uniqueness',
    'duplicate_customer_profile_key',
    COUNT_BIG(*),
    'customer_profile_key must be unique'
FROM (
    SELECT customer_profile_key
    FROM analytics.dim_customer_profile
    GROUP BY customer_profile_key
    HAVING COUNT(*) > 1
) AS duplicates;

INSERT INTO #validation_results
SELECT
    'uniqueness',
    'duplicate_product_key',
    COUNT_BIG(*),
    'product_key must be unique'
FROM (
    SELECT product_key
    FROM analytics.dim_product
    GROUP BY product_key
    HAVING COUNT(*) > 1
) AS duplicates;

INSERT INTO #validation_results
SELECT
    'uniqueness',
    'duplicate_issue_key',
    COUNT_BIG(*),
    'issue_key must be unique'
FROM (
    SELECT issue_key
    FROM analytics.dim_issue
    GROUP BY issue_key
    HAVING COUNT(*) > 1
) AS duplicates;

INSERT INTO #validation_results
SELECT
    'uniqueness',
    'duplicate_channel_key',
    COUNT_BIG(*),
    'channel_key must be unique'
FROM (
    SELECT channel_key
    FROM analytics.dim_channel
    GROUP BY channel_key
    HAVING COUNT(*) > 1
) AS duplicates;

INSERT INTO #validation_results
SELECT
    'uniqueness',
    'duplicate_priority_key',
    COUNT_BIG(*),
    'priority_key must be unique'
FROM (
    SELECT priority_key
    FROM analytics.dim_priority
    GROUP BY priority_key
    HAVING COUNT(*) > 1
) AS duplicates;

INSERT INTO #validation_results
SELECT
    'uniqueness',
    'duplicate_status_key',
    COUNT_BIG(*),
    'status_key must be unique'
FROM (
    SELECT status_key
    FROM analytics.dim_status
    GROUP BY status_key
    HAVING COUNT(*) > 1
) AS duplicates;

INSERT INTO #validation_results
SELECT
    'uniqueness',
    'duplicate_date_key',
    COUNT_BIG(*),
    'date_key must be unique'
FROM (
    SELECT date_key
    FROM analytics.dim_date
    GROUP BY date_key
    HAVING COUNT(*) > 1
) AS duplicates;

-- Every FactTicket foreign key must resolve to one dimension row.
INSERT INTO #validation_results
SELECT
    'relationship',
    'orphan_customer_profile_key',
    COUNT_BIG(*),
    'Every fact customer_profile_key must exist in dim_customer_profile'
FROM analytics.fact_ticket AS fact
LEFT JOIN analytics.dim_customer_profile AS dim
    ON fact.customer_profile_key = dim.customer_profile_key
WHERE dim.customer_profile_key IS NULL;

INSERT INTO #validation_results
SELECT
    'relationship',
    'orphan_product_key',
    COUNT_BIG(*),
    'Every fact product_key must exist in dim_product'
FROM analytics.fact_ticket AS fact
LEFT JOIN analytics.dim_product AS dim
    ON fact.product_key = dim.product_key
WHERE dim.product_key IS NULL;

INSERT INTO #validation_results
SELECT
    'relationship',
    'orphan_issue_key',
    COUNT_BIG(*),
    'Every fact issue_key must exist in dim_issue'
FROM analytics.fact_ticket AS fact
LEFT JOIN analytics.dim_issue AS dim
    ON fact.issue_key = dim.issue_key
WHERE dim.issue_key IS NULL;

INSERT INTO #validation_results
SELECT
    'relationship',
    'orphan_channel_key',
    COUNT_BIG(*),
    'Every fact channel_key must exist in dim_channel'
FROM analytics.fact_ticket AS fact
LEFT JOIN analytics.dim_channel AS dim
    ON fact.channel_key = dim.channel_key
WHERE dim.channel_key IS NULL;

INSERT INTO #validation_results
SELECT
    'relationship',
    'orphan_priority_key',
    COUNT_BIG(*),
    'Every fact priority_key must exist in dim_priority'
FROM analytics.fact_ticket AS fact
LEFT JOIN analytics.dim_priority AS dim
    ON fact.priority_key = dim.priority_key
WHERE dim.priority_key IS NULL;

INSERT INTO #validation_results
SELECT
    'relationship',
    'orphan_status_key',
    COUNT_BIG(*),
    'Every fact status_key must exist in dim_status'
FROM analytics.fact_ticket AS fact
LEFT JOIN analytics.dim_status AS dim
    ON fact.status_key = dim.status_key
WHERE dim.status_key IS NULL;

INSERT INTO #validation_results
SELECT
    'relationship',
    'orphan_purchase_date_key',
    COUNT_BIG(*),
    'Every fact purchase_date_key must exist in dim_date'
FROM analytics.fact_ticket AS fact
LEFT JOIN analytics.dim_date AS dim
    ON fact.purchase_date_key = dim.date_key
WHERE dim.date_key IS NULL;

-- Validate analytical flags and metric ranges against business definitions.
INSERT INTO #validation_results
SELECT
    'business_rule',
    'invalid_csat_range',
    COUNT_BIG(*),
    'CSAT must be NULL or one of 1, 2, 3, 4, 5'
FROM analytics.fact_ticket
WHERE customer_satisfaction_rating IS NOT NULL
  AND customer_satisfaction_rating NOT IN (1, 2, 3, 4, 5);

INSERT INTO #validation_results
SELECT
    'business_rule',
    'inconsistent_has_csat',
    COUNT_BIG(*),
    'has_csat must indicate whether a CSAT value exists'
FROM analytics.fact_ticket
WHERE has_csat <>
    CASE
        WHEN customer_satisfaction_rating IS NOT NULL THEN 1
        ELSE 0
    END;

INSERT INTO #validation_results
SELECT
    'business_rule',
    'inconsistent_low_csat',
    COUNT_BIG(*),
    'is_low_csat must equal 1 only when CSAT is 1 or 2'
FROM analytics.fact_ticket
WHERE is_low_csat <>
    CASE
        WHEN customer_satisfaction_rating <= 2 THEN 1
        ELSE 0
    END;

INSERT INTO #validation_results
SELECT
    'business_rule',
    'inconsistent_closed_flag',
    COUNT_BIG(*),
    'is_closed must agree with the Closed ticket status'
FROM analytics.fact_ticket AS fact
INNER JOIN analytics.dim_status AS status
    ON fact.status_key = status.status_key
WHERE fact.is_closed <>
    CASE
        WHEN LOWER(status.ticket_status) = 'closed' THEN 1
        ELSE 0
    END;

INSERT INTO #validation_results
SELECT
    'business_rule',
    'negative_resolution_cycle_value',
    COUNT_BIG(*),
    'resolution_cycle_minutes must not contain negative values'
FROM analytics.fact_ticket
WHERE resolution_cycle_minutes < 0;

INSERT INTO #validation_results
SELECT
    'business_rule',
    'flagged_negative_cycle_has_value',
    COUNT_BIG(*),
    'Flagged negative cycles must have a NULL analytical metric'
FROM analytics.fact_ticket
WHERE dq_negative_resolution_cycle = 1
  AND resolution_cycle_minutes IS NOT NULL;

-- Check that required database constraints remain installed.
INSERT INTO #validation_results
SELECT
    'schema',
    'expected_foreign_keys',
    CASE WHEN COUNT_BIG(*) = 7 THEN 0 ELSE 1 END,
    CONCAT('expected=7; actual=', COUNT_BIG(*))
FROM sys.foreign_keys AS fk
INNER JOIN sys.tables AS table_metadata
    ON fk.parent_object_id = table_metadata.object_id
INNER JOIN sys.schemas AS schema_metadata
    ON table_metadata.schema_id = schema_metadata.schema_id
WHERE schema_metadata.name = 'analytics';

INSERT INTO #validation_results
SELECT
    'schema',
    'expected_check_constraints',
    CASE WHEN COUNT_BIG(*) = 7 THEN 0 ELSE 1 END,
    CONCAT('expected=7; actual=', COUNT_BIG(*))
FROM sys.check_constraints AS constraint_metadata
INNER JOIN sys.tables AS table_metadata
    ON constraint_metadata.parent_object_id = table_metadata.object_id
INNER JOIN sys.schemas AS schema_metadata
    ON table_metadata.schema_id = schema_metadata.schema_id
WHERE schema_metadata.name = 'analytics';

-- CSV line-ending characters must not leak into typed dimension attributes.
INSERT INTO #validation_results
SELECT
    'data_cleanliness',
    'carriage_return_in_dimension_text',
    COUNT_BIG(*),
    'Typed dimension text must not contain CHAR(13)'
FROM (
    SELECT customer_gender AS text_value
    FROM analytics.dim_customer_profile
    UNION ALL
    SELECT customer_age_band
    FROM analytics.dim_customer_profile
    UNION ALL
    SELECT product_purchased
    FROM analytics.dim_product
    UNION ALL
    SELECT ticket_type
    FROM analytics.dim_issue
    UNION ALL
    SELECT ticket_subject
    FROM analytics.dim_issue
    UNION ALL
    SELECT ticket_channel
    FROM analytics.dim_channel
    UNION ALL
    SELECT ticket_priority
    FROM analytics.dim_priority
    UNION ALL
    SELECT ticket_status
    FROM analytics.dim_status
    UNION ALL
    SELECT day_name
    FROM analytics.dim_date
    UNION ALL
    SELECT month_name
    FROM analytics.dim_date
    UNION ALL
    SELECT quarter
    FROM analytics.dim_date
    UNION ALL
    SELECT year_month
    FROM analytics.dim_date
) AS dimension_text
WHERE text_value LIKE '%' + CHAR(13) + '%';

-- The public analytics model must not expose direct identifiers or free text.
INSERT INTO #validation_results
SELECT
    'privacy',
    'pii_columns_in_analytics',
    COUNT_BIG(*),
    'Analytics tables must not expose names, emails, or ticket free text'
FROM sys.columns AS column_metadata
INNER JOIN sys.tables AS table_metadata
    ON column_metadata.object_id = table_metadata.object_id
INNER JOIN sys.schemas AS schema_metadata
    ON table_metadata.schema_id = schema_metadata.schema_id
WHERE schema_metadata.name = 'analytics'
  AND column_metadata.name IN (
      'customer_name',
      'customer_email',
      'ticket_description',
      'ticket_body'
  );

-- Display failures first, followed by successful checks.
SELECT
    check_group,
    check_name,
    failed_rows,
    CASE WHEN failed_rows = 0 THEN 'PASS' ELSE 'FAIL' END AS [status],
    details
FROM #validation_results
ORDER BY
    CASE WHEN failed_rows > 0 THEN 0 ELSE 1 END,
    check_group,
    check_name;

SELECT
    COUNT(*) AS total_checks,
    SUM(CASE WHEN failed_rows = 0 THEN 1 ELSE 0 END) AS passed_checks,
    SUM(CASE WHEN failed_rows > 0 THEN 1 ELSE 0 END) AS failed_checks
FROM #validation_results;

IF EXISTS (
    SELECT 1
    FROM #validation_results
    WHERE failed_rows > 0
)
BEGIN
    THROW 51010, 'Analytics model validation failed.', 1;
END;
GO
