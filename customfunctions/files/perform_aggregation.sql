CALL customfunctions.DEV.PERFORM_AGGREGATION(
'{
    "request_id": "AGG_001",
    "source_table": "customfunctions.dev.orders",
    "target_table": "customfunctions.dev.orders_aggregates",
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
