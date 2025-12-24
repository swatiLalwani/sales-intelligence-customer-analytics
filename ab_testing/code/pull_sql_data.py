"""
===============================================================================
Data Pull Script: Warehouse → Python DataFrame
===============================================================================
Purpose:
    - To connect to the SQL Server data warehouse and retrieve source data
      for downstream analytics, AI insight generation, and experimentation.
    - Designed for reuse in other scripts (AI predictions, A/B testing, churn).

Business Context:
    - This script is part of the Sales Intelligence / Customer Analytics project.
    - It allows analysts to pull sample or full datasets directly from the
      gold layer of the Medallion Architecture for offline analysis.

Data Source:
    - SQL Server: DESKTOP-CUKPVKG\SQLEXPRESS
    - Database: DataWarehouseAnalytics
    - Table/View Example: gold.v_ai_churn_input

Workflow:
    1. Establish trusted ODBC connection to SQL Server.
    2. Execute SQL query (customizable, currently TOP 5 preview).
    3. Return results as a Pandas DataFrame for further processing.
    4. Close connection gracefully and print status messages.

Use Cases:
    - Test connectivity to the warehouse
    - Validate data model and schema structure
    - Pull preview rows for development and notebook analysis
    - Support automation scripts for AI insight generation or A/B testing

Python & Database Tools:
    - pandas: Converts SQL query results to DataFrame for analysis
    - pyodbc: Manages SQL Server connection via ODBC Driver 17

Usage:
    Run directly from terminal or VS Code:
        python pull_sql_data.py

    Adapt the query string to pull any table/view:
        query = "SELECT * FROM gold.fact_sales"
        query = "SELECT * FROM gold.v_customer_churn_status"
        query = "SELECT * FROM gold.dim_customers"

Output:
    - Head of the result set printed to console
    - DataFrame stored in variable `df` for next steps
===============================================================================
"""

import pandas as pd
import pyodbc

server = "DESKTOP-CUKPVKG\SQLEXPRESS"
database = "DataWarehouseAnalytics"

print("✅ Building connection...")

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={server};"
    f"DATABASE={database};"
    "Trusted_Connection=yes;"
)

print("✅ Attempting to connect (10s timeout)...")
conn = pyodbc.connect(conn_str, timeout=10)

print("✅ Connected! Running query...")

query = "SELECT TOP (5) * FROM gold.v_ai_churn_input;"
df = pd.read_sql(query, conn)

print("✅ Query returned rows:", len(df))
print(df)

conn.close()
print("✅ Done")

