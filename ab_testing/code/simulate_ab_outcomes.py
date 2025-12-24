"""
===============================================================================
A/B Test Outcome Simulation
===============================================================================
Purpose:
    - To simulate 30-day retention and revenue outcomes for customers in an
      active A/B test.
    - To generate realistic experimental data when real campaign results are
      not yet available.
    - To populate the gold.ab_test_outcomes table for downstream analysis.

Business Context:
    - Customers have already been randomly assigned into:
        • Group A (Control): No retention offer.
        • Group B (Treatment): Receives a retention offer (e.g., discount or
          personalized retention email).
    - This script simulates how many customers in each group return to purchase
      within 30 days and how much revenue they generate.

Data Inputs (from the data warehouse):
    - gold.ab_customer_assignment
        • customer_key
        • experiment_group (A or B)
        • experiment_name (e.g., 'Retention_Offer_Test')

Simulation Logic:
    1. Read all customers assigned to the specified experiment from SQL Server.
    2. For each customer, use group-specific retention probabilities:
        • P_RETENTION_A for Control (A)
        • P_RETENTION_B for Treatment (B)
    3. For customers who "purchase" (simulated as a Bernoulli trial):
        • Draw a revenue value from a normal distribution with configurable
          mean (REV_MEAN) and standard deviation (REV_STD).
        • Ensure revenue is never negative.
    4. For non-purchasing customers:
        • Set revenue_within_30d = 0.
    5. Build a list of outcomes with:
        • customer_key
        • experiment_name
        • purchase_within_30d (0/1)
        • revenue_within_30d
        • evaluated_at (today's date)
    6. Upsert these outcomes into gold.ab_test_outcomes using a MERGE statement:
        • Update existing rows for the same customer + experiment.
        • Insert new rows when none exist.

Key Parameters You Can Tune:
    - P_RETENTION_A: Baseline retention probability for Control.
    - P_RETENTION_B: Expected improved retention for Treatment.
    - REV_MEAN / REV_STD: Revenue distribution for purchasing customers.
    - Random seed (set in numpy) to make simulations reproducible.

Python & Database Tools:
    - numpy: Random number generation for purchases and revenue.
    - pandas: Handling assignment data as a DataFrame.
    - pyodbc: SQL Server connectivity and MERGE execution.
    - datetime.date: To stamp evaluation date.

Outputs:
    - Records written (inserted/updated) into gold.ab_test_outcomes.
    - Console message summarizing how many rows were processed.

Usage:
    - Run after ab_customer_assignment is populated:
        python simulate_ab_outcomes.py

    - Follow with statistical analysis in ab_significance.py to measure
      retention lift and revenue impact for the experiment.
===============================================================================
"""

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
