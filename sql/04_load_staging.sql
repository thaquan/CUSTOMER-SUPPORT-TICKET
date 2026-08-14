-- Planned next phase: bulk-load the eight local Gold CSV files into staging.
USE CustomerSupportAnalytics;
GO

SET NOCOUNT ON;
SET XACT_ABORT ON;
GO

BEGIN TRY
    BEGIN TRANSACTION;

    TRUNCATE TABLE staging.fact_ticket;
    TRUNCATE TABLE staging.dim_customer_profile;
    TRUNCATE TABLE staging.dim_product;
    TRUNCATE TABLE staging.dim_issue;
    TRUNCATE TABLE staging.dim_channel;
    TRUNCATE TABLE staging.dim_priority;
    TRUNCATE TABLE staging.dim_status;
    TRUNCATE TABLE staging.dim_date;

    BULK INSERT staging.fact_ticket
    FROM 'D:\Customer Support Ticket Dataset\data\gold\fact_ticket.csv'
    WITH (
        FORMAT = 'CSV',
        FIRSTROW = 2,
        FIELDQUOTE = '"',
        ROWTERMINATOR = '0x0a',
        CODEPAGE = '65001',
        TABLOCK
    );

BULK INSERT staging.dim_customer_profile
FROM 'D:\Customer Support Ticket Dataset\data\gold\dim_customer_profile.csv'
WITH (
    FORMAT = 'CSV',
    FIRSTROW = 2,
    FIELDQUOTE = '"',
    ROWTERMINATOR = '0x0a',
    CODEPAGE = '65001',
    TABLOCK
);

BULK INSERT staging.dim_product
FROM 'D:\Customer Support Ticket Dataset\data\gold\dim_product.csv'
WITH (
    FORMAT = 'CSV',
    FIRSTROW = 2,
    FIELDQUOTE = '"',
    ROWTERMINATOR = '0x0a',
    CODEPAGE = '65001',
    TABLOCK
);

BULK INSERT staging.dim_issue
FROM 'D:\Customer Support Ticket Dataset\data\gold\dim_issue.csv'
WITH (
    FORMAT = 'CSV',
    FIRSTROW = 2,
    FIELDQUOTE = '"',
    ROWTERMINATOR = '0x0a',
    CODEPAGE = '65001',
    TABLOCK
);

BULK INSERT staging.dim_channel
FROM 'D:\Customer Support Ticket Dataset\data\gold\dim_channel.csv'
WITH (
    FORMAT = 'CSV',
    FIRSTROW = 2,
    FIELDQUOTE = '"',
    ROWTERMINATOR = '0x0a',
    CODEPAGE = '65001',
    TABLOCK
);

BULK INSERT staging.dim_priority
FROM 'D:\Customer Support Ticket Dataset\data\gold\dim_priority.csv'
WITH (
    FORMAT = 'CSV',
    FIRSTROW = 2,
    FIELDQUOTE = '"',
    ROWTERMINATOR = '0x0a',
    CODEPAGE = '65001',
    TABLOCK
);

BULK INSERT staging.dim_status
FROM 'D:\Customer Support Ticket Dataset\data\gold\dim_status.csv'
WITH (
    FORMAT = 'CSV',
    FIRSTROW = 2,
    FIELDQUOTE = '"',
    ROWTERMINATOR = '0x0a',
    CODEPAGE = '65001',
    TABLOCK
);

BULK INSERT staging.dim_date
FROM 'D:\Customer Support Ticket Dataset\data\gold\dim_date.csv'
WITH (
    FORMAT = 'CSV',
    FIRSTROW = 2,
    FIELDQUOTE = '"',
    ROWTERMINATOR = '0x0a',
    CODEPAGE = '65001',
    TABLOCK
);

    COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    THROW;
END CATCH;
GO

SELECT
    'fact_ticket' AS table_name,
    COUNT_BIG(*) AS row_count
FROM staging.fact_ticket

UNION ALL

SELECT
    'dim_customer_profile',
    COUNT_BIG(*)
FROM staging.dim_customer_profile

UNION ALL

SELECT
    'dim_product',
    COUNT_BIG(*)
FROM staging.dim_product

UNION ALL

SELECT
    'dim_issue',
    COUNT_BIG(*)
FROM staging.dim_issue

UNION ALL

SELECT
    'dim_channel',
    COUNT_BIG(*)
FROM staging.dim_channel

UNION ALL

SELECT
    'dim_priority',
    COUNT_BIG(*)
FROM staging.dim_priority

UNION ALL

SELECT
    'dim_status',
    COUNT_BIG(*)
FROM staging.dim_status

UNION ALL

SELECT
    'dim_date',
    COUNT_BIG(*)
FROM staging.dim_date;
GO

SELECT *
FROM staging.fact_ticket
WHERE ticket_id = N'ticket_id';

SELECT TOP (5) *
FROM staging.fact_ticket;

SELECT
    'fact_ticket' AS table_name,
    COUNT(*) AS rows_with_carriage_return
FROM staging.fact_ticket
WHERE dq_negative_resolution_cycle
    LIKE '%' + CHAR(13) + '%';

SELECT
    'dim_date' AS table_name,
    COUNT(*) AS rows_with_carriage_return
FROM staging.dim_date
WHERE is_weekend
    LIKE '%' + CHAR(13) + '%';
GO
