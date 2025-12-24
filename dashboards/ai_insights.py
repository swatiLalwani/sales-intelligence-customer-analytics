import pandas as pd
import pyodbc
from datetime import datetime

# -----------------------------
# 1) SQL Server connection
# -----------------------------
server = "DESKTOP-CUKPVKG\SQLEXPRESS"
database = "DataWarehouseAnalytics"

conn_str = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    "Trusted_Connection=yes;"
)

# -----------------------------
# 2) Pull input rows
# -----------------------------
QUERY = """
SELECT TOP (200)  -- start small for testing
    customer_key,
    country,
    risk_status,
    days_since_last_purchase,
    lifetime_orders,
    lifetime_revenue
FROM gold.v_ai_churn_input
ORDER BY days_since_last_purchase DESC;
"""

def generate_rule_based_insight(row: pd.Series) -> dict:
    """Fallback 'AI-like' explanation without calling any API."""
    days = int(row.get("days_since_last_purchase", 0) or 0)
    orders = int(row.get("lifetime_orders", 0) or 0)
    rev = float(row.get("lifetime_revenue", 0.0) or 0.0)
    status = str(row.get("risk_status", "") or "")
    country = str(row.get("country", "") or "")

    drivers = []
    if days >= 180:
        drivers.append(f"high inactivity ({days} days since last purchase)")
    elif days >= 90:
        drivers.append(f"declining recency ({days} days since last purchase)")
    if orders <= 2:
        drivers.append("low historical engagement (≤2 lifetime orders)")
    if rev < 1000:
        drivers.append("low lifetime value")
    elif rev >= 5000:
        drivers.append("meaningful lifetime value")

    if not drivers:
        drivers = ["recent engagement is moderate, but risk signals are present"]

    # Simple recommended action logic
    if status == "AT_RISK" and days >= 120:
        action = "Send a personalized reactivation email with a time-limited offer."
        confidence = "High" if days >= 180 else "Medium"
    elif status == "CHURNED":
        action = "Run a win-back campaign and survey the customer for churn reasons."
        confidence = "High"
    else:
        action = "Offer personalized recommendations based on prior purchases."
        confidence = "Medium"

    explanation = (
        f"Customer is {status} in {country} due to " + ", ".join(drivers) + "."
    )

    return {
        "ai_explanation": explanation[:480],
        "ai_action": action[:280],
        "ai_confidence": confidence
    }

def main():
    print("✅ Starting AI insights generation...")
    conn = pyodbc.connect(conn_str, timeout=10)
    df = pd.read_sql(QUERY, conn)
    conn.close()

    print(f"✅ Pulled {len(df)} rows from gold.v_ai_churn_input")

    # -----------------------------
    # 3) Generate insights
    # -----------------------------
    insights = []
    for _, row in df.iterrows():
        out = generate_rule_based_insight(row)
        insights.append({
            "customer_key": row["customer_key"],
            "ai_explanation": out["ai_explanation"],
            "ai_action": out["ai_action"],
            "ai_confidence": out["ai_confidence"],
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    out_df = pd.DataFrame(insights)

    # -----------------------------
    # 4) Save output (CSV)
    # -----------------------------
    out_df.to_csv("customer_ai_insights.csv", index=False)
    print("✅ Saved: customer_ai_insights.csv")
    print(out_df.head(5))

if __name__ == "__main__":
    main()
