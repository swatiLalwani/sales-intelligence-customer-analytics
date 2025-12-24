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
