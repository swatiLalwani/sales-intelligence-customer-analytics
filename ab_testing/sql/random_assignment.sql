/*
===============================================================================
A/B Testing - Random Assignment Script
===============================================================================
Purpose:
    - To randomly assign eligible customers into A/B experiment groups.
    - Ensures each customer receives a consistent assignment for the duration
      of the experiment (no swapping or duplication).
    - Supports controlled testing for retention offers and churn intervention.

Business Context:
    - Used to test if a retention offer improves reactivation and revenue.
    - Group A (Control): No offer / baseline performance.
    - Group B (Treatment): Receives retention incentive or communication.
    - Eligible customers are those classified as "AT_RISK" via churn logic.

Assignment Logic:
    - NEWID() + CHECKSUM() used to produce a pseudo-random split.
    - Even values assigned to 'A'; odd values assigned to 'B'.
    - WHERE NOT EXISTS prevents customers from being re-assigned.
    - Guarantees one assignment per experiment per customer.

Key Conditions:
    • Only assign customers who are AT_RISK.
    • Prevent duplicate enrollment in the same experiment.
    • Assignment date stored for time-based analysis.

Data Flow:
    1. Identify eligible customers (v_customer_churn_status)
    2. Assign A/B groups
    3. Insert into gold.ab_customer_assignment
    4. Outcomes tracked in gold.ab_test_outcomes
    5. Statistical testing done via ab_significance.py (Python)

Validation Check Example:
    SELECT experiment_group, COUNT(*)
    FROM gold.ab_customer_assignment
    WHERE experiment_name = 'Retention_Offer_Test'
    GROUP BY experiment_group;

Expected Result:
    - Roughly 50/50 split (minor variations acceptable)
    - No duplicate customer assignments
===============================================================================
*/

INSERT INTO gold.ab_customer_assignment (customer_key, experiment_name, experiment_group, assigned_at)
SELECT
    customer_key,
    'Retention_Offer_Test' AS experiment_name,
    CASE WHEN ABS(CHECKSUM(NEWID())) % 2 = 0 THEN 'A' ELSE 'B' END AS experiment_group,
    CAST(GETDATE() AS DATE) AS assigned_at
FROM gold.v_customer_churn_status
WHERE risk_status = 'AT_RISK'
  AND NOT EXISTS (
      SELECT 1
      FROM gold.ab_customer_assignment a
      WHERE a.customer_key = gold.v_customer_churn_status.customer_key
        AND a.experiment_name = 'Retention_Offer_Test'
  );
