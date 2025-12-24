/*
===============================================================================
A/B Testing - Assignment Table
===============================================================================
Purpose:
    - To store customer assignments for A/B experiments.
    - Tracks which customers belong to Control (A) or Treatment (B).
    - Ensures consistent evaluation of experiment outcomes over time.

Business Context:
    - Used for marketing/retention experiments such as email offers,
      incentives, pricing tests, or feature exposure.
    - Each customer is assigned once per experiment to avoid bias or duplicate
      sampling.
    - Supports later analysis of activation, retention, and revenue lift.

Table Description:
    gold.ab_customer_assignment
        • customer_key       → Unique customer identifier
        • experiment_name    → Name of the test (e.g., 'Retention_Offer_Test')
        • experiment_group   → A (Control) or B (Treatment)
        • assigned_at        → Date customer was assigned

Primary Key:
    (customer_key, experiment_name)
    - Prevents duplicate enrollment
    - Ensures one assignment per experiment per customer

Usage:
    - Populated once before running an experiment.
    - Input to outcome simulation or actual campaign data.
    - Consumed by significance testing in Python (chi-square / t-test).

Example Query:
    SELECT experiment_group, COUNT(*)
    FROM gold.ab_customer_assignment
    WHERE experiment_name = 'Retention_Offer_Test'
    GROUP BY experiment_group;
===============================================================================
*/

CREATE TABLE gold.ab_customer_assignment (
    customer_key BIGINT NOT NULL,
    experiment_name VARCHAR(100) NOT NULL,
    experiment_group CHAR(1) NOT NULL,   -- 'A' or 'B'
    assigned_at DATE NOT NULL,
    PRIMARY KEY (customer_key, experiment_name)
);
