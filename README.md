# CustomFunctions


<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

# Setup and Deployment Guide

## 1. Installing Snowflake CLI

[Link](https://docs.snowflake.com/en/CUSTOM_FUNCTIONSeloper-guide/snowflake-cli-v2/installation/installation)

[Cheat
Sheet](https://github.com/Snowflake-Labs/sf-cheatsheets/blob/main/snowflake-cli.md)

To install the Snowflake CLI, follow the instructions provided in the
official installation guide. This guide covers all the necessary steps
to set up the CLI on your system.

## 2. Configuring the CLI

To use the Snowflake CLI, you need to create a connection configuration
in the ~/.snowflake/config.toml file. This file allows you to specify
connection details for various environments. Refer to the Snowflake CLI
configuration documentation for a comprehensive guide.

[Using Snowpark in Snowflake
CLI](https://docs.snowflake.com/en/CUSTOM_FUNCTIONSeloper-guide/snowflake-cli-v2/snowpark/overview)

## 3. Setting Up Your Database and Schema

You can use the Snowsight UI or the Snowflake CLI to execute the
following SQL commands. While the code example uses the ACCOUNTADMIN
role for simplicity, you should use a role with the appropriate
permissions in your environment.

``` sql
ALTER SESSION SET query_tag = '{"team":"Solutions","name":"JeremyDemlow", "version":0.1, "attributes":{"medium":"setup", "source":"DATASCIENCE", "purpose": "setup"}}';

USE ROLE ACCOUNTADMIN;
CREATE ROLE DATA_SCIENTIST;

USE ROLE SYSADMIN;
GRANT CREATE DATABASE ON ACCOUNT TO ROLE DATA_SCIENTIST;
GRANT CREATE WAREHOUSE ON ACCOUNT TO ROLE DATA_SCIENTIST;
GRANT CREATE COMPUTE POOL ON ACCOUNT TO ROLE DATA_SCIENTIST;

USE ROLE ACCOUNTADMIN;
GRANT CREATE INTEGRATION ON ACCOUNT TO ROLE DATA_SCIENTIST;
GRANT MONITOR USAGE ON ACCOUNT TO ROLE DATA_SCIENTIST;
GRANT EXECUTE MANAGED TASK ON ACCOUNT TO ROLE DATA_SCIENTIST;
GRANT BIND SERVICE ENDPOINT ON ACCOUNT TO ROLE DATA_SCIENTIST;
GRANT IMPORTED PRIVILEGES ON DATABASE snowflake TO ROLE DATA_SCIENTIST;
SET my_user_var = (SELECT  '"' || CURRENT_USER() || '"' );
GRANT ROLE data_scientist TO USER identifier($my_user_var);

USE ROLE DATA_SCIENTIST;

CREATE OR REPLACE WAREHOUSE DS_WH_XS
  WAREHOUSE_SIZE = XSMALL
  AUTO_SUSPEND = 120
  AUTO_RESUME = TRUE;

CREATE DATABASE DATASCIENCE; 
CREATE SCHEMA DATASCIENCE;
USE SCHEMA DATASCIENCE;
```

## 4. Initializing and Deploying the Snowpark Project

### Creating a Boilerplate

To set up a boilerplate Snowpark project, use the following command:

``` bash
snow init custom_functions --template example_snowpark
```

> Note: The boilerplate structure can be customized. In this example,
> adjustments were made to rename the default ‘app/’ directory to
> ‘DATASCIENCE/’ in the snowflake.yml file. You can modify these
> settings based on your preferences. As I have done here to match the
> CUSTOM_FUNCTIONSelopmen style that I enjoy.

### Adding Repo To Snowflake

``` bash
snow connection set-default DATASCIENCE
snow connection test
snow git setup DATASCIENCE
```

### Building and Deploying the Project

To build and deploy the Snowpark project, execute:

``` bash
snow snowpark build; snow snowpark deploy --replace; rm DATASCIENCE.zip; rm dependencies.zip; rm dev.zip; rm requirements.snowflake.txt
```

The deployment output will list the created objects, such as procedures
and functions.

## 5. Creating and Testing a Table

### Creating a Fake Orders Table

Navigate to the CUSTOM_FUNCTIONS/CUSTOM_FUNCTIONSelopment.ipynb notebook
and run the cells to create a fake orders table in the CUSTOM_FUNCTIONS
schema. This setup is essential for testing and
CUSTOM_FUNCTIONSelopment.

> Note: Running the entire notebook will also perform an aggregation in
> the CUSTOM_FUNCTIONS schema. You can defer this step if you prefer to
> follow the next steps.

### Testing Functions and Procedures

To test the functions and procedures, use the following commands in
Snowsight or the Snowflake CLI:

``` bash
# Run Function
snow sql -q "SELECT DATASCIENCE.CUSTOM_FUNCTIONS.HELLO_FUNCTION('I would like a sandwich, please');"

# Run Procedures
snow sql -f ./customfunctions/files/perform_aggregation_config.sql
now sql -f ./customfunctions/files/perform_aggregation_config.sql -D SOURCE_TABLE=DATASCIENCE.CUSTOM_FUNCTIONS.ORDERS -D TARGET_TABLE=DATASCIENCE.CUSTOM_FUNCTIONS.ORDERS_AGGREGATES
```

**In Snowsight:**

``` sql
CREATE SCHEMA IF NOT EXISTS DATASCIENCE.UAT;
-- Using caller rights of the session, but using CUSTOM_FUNCTIONS data and putting the results in uat
CALL DATASCIENCE.CUSTOM_FUNCTIONS.PERFORM_AGGREGATION(
'{
    "request_id": "AGG_002",
    "source_table": "DATASCIENCE.CUSTOM_FUNCTIONS.orders",
    "target_table": "DATASCIENCE.uat.orders_aggregates",
    "group_by": ["PRODUCT_CATEGORY", "REGION"],
    "metrics": [
        {"name": "TOTAL_SALES", "function": "sum", "column": "SALES_AMOUNT"},
        {"name": "AVERAGE_ORDER_VALUE", "function": "avg", "column": "ORDER_VALUE"},
        {"name": "ORDER_COUNT", "function": "count", "column": "ORDER_ID"}
    ],
    "filters": [
        {"column": "DATE", "operator": "between", "value": ["2023-01-01", "2023-12-31"]},
        {"column": "STATUS", "operator": "in", "value": ["completed", "shipped"]}
    ],
    "version": "1.0.0"
}'
);

# This is showing how you can use a file in your procedures or functions.
CALL DATASCIENCE.CUSTOM_FUNCTIONS.HELLO_PROCEDURE('Developer we should expect our yaml to appear');
```

This guide provides a streamlined approach to setting up and deploying
your Snowflake environment with Snowpark. Customize as necessary to fit
your project’s requirements.
