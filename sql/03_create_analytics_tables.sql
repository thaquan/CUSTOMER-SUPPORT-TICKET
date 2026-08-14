USE CustomerSupportAnalytics;
GO

-- Drop the fact first because it owns all foreign-key references.
DROP TABLE IF EXISTS analytics.fact_ticket;
DROP TABLE IF EXISTS analytics.dim_customer_profile;
DROP TABLE IF EXISTS analytics.dim_product;
DROP TABLE IF EXISTS analytics.dim_issue;
DROP TABLE IF EXISTS analytics.dim_channel;
DROP TABLE IF EXISTS analytics.dim_priority;
DROP TABLE IF EXISTS analytics.dim_status;
DROP TABLE IF EXISTS analytics.dim_date;
GO

CREATE TABLE analytics.dim_customer_profile (
    customer_profile_key INT NOT NULL,
    customer_age SMALLINT NOT NULL,
    customer_gender NVARCHAR(50) NOT NULL,
    customer_age_band VARCHAR(20) NOT NULL,

    CONSTRAINT pk_dim_customer_profile
        PRIMARY KEY (customer_profile_key),
    CONSTRAINT uq_dim_customer_profile_grain
        UNIQUE (customer_age, customer_gender, customer_age_band),
    CONSTRAINT ck_dim_customer_profile_age
        CHECK (customer_age BETWEEN 18 AND 100)
);
GO

CREATE TABLE analytics.dim_product (
    product_key INT NOT NULL,
    product_purchased NVARCHAR(255) NOT NULL,

    CONSTRAINT pk_dim_product
        PRIMARY KEY (product_key),
    CONSTRAINT uq_dim_product_grain
        UNIQUE (product_purchased)
);
GO

CREATE TABLE analytics.dim_issue (
    issue_key INT NOT NULL,
    ticket_type NVARCHAR(100) NOT NULL,
    ticket_subject NVARCHAR(255) NOT NULL,

    CONSTRAINT pk_dim_issue
        PRIMARY KEY (issue_key),
    CONSTRAINT uq_dim_issue_grain
        UNIQUE (ticket_type, ticket_subject)
);
GO

CREATE TABLE analytics.dim_channel (
    channel_key INT NOT NULL,
    ticket_channel NVARCHAR(100) NOT NULL,

    CONSTRAINT pk_dim_channel
        PRIMARY KEY (channel_key),
    CONSTRAINT uq_dim_channel_grain
        UNIQUE (ticket_channel)
);
GO

CREATE TABLE analytics.dim_priority (
    priority_key INT NOT NULL,
    ticket_priority NVARCHAR(50) NOT NULL,

    CONSTRAINT pk_dim_priority
        PRIMARY KEY (priority_key),
    CONSTRAINT uq_dim_priority_grain
        UNIQUE (ticket_priority)
);
GO

CREATE TABLE analytics.dim_status (
    status_key INT NOT NULL,
    ticket_status NVARCHAR(100) NOT NULL,

    CONSTRAINT pk_dim_status
        PRIMARY KEY (status_key),
    CONSTRAINT uq_dim_status_grain
        UNIQUE (ticket_status)
);
GO

CREATE TABLE analytics.dim_date (
    date_key INT NOT NULL,
    [date] DATE NOT NULL,
    [day] TINYINT NOT NULL,
    day_of_week_number TINYINT NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    month_number TINYINT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    quarter CHAR(2) NOT NULL,
    [year] SMALLINT NOT NULL,
    year_month CHAR(7) NOT NULL,
    is_weekend BIT NOT NULL,

    CONSTRAINT pk_dim_date
        PRIMARY KEY (date_key),
    CONSTRAINT uq_dim_date_grain
        UNIQUE ([date]),
    CONSTRAINT ck_dim_date_day
        CHECK ([day] BETWEEN 1 AND 31),
    CONSTRAINT ck_dim_date_weekday
        CHECK (day_of_week_number BETWEEN 1 AND 7),
    CONSTRAINT ck_dim_date_month
        CHECK (month_number BETWEEN 1 AND 12),
    CONSTRAINT ck_dim_date_quarter
        CHECK (quarter IN ('Q1', 'Q2', 'Q3', 'Q4'))
);
GO

CREATE TABLE analytics.fact_ticket (
    ticket_id INT NOT NULL,
    customer_profile_key INT NOT NULL,
    product_key INT NOT NULL,
    issue_key INT NOT NULL,
    channel_key INT NOT NULL,
    priority_key INT NOT NULL,
    status_key INT NOT NULL,
    purchase_date_key INT NOT NULL,
    first_response_at DATETIME2(0) NULL,
    resolution_at DATETIME2(0) NULL,
    resolution_cycle_minutes DECIMAL(12, 2) NULL,
    customer_satisfaction_rating DECIMAL(2, 1) NULL,
    is_closed BIT NOT NULL,
    has_csat BIT NOT NULL,
    is_low_csat BIT NOT NULL,
    dq_invalid_age BIT NOT NULL,
    dq_invalid_csat BIT NOT NULL,
    dq_invalid_purchase_date BIT NOT NULL,
    dq_invalid_first_response_at BIT NOT NULL,
    dq_invalid_resolution_at BIT NOT NULL,
    dq_negative_resolution_cycle BIT NOT NULL,

    CONSTRAINT pk_fact_ticket
        PRIMARY KEY (ticket_id),
    CONSTRAINT ck_fact_ticket_resolution_cycle
        CHECK (
            resolution_cycle_minutes IS NULL
            OR resolution_cycle_minutes >= 0
        ),
    CONSTRAINT ck_fact_ticket_csat
        CHECK (
            customer_satisfaction_rating IS NULL
            OR customer_satisfaction_rating IN (1, 2, 3, 4, 5)
        )
);
GO

ALTER TABLE analytics.fact_ticket
ADD CONSTRAINT fk_fact_customer_profile
FOREIGN KEY (customer_profile_key)
REFERENCES analytics.dim_customer_profile (customer_profile_key);
GO

ALTER TABLE analytics.fact_ticket
ADD CONSTRAINT fk_fact_product
FOREIGN KEY (product_key)
REFERENCES analytics.dim_product (product_key);
GO

ALTER TABLE analytics.fact_ticket
ADD CONSTRAINT fk_fact_issue
FOREIGN KEY (issue_key)
REFERENCES analytics.dim_issue (issue_key);
GO

ALTER TABLE analytics.fact_ticket
ADD CONSTRAINT fk_fact_channel
FOREIGN KEY (channel_key)
REFERENCES analytics.dim_channel (channel_key);
GO

ALTER TABLE analytics.fact_ticket
ADD CONSTRAINT fk_fact_priority
FOREIGN KEY (priority_key)
REFERENCES analytics.dim_priority (priority_key);
GO

ALTER TABLE analytics.fact_ticket
ADD CONSTRAINT fk_fact_status
FOREIGN KEY (status_key)
REFERENCES analytics.dim_status (status_key);
GO

ALTER TABLE analytics.fact_ticket
ADD CONSTRAINT fk_fact_purchase_date
FOREIGN KEY (purchase_date_key)
REFERENCES analytics.dim_date (date_key);
GO

CREATE INDEX ix_fact_ticket_customer_profile
ON analytics.fact_ticket (customer_profile_key);

CREATE INDEX ix_fact_ticket_product
ON analytics.fact_ticket (product_key);

CREATE INDEX ix_fact_ticket_issue
ON analytics.fact_ticket (issue_key);

CREATE INDEX ix_fact_ticket_channel
ON analytics.fact_ticket (channel_key);

CREATE INDEX ix_fact_ticket_priority
ON analytics.fact_ticket (priority_key);

CREATE INDEX ix_fact_ticket_status
ON analytics.fact_ticket (status_key);

CREATE INDEX ix_fact_ticket_purchase_date
ON analytics.fact_ticket (purchase_date_key);
GO
