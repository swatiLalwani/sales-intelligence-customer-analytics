/*
===============================================================================
A/B Testing - Outcomes Table
===============================================================================
Purpose:
    - To store observed or simulated experiment results for each customer.
    - Tracks 30-day retention behavior and revenue impact after treatment.
    - Enables statistical analysis (chi-square, t-test) to determine if
      Treatment (B) performs better than Control (A).

Business Context:
    - This table is populated after the experiment has run or simulated
      (via campaign response, purchase data, or Python simulation).
    - Used to calculate metrics such as:
        • Retention Rate Difference
        • Revenue Impact
        • Uplift / Lift %
        • p-values for statistical significance

Table Description:
    gold.ab_test_outcomes
        • customer_key          → Unique customer identifier
        • experiment_name       → Name of the A/B test
        • purchase_within_30d   → 1 if customer purchased within 30 days, else 0
        • revenue_within_30d    → Revenue generated within the window
        • evaluated_at          → Date result was recorded

Primary Key:
    (customer_key, experiment_name)
    - Ensures only one outcome record per customer per experiment
    - Prevents duplicate evaluation rows

Data Flow:
    1. gold.ab_customer_assignment → customers enter experiment
    2. gold.ab_test_outcomes       → results captured (SQL or Python)
    3. ab_significance.py          → retrieves outcomes for analysis
    4. Results reported in A/B Test Memo

Usage Example:
    SELECT experiment_group, AVG(purchase_within_30d) AS retention_rate
    FROM gold.ab_customer_assignment a
    JOIN gold.ab_test_outcomes o USING (customer_key, experiment_name)
    GROUP BY experiment_group;
===============================================================================
*/

CREATE TABLE gold.ab_test_outcomes (
    customer_key BIGINT NOT NULL,
    experiment_name VARCHAR(100) NOT NULL,
    purchase_within_30d BIT NOT NULL,
    revenue_within_30d DECIMAL(18,2) NOT NULL,
    evaluated_at DATE NOT NULL,
    PRIMARY KEY (customer_key, experiment_name)
);
