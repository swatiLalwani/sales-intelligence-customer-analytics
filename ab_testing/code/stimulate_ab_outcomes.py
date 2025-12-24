import numpy as np
import pandas as pd
import pyodbc
from datetime import date

# -----------------------------
# CONFIG
# -----------------------------
SERVER = "DESKTOP-CUKPVKG\SQLEXPRESS"
DATABASE = "DataWarehouseAnalytics"
EXPERIMENT = "Retention_Offer_Test"

# Retention probabilities (tune these)
P_RETENTION_A = 0.18   # 18% buy within 30 days
P_RETENTION_B = 0.24   # 24% buy within 30 days (lift)

# Revenue settings (if purchased)
REV_MEAN = 180.0
REV_STD = 60.0

conn_str = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Trusted_Connection=yes;"
)

# -----------------------------
# 1) Pull assignment data
# -----------------------------
query = f"""
SELECT customer_key, experiment_group
FROM gold.ab_customer_assignment
WHERE experiment_name = '{EXPERIMENT}';
"""

conn = pyodbc.connect(conn_str, timeout=10)
df = pd.read_sql(query, conn)
print(f"✅ Loaded assignments: {len(df)} customers")

# -----------------------------
# 2) Simulate outcomes
# -----------------------------
rng = np.random.default_rng(42)

def simulate_row(group: str):
    p = P_RETENTION_A if group == "A" else P_RETENTION_B
    purchased = rng.random() < p
    if purchased:
        revenue = max(0.0, rng.normal(REV_MEAN, REV_STD))
    else:
        revenue = 0.0
    return int(purchased), float(round(revenue, 2))

outcomes = []
today = date.today().isoformat()

for _, r in df.iterrows():
    purchased, revenue = simulate_row(r["experiment_group"])
    outcomes.append((
        int(r["customer_key"]),
        EXPERIMENT,
        purchased,
        revenue,
        today
    ))

# -----------------------------
# 3) Insert outcomes into SQL (UPSERT via MERGE)
# -----------------------------
merge_sql = """
MERGE gold.ab_test_outcomes AS target
USING (VALUES (?, ?, ?, ?, ?)) AS source (
    customer_key,
    experiment_name,
    purchase_within_30d,
    revenue_within_30d,
    evaluated_at
)
ON target.customer_key = source.customer_key
AND target.experiment_name = source.experiment_name

WHEN MATCHED THEN
    UPDATE SET
        purchase_within_30d = source.purchase_within_30d,
        revenue_within_30d = source.revenue_within_30d,
        evaluated_at = source.evaluated_at

WHEN NOT MATCHED THEN
    INSERT (customer_key, experiment_name, purchase_within_30d, revenue_within_30d, evaluated_at)
    VALUES (source.customer_key, source.experiment_name, source.purchase_within_30d, source.revenue_within_30d, source.evaluated_at);
"""

cur = conn.cursor()
for row in outcomes:
    cur.execute(merge_sql, row[0], row[1], row[2], row[3], row[4])

conn.commit()
cur.close()
conn.close()

print(f"🎉 Inserted/updated outcomes: {len(outcomes)} rows into gold.ab_test_outcomes")
