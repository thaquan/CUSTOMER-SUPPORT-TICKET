USE master;
GO

IF DB_ID(N'CustomerSupportAnalytics') IS NULL
BEGIN
    CREATE DATABASE CustomerSupportAnalytics;
END;
GO

USE CustomerSupportAnalytics;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.schemas
    WHERE name = N'staging'
)

BEGIN 
    EXEC(N'CREATE SCHEMA staging;');
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.schemas
    WHERE name = N'analytics'
)

BEGIN 
    EXEC(N'CREATE SCHEMA analytics;');
END;
GO

SELECT 
    name
FROM sys.schemas
WHERE name IN (
    N'staging', 
    N'analytics'
);

