USE CustomerSupportAnalytics;
GO

DROP TABLE IF EXISTS staging.dim_customer_profile;
GO

CREATE TABLE staging.dim_customer_profile (
    customer_profile_key NVARCHAR(50) NULL,
    customer_age NVARCHAR(50) NULL,
    customer_gender NVARCHAR(100) NULL,
    customer_age_band NVARCHAR(50) NULL
);
GO

DROP TABLE IF EXISTS staging.dim_product;
GO

CREATE TABLE staging.dim_product (
    product_key NVARCHAR(50) NULL,
    product_purchased NVARCHAR(255) NULL
);
GO

DROP TABLE IF EXISTS staging.dim_issue;
GO

CREATE TABLE staging.dim_issue (
    issue_key NVARCHAR(50) NULL,
    ticket_type NVARCHAR(255) NULL,
    ticket_subject NVARCHAR(255) NULL
);
GO

DROP TABLE IF EXISTS staging.dim_channel;
GO

CREATE TABLE staging.dim_channel (
    channel_key NVARCHAR(50) NULL,
    ticket_channel NVARCHAR(100) NULL
);
GO

DROP TABLE IF EXISTS staging.dim_priority;
GO

CREATE TABLE staging.dim_priority (
    priority_key NVARCHAR(50) NULL,
    ticket_priority NVARCHAR(50) NULL
);
GO

DROP TABLE IF EXISTS staging.dim_status;
GO

CREATE TABLE staging.dim_status (
    status_key NVARCHAR(50) NULL,
    ticket_status NVARCHAR(100) NULL
);
GO

DROP TABLE IF EXISTS staging.dim_date;
GO

CREATE TABLE staging.dim_date (
    date_key NVARCHAR(50) NULL,
    [date] NVARCHAR(50) NULL,
    [day] NVARCHAR(50) NULL,
    day_of_week_number NVARCHAR(50) NULL,
    day_name NVARCHAR(50) NULL,
    month_number NVARCHAR(50) NULL,
    month_name NVARCHAR(50) NULL,
    quarter NVARCHAR(50) NULL,
    [year] NVARCHAR(50) NULL,
    year_month NVARCHAR(50) NULL,
    is_weekend NVARCHAR(50) NULL
);
GO

DROP TABLE IF EXISTS staging.fact_ticket;
GO

CREATE TABLE staging.fact_ticket (
    ticket_id NVARCHAR(50) NULL,
    customer_profile_key NVARCHAR(50) NULL,
    product_key NVARCHAR(50) NULL,
    issue_key NVARCHAR(50) NULL,
    channel_key NVARCHAR(50) NULL,
    priority_key NVARCHAR(50) NULL,
    status_key NVARCHAR(50) NULL,
    purchase_date_key NVARCHAR(50) NULL,
    first_response_at NVARCHAR(100) NULL,
    resolution_at NVARCHAR(100) NULL,
    resolution_cycle_minutes NVARCHAR(100) NULL,
    customer_satisfaction_rating NVARCHAR(50) NULL,
    is_closed NVARCHAR(20) NULL,
    has_csat NVARCHAR(20) NULL,
    is_low_csat NVARCHAR(20) NULL,
    dq_invalid_age NVARCHAR(20) NULL,
    dq_invalid_csat NVARCHAR(20) NULL,
    dq_invalid_purchase_date NVARCHAR(20) NULL,
    dq_invalid_first_response_at NVARCHAR(20) NULL,
    dq_invalid_resolution_at NVARCHAR(20) NULL,
    dq_negative_resolution_cycle NVARCHAR(20) NULL
);
GO
