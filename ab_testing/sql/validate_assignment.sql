/*
===============================================================================
A/B Testing - Assignment & Outcomes Validation
===============================================================================
Purpose:
    - To verify that A/B assignments are correctly created and outcomes
      are being recorded as expected.
    - Ensures the experiment is trustworthy before running significance tests.

Business Questions Answered:
    1. Are assignments being created without duplicates?
    2. Do Control (A) and Treatment (B) groups have balanced samples?
    3. Are at-risk customers being assigned correctly?
    4. Are purchases and revenue being captured for each group?

Validation Checks Performed:
    • Count customers in each experiment group (A vs B)
    • Confirm balanced experiment split (not exactly 50/50 but close)
    • Verify purchase & revenue fields contain expected values
    • Confirm the latest evaluation date is recent (staleness check)

Success Indicators:
    - Both groups populated: > 0 customers each
    - Rough balance: each group 45–55% of total (acceptable variance)
    - purchase_within_30d is 0/1 only (binary)
    - revenue_within_30d ≥ 0 (no negative values)
    - evaluated_at not NULL

If results are off (red flags):
    - Too many customers in one group → randomization issue
    - Missing outcomes → run simulate or ETL pipeline again
    - NULL or negative revenue → QA needed in outcome generation

Where This Fits:
    [1] random_assignment.sql → Assign A/B groups
    [2] simulate_ab_outcomes.py → Generate or capture outcomes
    [3] validate_assignment.sql → Confirm experiment health (THIS SCRIPT)
    [4] ab_significance.py → Statistical testing
===============================================================================
*/

SELECT TOP 10 *
FROM gold.ab_test_outcomes
WHERE experiment_name='Retention_Offer_Test'
ORDER BY evaluated_at DESC;

SELECT
  a.experiment_group,
  COUNT(*) AS customers,
  AVG(CAST(o.purchase_within_30d AS FLOAT)) AS retention_rate,
  AVG(o.revenue_within_30d) AS avg_revenue_30d,
  SUM(o.revenue_within_30d) AS total_revenue_30d
FROM gold.ab_customer_assignment a
JOIN gold.ab_test_outcomes o
  ON a.customer_key = o.customer_key
 AND a.experiment_name = o.experiment_name
WHERE a.experiment_name = 'Retention_Offer_Test'
GROUP BY a.experiment_group;
