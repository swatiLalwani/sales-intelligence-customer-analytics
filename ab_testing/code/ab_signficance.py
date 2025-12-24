import pandas as pd
import pyodbc
from scipy.stats import chi2_contingency, ttest_ind

SERVER = "DESKTOP-CUKPVKG\SQLEXPRESS"
DATABASE = "DataWarehouseAnalytics"
EXPERIMENT = "Retention_Offer_Test"

conn_str = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Trusted_Connection=yes;"
)

query = f"""
SELECT a.experiment_group,
       o.purchase_within_30d,
       o.revenue_within_30d
FROM gold.ab_customer_assignment a
JOIN gold.ab_test_outcomes o
  ON a.customer_key = o.customer_key
 AND a.experiment_name = o.experiment_name
WHERE a.experiment_name = '{EXPERIMENT}';
"""

conn = pyodbc.connect(conn_str, timeout=10)
df = pd.read_sql(query, conn)
conn.close()

A = df[df["experiment_group"] == "A"]
B = df[df["experiment_group"] == "B"]

ret_A = int(A["purchase_within_30d"].sum())
no_A  = int(len(A) - ret_A)
ret_B = int(B["purchase_within_30d"].sum())
no_B  = int(len(B) - ret_B)

# 1) Retention significance (Chi-square)
table = [[ret_A, no_A], [ret_B, no_B]]
chi2, p_ret, _, _ = chi2_contingency(table)

# 2) Revenue significance (t-test; use only purchasers or include zeros; choose one)
rev_A = A["revenue_within_30d"].astype(float)
rev_B = B["revenue_within_30d"].astype(float)
t_stat, p_rev = ttest_ind(rev_A, rev_B, equal_var=False)

rate_A = ret_A / len(A) if len(A) else 0
rate_B = ret_B / len(B) if len(B) else 0
lift = (rate_B - rate_A) / rate_A if rate_A else 0

print("=== A/B Test Summary ===")
print(f"Group A customers: {len(A)}, retention: {rate_A:.3f}")
print(f"Group B customers: {len(B)}, retention: {rate_B:.3f}")
print(f"Lift: {lift*100:.2f}%")
print(f"Retention p-value (chi-square): {p_ret:.4f}")
print(f"Revenue p-value (t-test): {p_rev:.4f}")
