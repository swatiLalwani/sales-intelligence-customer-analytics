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
