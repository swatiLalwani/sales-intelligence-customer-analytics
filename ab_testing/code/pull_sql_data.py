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

