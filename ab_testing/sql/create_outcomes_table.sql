CREATE TABLE gold.ab_test_outcomes (
    customer_key BIGINT NOT NULL,
    experiment_name VARCHAR(100) NOT NULL,
    purchase_within_30d BIT NOT NULL,
    revenue_within_30d DECIMAL(18,2) NOT NULL,
    evaluated_at DATE NOT NULL,
    PRIMARY KEY (customer_key, experiment_name)
);
