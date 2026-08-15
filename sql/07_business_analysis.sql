-- Reusable operational and customer-experience analysis.
USE CustomerSupportAnalytics;
GO

SET NOCOUNT ON;
GO

-- Business question: What is the overall support workload?
-- Result grain: One row for the complete dataset.
-- KPI note: Low-CSAT rate uses only tickets that have a CSAT response.
SELECT
    COUNT_BIG(*) AS total_tickets,
    SUM(CAST(is_closed AS BIGINT)) AS closed_tickets,
    COUNT_BIG(*) - SUM(CAST(is_closed AS BIGINT)) AS backlog_tickets,
    CAST(
        100.0 * SUM(CAST(is_closed AS BIGINT))
        / NULLIF(COUNT_BIG(*), 0) AS DECIMAL(6, 2)
    ) AS resolution_rate_pct,
    SUM(CAST(has_csat AS BIGINT)) AS csat_responses,

    CAST(
        100.0 * SUM(CAST(has_csat AS BIGINT))
        / NULLIF(COUNT_BIG(*), 0) AS DECIMAL(6, 2)
    ) AS csat_response_rate_pct,

    CAST (
        AVG(customer_satisfaction_rating)
        AS DECIMAL(4, 2)
    ) AS average_csat,

    SUM(CAST(is_low_csat AS BIGINT)) AS low_csat_tickets,

    CAST(
        100.0 * SUM(CAST(is_low_csat AS BIGINT))
        / NULLIF(SUM(CAST(has_csat AS BIGINT)), 0) AS DECIMAL(6, 2)
    ) AS low_csat_rate_pct,

    COUNT(resolution_cycle_minutes) AS valid_resolution_cycle_tickets,

    CAST (
        AVG(resolution_cycle_minutes)
        AS DECIMAL(12, 2)
    ) AS average_resolution_cycle_minutes,

    (
        SELECT TOP (1)
            CAST(
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY resolution_cycle_minutes) OVER ()
                AS DECIMAL(12, 2)
            )
        FROM analytics.fact_ticket
        WHERE resolution_cycle_minutes IS NOT NULL
    ) AS median_resolution_cycle_minutes
FROM analytics.fact_ticket;
GO

-- Business question: Where is unresolved workload concentrated?
-- Result grain: One row per priority and unresolved status.
-- KPI note: Backlog means is_closed = 0.

SELECT
    priority.ticket_priority,
    status.ticket_status,
    COUNT_BIG(*) AS backlog_tickets,
    CAST(
        100.0 * COUNT_BIG(*)
        / NULLIF(SUM(COUNT_BIG(*)) OVER (), 0) AS DECIMAL(6, 2)
    ) AS backlog_percentage
FROM analytics.fact_ticket AS fact
JOIN analytics.dim_priority AS priority
    ON fact.priority_key = priority.priority_key
JOIN analytics.dim_status AS status
    ON fact.status_key = status.status_key
WHERE fact.is_closed = 0
GROUP BY
    priority.ticket_priority,
    status.ticket_status
ORDER BY
    CASE priority.ticket_priority
        WHEN 'Critical' THEN 1
        WHEN 'High' THEN 2
        WHEN 'Medium' THEN 3
        WHEN 'Low' THEN 4
        ELSE 5
    END,
    backlog_tickets DESC;
GO

-- Business question: How do support channels compare?
-- Result grain: One row per support channel.
-- KPI note: Low-CSAT rate uses tickets with CSAT as its denominator.

SELECT
    channel.ticket_channel,
    COUNT_BIG(*) AS total_tickets,

    SUM(CAST(fact.is_closed AS BIGINT))
        AS closed_tickets,

    COUNT_BIG(*) -
        SUM(CAST(fact.is_closed AS BIGINT))
        AS backlog_tickets,

    CAST(
        100.0 * SUM(CAST(fact.is_closed AS BIGINT))
        / NULLIF(COUNT_BIG(*), 0)
        AS DECIMAL(6, 2)
    ) AS resolution_rate_pct,

    SUM(CAST(fact.has_csat AS BIGINT))
        AS csat_responses,

    CAST(
        AVG(fact.customer_satisfaction_rating)
        AS DECIMAL(4, 2)
    ) AS average_csat,

    CAST(
        100.0 * SUM(CAST(fact.is_low_csat AS BIGINT))
        / NULLIF(SUM(CAST(fact.has_csat AS BIGINT)), 0)
        AS DECIMAL(6, 2)
    ) AS low_csat_rate_pct,

    COUNT(fact.resolution_cycle_minutes)
        AS valid_resolution_cycle_tickets,

    CAST(
        AVG(fact.resolution_cycle_minutes)
        AS DECIMAL(12, 2)
    ) AS average_resolution_cycle_minutes
FROM analytics.fact_ticket AS fact
INNER JOIN analytics.dim_channel AS channel
    ON fact.channel_key = channel.channel_key
GROUP BY channel.ticket_channel
ORDER BY total_tickets DESC;
GO

-- Business question: Which issue categories generate most support demand?
-- Result grain: One row per ticket type and subject.
-- KPI note: Cumulative share supports Pareto analysis.
WITH issue_volume AS (
    SELECT
        issue.ticket_type,
        issue.ticket_subject,
        COUNT_BIG(*) AS total_tickets
    FROM analytics.fact_ticket AS fact
    INNER JOIN analytics.dim_issue AS issue
        ON fact.issue_key = issue.issue_key
    GROUP BY
        issue.ticket_type,
        issue.ticket_subject
),
issue_pareto AS (
    SELECT
        ticket_type,
        ticket_subject,
        total_tickets,
        SUM(total_tickets) OVER (
            ORDER BY total_tickets DESC, ticket_type, ticket_subject
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_ticket_count,
        SUM(total_tickets) OVER () AS all_ticket_count
    FROM issue_volume
)

SELECT
    ticket_type,
    ticket_subject,
    total_tickets,

    CAST (
        100.0 * total_tickets
        / NULLIF(all_ticket_count, 0) AS DECIMAL(6, 2)
    ) AS ticket_share_pct,

    CAST (
        100.0 * cumulative_ticket_count
        / NULLIF(all_ticket_count, 0) AS DECIMAL(6, 2)
    ) AS cumulative_ticket_share_pct,
    CASE
        WHEN 100.0 * cumulative_ticket_count / NULLIF(all_ticket_count, 0) <= 80 THEN 'Top 80%'
        ELSE 'Remaining'
    END AS pareto_category
FROM issue_pareto
ORDER BY
    total_tickets DESC,
    ticket_type,
    ticket_subject;
GO

-- Business question: Which products generate demand and low satisfaction?
-- Result grain: One row per purchased product.
-- KPI note: Ticket volume is not a product defect rate because sales volume is unavailable.

SELECT
    product.product_purchased,
    COUNT_BIG(*) AS total_tickets,
    COUNT_BIG(*) -
    SUM(CAST(fact.is_closed AS BIGINT)) AS backlog_tickets,

    CAST (
        100.0 * (
            COUNT_BIG(*) - SUM(CAST(fact.is_closed AS BIGINT))
        )
        / NULLIF(COUNT_BIG(*), 0) AS DECIMAL(6, 2)
    ) AS backlog_rate_pct,

    SUM(CAST(fact.has_csat AS BIGINT)) AS csat_responses,

    CAST (
        AVG(fact.customer_satisfaction_rating)
        AS DECIMAL(4, 2)
    ) AS average_csat,

    CAST (
        100.0 * SUM(CAST(fact.is_low_csat AS BIGINT))
        / NULLIF(SUM(CAST(fact.has_csat AS BIGINT)), 0) AS DECIMAL(6, 2)
    ) AS low_csat_rate_pct
FROM analytics.fact_ticket AS fact
INNER JOIN analytics.dim_product AS product
    ON fact.product_key = product.product_key
GROUP BY
    product.product_purchased
ORDER BY
    total_tickets DESC,
    product.product_purchased;
GO

-- Business question: Do high-priority tickets remain unresolved?
-- Result grain: One row per ticket priority.
-- KPI note: Resolution cycle excludes missing and invalid cycle values.
SELECT
    priority.ticket_priority,
    COUNT_BIG(*) AS total_tickets,

    SUM(CAST(fact.is_closed AS BIGINT)) AS closed_tickets,

    COUNT_BIG(*) - SUM(CAST(fact.is_closed AS BIGINT)) AS backlog_tickets,

    CAST(
        100.0 * (
            COUNT_BIG(*) - SUM(CAST(fact.is_closed AS BIGINT))
        )
        / NULLIF(COUNT_BIG(*), 0) AS DECIMAL(6, 2)
    ) AS backlog_rate_pct,

    COUNT(fact.resolution_cycle_minutes) AS valid_resolution_cycle_tickets,

    CAST (
        AVG(fact.resolution_cycle_minutes)
        AS DECIMAL(12, 2)
    ) AS average_resolution_cycle_minutes,

    CAST(
        AVG(fact.customer_satisfaction_rating)
        AS DECIMAL(4, 2)
    ) AS average_csat
FROM analytics.fact_ticket AS fact
JOIN analytics.dim_priority AS priority
    ON fact.priority_key = priority.priority_key
GROUP BY
    priority.ticket_priority
ORDER BY
    CASE priority.ticket_priority
        WHEN 'Critical' THEN 1
        WHEN 'High' THEN 2
        WHEN 'Medium' THEN 3
        WHEN 'Low' THEN 4
        ELSE 5
    END;
GO

-- Business question: Which product purchase cohorts are represented in support?
-- Result grain: One row per purchase year-month.
-- KPI note: This is a purchase cohort, not a ticket-created timeline.

SELECT
    calendar.year_month AS purchase_year_month,
    MIN(calendar.[date]) AS cohort_month_start,
    COUNT_BIG(*) AS tickets_linked_to_purchases,

    SUM(CAST(fact.is_closed AS BIGINT)) AS closed_tickets,

    CAST(
        AVG(fact.customer_satisfaction_rating)
        AS DECIMAL(4, 2)
    ) AS average_csat
FROM analytics.fact_ticket AS fact
JOIN analytics.dim_date AS  calendar
    ON fact.purchase_date_key = calendar.date_key
GROUP BY
    calendar.year_month
ORDER BY
    cohort_month_start;
GO

-- Business question: How much source data required quality flagging?
-- Result grain: One row for the complete analytical dataset.
-- KPI note: Quality flags preserve source issues without silently correcting them.

SELECT
    COUNT_BIG(*) AS total_tickets,
    SUM(CAST(dq_invalid_age AS BIGINT))
        AS invalid_age_rows,
    SUM(CAST(dq_invalid_csat AS BIGINT))
        AS invalid_csat_rows,
    SUM(CAST(dq_invalid_purchase_date AS BIGINT))
        AS invalid_purchase_date_rows,
    SUM(CAST(dq_invalid_first_response_at AS BIGINT))
        AS invalid_first_response_rows,
    SUM(CAST(dq_invalid_resolution_at AS BIGINT))
        AS invalid_resolution_rows,
    SUM(CAST(dq_negative_resolution_cycle AS BIGINT))
        AS negative_resolution_cycle_rows,

    CAST(
        100.0 * SUM(
            CAST(dq_negative_resolution_cycle AS BIGINT)
        )
        / NULLIF(COUNT_BIG(*), 0)
        AS DECIMAL(6, 2)
    ) AS negative_resolution_cycle_rate_pct
FROM analytics.fact_ticket;
GO
