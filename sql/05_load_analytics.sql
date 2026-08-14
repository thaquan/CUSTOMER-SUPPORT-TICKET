-- Convert text-based staging data into the typed analytics model.
USE CustomerSupportAnalytics;
GO

SET NOCOUNT ON;
SET XACT_ABORT ON;
GO

-- Stop before changing analytics data when critical staging values are invalid.
IF NOT EXISTS (SELECT 1 FROM staging.fact_ticket)
    THROW 51000, 'staging.fact_ticket is empty.', 1;

IF EXISTS (
    SELECT 1
    FROM staging.fact_ticket
    WHERE TRY_CONVERT(INT, ticket_id) IS NULL
)
    THROW 51001, 'Invalid ticket_id found in staging.fact_ticket.', 1;

IF EXISTS (
    SELECT 1
    FROM staging.dim_date
    WHERE TRY_CONVERT(DATE, [date]) IS NULL
)
    THROW 51002, 'Invalid date found in staging.dim_date.', 1;

BEGIN TRY
    BEGIN TRANSACTION;

    -- Delete the fact first because it references all dimensions.
    DELETE FROM analytics.fact_ticket;
    DELETE FROM analytics.dim_customer_profile;
    DELETE FROM analytics.dim_product;
    DELETE FROM analytics.dim_issue;
    DELETE FROM analytics.dim_channel;
    DELETE FROM analytics.dim_priority;
    DELETE FROM analytics.dim_status;
    DELETE FROM analytics.dim_date;

    -- Load dimensions before the fact so every foreign key has a parent row.
    INSERT INTO analytics.dim_customer_profile (
        customer_profile_key,
        customer_age,
        customer_gender,
        customer_age_band
    )
    SELECT
        TRY_CONVERT(INT, customer_profile_key),
        TRY_CONVERT(SMALLINT, customer_age),
        LTRIM(RTRIM(customer_gender)),
        LTRIM(RTRIM(customer_age_band))
    FROM staging.dim_customer_profile;

    INSERT INTO analytics.dim_product (
        product_key,
        product_purchased
    )
    SELECT
        TRY_CONVERT(INT, product_key),
        LTRIM(RTRIM(product_purchased))
    FROM staging.dim_product;

    INSERT INTO analytics.dim_issue (
        issue_key,
        ticket_type,
        ticket_subject
    )
    SELECT
        TRY_CONVERT(INT, issue_key),
        LTRIM(RTRIM(ticket_type)),
        LTRIM(RTRIM(ticket_subject))
    FROM staging.dim_issue;

    INSERT INTO analytics.dim_channel (
        channel_key,
        ticket_channel
    )
    SELECT
        TRY_CONVERT(INT, channel_key),
        LTRIM(RTRIM(ticket_channel))
    FROM staging.dim_channel;

    INSERT INTO analytics.dim_priority (
        priority_key,
        ticket_priority
    )
    SELECT
        TRY_CONVERT(INT, priority_key),
        LTRIM(RTRIM(ticket_priority))
    FROM staging.dim_priority;

    INSERT INTO analytics.dim_status (
        status_key,
        ticket_status
    )
    SELECT
        TRY_CONVERT(INT, status_key),
        LTRIM(RTRIM(ticket_status))
    FROM staging.dim_status;

    INSERT INTO analytics.dim_date (
        date_key,
        [date],
        [day],
        day_of_week_number,
        day_name,
        month_number,
        month_name,
        quarter,
        [year],
        year_month,
        is_weekend
    )
    SELECT
        TRY_CONVERT(INT, date_key),
        TRY_CONVERT(DATE, [date]),
        TRY_CONVERT(TINYINT, [day]),
        TRY_CONVERT(TINYINT, day_of_week_number),
        LTRIM(RTRIM(day_name)),
        TRY_CONVERT(TINYINT, month_number),
        LTRIM(RTRIM(month_name)),
        LTRIM(RTRIM(quarter)),
        TRY_CONVERT(SMALLINT, [year]),
        LTRIM(RTRIM(year_month)),
        CASE REPLACE(LTRIM(RTRIM(is_weekend)), CHAR(13), '')
            WHEN N'True' THEN CAST(1 AS BIT)
            WHEN N'False' THEN CAST(0 AS BIT)
            ELSE NULL
        END
    FROM staging.dim_date;

    INSERT INTO analytics.fact_ticket (
        ticket_id,
        customer_profile_key,
        product_key,
        issue_key,
        channel_key,
        priority_key,
        status_key,
        purchase_date_key,
        first_response_at,
        resolution_at,
        resolution_cycle_minutes,
        customer_satisfaction_rating,
        is_closed,
        has_csat,
        is_low_csat,
        dq_invalid_age,
        dq_invalid_csat,
        dq_invalid_purchase_date,
        dq_invalid_first_response_at,
        dq_invalid_resolution_at,
        dq_negative_resolution_cycle
    )
    SELECT
        TRY_CONVERT(INT, ticket_id),
        TRY_CONVERT(INT, customer_profile_key),
        TRY_CONVERT(INT, product_key),
        TRY_CONVERT(INT, issue_key),
        TRY_CONVERT(INT, channel_key),
        TRY_CONVERT(INT, priority_key),
        TRY_CONVERT(INT, status_key),
        TRY_CONVERT(INT, purchase_date_key),
        TRY_CONVERT(
            DATETIME2(0),
            NULLIF(LTRIM(RTRIM(first_response_at)), N'')
        ),
        TRY_CONVERT(
            DATETIME2(0),
            NULLIF(LTRIM(RTRIM(resolution_at)), N'')
        ),
        TRY_CONVERT(
            DECIMAL(12, 2),
            NULLIF(LTRIM(RTRIM(resolution_cycle_minutes)), N'')
        ),
        TRY_CONVERT(
            DECIMAL(2, 1),
            NULLIF(LTRIM(RTRIM(customer_satisfaction_rating)), N'')
        ),
        CASE REPLACE(LTRIM(RTRIM(is_closed)), CHAR(13), '')
            WHEN N'True' THEN CAST(1 AS BIT)
            WHEN N'False' THEN CAST(0 AS BIT)
            ELSE NULL
        END,
        CASE REPLACE(LTRIM(RTRIM(has_csat)), CHAR(13), '')
            WHEN N'True' THEN CAST(1 AS BIT)
            WHEN N'False' THEN CAST(0 AS BIT)
            ELSE NULL
        END,
        CASE REPLACE(LTRIM(RTRIM(is_low_csat)), CHAR(13), '')
            WHEN N'True' THEN CAST(1 AS BIT)
            WHEN N'False' THEN CAST(0 AS BIT)
            ELSE NULL
        END,
        CASE REPLACE(LTRIM(RTRIM(dq_invalid_age)), CHAR(13), '')
            WHEN N'True' THEN CAST(1 AS BIT)
            WHEN N'False' THEN CAST(0 AS BIT)
            ELSE NULL
        END,
        CASE REPLACE(LTRIM(RTRIM(dq_invalid_csat)), CHAR(13), '')
            WHEN N'True' THEN CAST(1 AS BIT)
            WHEN N'False' THEN CAST(0 AS BIT)
            ELSE NULL
        END,
        CASE REPLACE(LTRIM(RTRIM(dq_invalid_purchase_date)), CHAR(13), '')
            WHEN N'True' THEN CAST(1 AS BIT)
            WHEN N'False' THEN CAST(0 AS BIT)
            ELSE NULL
        END,
        CASE REPLACE(LTRIM(RTRIM(dq_invalid_first_response_at)), CHAR(13), '')
            WHEN N'True' THEN CAST(1 AS BIT)
            WHEN N'False' THEN CAST(0 AS BIT)
            ELSE NULL
        END,
        CASE REPLACE(LTRIM(RTRIM(dq_invalid_resolution_at)), CHAR(13), '')
            WHEN N'True' THEN CAST(1 AS BIT)
            WHEN N'False' THEN CAST(0 AS BIT)
            ELSE NULL
        END,
        CASE REPLACE(LTRIM(RTRIM(dq_negative_resolution_cycle)), CHAR(13), '')
            WHEN N'True' THEN CAST(1 AS BIT)
            WHEN N'False' THEN CAST(0 AS BIT)
            ELSE NULL
        END
    FROM staging.fact_ticket;

    COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    THROW;
END CATCH;
GO

-- Report final row counts for reconciliation with the Gold CSV files.
SELECT 'fact_ticket' AS table_name, COUNT_BIG(*) AS row_count
FROM analytics.fact_ticket
UNION ALL
SELECT 'dim_customer_profile', COUNT_BIG(*)
FROM analytics.dim_customer_profile
UNION ALL
SELECT 'dim_product', COUNT_BIG(*)
FROM analytics.dim_product
UNION ALL
SELECT 'dim_issue', COUNT_BIG(*)
FROM analytics.dim_issue
UNION ALL
SELECT 'dim_channel', COUNT_BIG(*)
FROM analytics.dim_channel
UNION ALL
SELECT 'dim_priority', COUNT_BIG(*)
FROM analytics.dim_priority
UNION ALL
SELECT 'dim_status', COUNT_BIG(*)
FROM analytics.dim_status
UNION ALL
SELECT 'dim_date', COUNT_BIG(*)
FROM analytics.dim_date;
GO
