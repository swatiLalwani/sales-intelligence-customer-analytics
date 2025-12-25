import pandas as pd
import pyodbc

# -----------------------------
# CONFIG
# -----------------------------
CSV_PATH = "customer_ai_insights.csv"

SERVER = "DESKTOP-CUKPVKG\SQLEXPRESS"
DATABASE = "DataWarehouseAnalytics"

TABLE = "gold.customer_ai_insights"

# -----------------------------
# CONNECT TO SQL SERVER
# -----------------------------
conn_str = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Trusted_Connection=yes;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

print("✅ Connected to SQL Server")

# -----------------------------
# LOAD CSV
# -----------------------------
df = pd.read_csv(CSV_PATH)
df = df.fillna("")

print(f"✅ Loaded {len(df)} AI insight rows")

# -----------------------------
# UPSERT QUERY (MERGE)
# -----------------------------
merge_sql = f"""
MERGE {TABLE} AS target
USING (VALUES (?, ?, ?, ?, ?)) AS source (
    customer_key,
    ai_explanation,
    ai_action,
    ai_confidence,
    generated_at
)
ON target.customer_key = source.customer_key

WHEN MATCHED THEN
    UPDATE SET
        ai_explanation = source.ai_explanation,
        ai_action = source.ai_action,
        ai_confidence = source.ai_confidence,
        generated_at = source.generated_at

WHEN NOT MATCHED THEN
    INSERT (
        customer_key,
        ai_explanation,
        ai_action,
        ai_confidence,
        generated_at
    )
    VALUES (
        source.customer_key,
        source.ai_explanation,
        source.ai_action,
        source.ai_confidence,
        source.generated_at
    );
"""

# -----------------------------
# EXECUTE UPSERT ROW BY ROW
# -----------------------------
rows_upserted = 0

for _, row in df.iterrows():
    cursor.execute(
        merge_sql,
        int(row["customer_key"]),
        row["ai_explanation"],
        row["ai_action"],
        row["ai_confidence"],
        row["generated_at"]
    )
    rows_upserted += 1

conn.commit()
cursor.close()
conn.close()

print(f"🎉 UPSERT complete — {rows_upserted} rows processed")
