/*
===============================================================================
Automated AI Insights – Data Warehouse Setup
===============================================================================
Purpose:
    - To prepare the data warehouse for AI-driven customer churn insights.
    - Creates a dedicated input view for at-risk / churned customers and a
      target table to store generated AI explanations and recommended actions.

Business Context:
    - Supports churn prevention and customer retention initiatives.
    - Enables Python/AI pipelines to:
        • Pull standardized churn risk features from gold.v_ai_churn_input.
        • Generate human-readable explanations and next-best-actions.
        • Persist insights into gold.customer_ai_insights for BI and CRM use.

Objects Created:
    1) View: gold.v_ai_churn_input
        - Filters customers to only:
            • AT_RISK
            • CHURNED
        - Exposes key features:
            • customer_key
            • country
            • risk_status
            • days_since_last_purchase
            • lifetime_revenue
            • lifetime_orders

    2) Table: gold.customer_ai_insights
        - Stores AI output per customer:
            • customer_key        (PK)
            • ai_explanation      (why the customer is at risk)
            • ai_action           (recommended retention action)
            • ai_confidence       ('High', 'Medium', etc.)
            • generated_at        (timestamp of AI generation)

Data Flow:
    1. gold.v_customer_churn_status
           ↓ (filtered)
       gold.v_ai_churn_input
           ↓ (Python / ai_insights.py)
       gold.customer_ai_insights
           ↓ (Power BI tooltip / CRM / reporting)

Usage Examples:
    - Populate insights via Python:
        • ai_insights.py
        • upsert_ai_insights.py
    - Consume insights in dashboards:
        • Join customer_ai_insights to churn/behavior views by customer_key.
    - Quick validation:
        SELECT TOP 10 *
        FROM gold.customer_ai_insights
        ORDER BY generated_at DESC;

Notes:
    - PRIMARY KEY on customer_key enforces one active AI insight per customer.
    - Insights can be refreshed by overwriting the record on regeneration.
===============================================================================
*/

CREATE OR ALTER VIEW gold.v_ai_churn_input AS
SELECT
    customer_key,
    country,
    risk_status,
    days_since_last_purchase,
    lifetime_revenue,
    lifetime_orders
FROM gold.v_customer_churn_status
WHERE risk_status IN ('AT_RISK', 'CHURNED');
GO
CREATE TABLE gold.customer_ai_insights (
    customer_key BIGINT NOT NULL,
    ai_explanation NVARCHAR(500) NULL,
    ai_action NVARCHAR(300) NULL,
    ai_confidence NVARCHAR(20) NULL,
    generated_at DATETIME2 NULL,
    PRIMARY KEY (customer_key)
);
SELECT TOP 10 *
FROM gold.customer_ai_insights
ORDER BY generated_at DESC;
