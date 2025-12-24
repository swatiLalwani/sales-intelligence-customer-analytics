"""
===============================================================================
A/B Test Significance Analysis
===============================================================================
Purpose:
    - To evaluate the impact of a retention offer on at-risk customers.
    - To compare 30-day retention and revenue between Control (A) and Treatment (B).
    - To provide statistically valid evidence for or against rolling out the offer.

Business Context:
    - Customers are randomly assigned to:
        • Group A (Control): No retention offer.
        • Group B (Treatment): Receives a retention offer (e.g., email/incentive).
    - We want to know if Group B performs better than Group A in a meaningful way.

Data Inputs (from the data warehouse):
    - gold.ab_customer_assignment
        • experiment_group (A or B)
        • experiment_name (e.g., 'Retention_Offer_Test')
        • customer_key
    - gold.ab_test_outcomes
        • purchase_within_30d (0/1 flag for at least one purchase in 30 days)
        • revenue_within_30d (monetary value in the 30-day window)

Logic & Steps:
    1. Read experiment data from SQL Server into a Pandas DataFrame.
    2. Split data into:
        • Group A (Control)
        • Group B (Treatment)
    3. Compute:
        • Number of customers in each group.
        • 30-day retention rate per group.
        • Retention lift = (B - A) / A.
    4. Perform statistical tests:
        • Chi-square test on retention (purchase_within_30d) to check if differences
          between A and B are statistically significant.
        • Two-sample t-test on revenue_within_30d to compare average revenue.
    5. Print a concise summary that can be copied into documentation or a memo.

Key Python / Stats Libraries Used:
    - pandas: Data loading and manipulation.
    - pyodbc: SQL Server connectivity.
    - scipy.stats:
        • chi2_contingency: For retention rate significance.
        • ttest_ind: For revenue difference significance.

Outputs:
    - Console summary including:
        • Group sizes and retention rates.
        • Retention lift (%).
        • p-values for retention and revenue.
    - These values are referenced in the A/B Test Results Memo and README.

Usage:
    - Run this script after assignment and outcome tables are populated:
        python ab_significance.py
===============================================================================
"""
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
