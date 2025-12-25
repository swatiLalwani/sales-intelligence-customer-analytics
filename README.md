📊 Sales Intelligence & Customer Analytics
(Data Analyst Portfolio Project – SQL • Power BI • A/B Testing • Insight Automation)

This project showcases how a Data Analyst supports business decision-making using customer data.
It focuses on understanding behavior, identifying churn risk, testing retention strategies, and generating insights for action  and not building pipelines or engineering systems. 

🎯Purpose of this Project:
To help business teams answer:
Who are our most valuable customers?
Which customers are at risk and why?
How much revenue could churn cost us?
Does a retention offer measurably improve outcomes?
What action should we take for each customer?

🧠 What This Project Includes:
Category	What Was Done	Why It Matters
Exploratory Analysis	Segments, value tiers, inactivity patterns	Understand user behavior & drivers
Business KPIs	AOV, retention %, churn %, revenue at risk	Supports decision-making
Dashboards	Customer Behavior + Churn & Retention	Present insights to stakeholders
A/B Test	Measure retention offer impact with stats	Decide if investment is worth scaling
Automated Insights	Rule-based explanations & actions	Empowers CRM / marketing to act

📌 Dashboards (Power BI)
Customer Behavior Dashboard:
Lifetime value tiers
Repeat purchase behavior
Revenue contribution by segment
Customer engagement overview
📍 dashboards/Customer Behavior dashboard.pbix
📸 [dashboards/screenshots/customer behavior.png](https://github.com/swatiLalwani/sales-intelligence-customer-analytics/blob/main/dashboards/screenshots/customer%20behavior.png)

Churn & Retention Dashboard:
Churn rate / retention rate
Inactive customer groups
Revenue at risk
Days since last purchase
📍 dashboards/Customer churn dashboard.pbix
📸 [dashboards/screenshots/customer churn.png](https://github.com/swatiLalwani/sales-intelligence-customer-analytics/blob/main/dashboards/screenshots/customer%20churn.png)

🧪 A/B Testing for Retention Impact
| Step                           | File                                      |
| ------------------------------ | ----------------------------------------- |
| Assign control vs offer groups | `/ab_testing/sql/random_assignment.sql`   |
| Simulate or load results       | `/ab_testing/simulate_ab_outcomes.py`     |
| Validate experiment health     | `/ab_testing/sql/validate_assignment.sql` |
| Statistical significance test  | `/ab_testing/code/ab_significance.py`     |

🧪 Experiment Result:
Group A Retention: 17.6%
Group B Retention: 23.8%
Retention Lift: +35.3% improvement in Group B
p-value: 0.0006 (well below 0.05 threshold)

📊 Interpretation:
The retention offer significantly improved outcomes. Customers who received the offer (Group B) returned at a 35.3% higher rate than those who did not.
Since the p-value is 0.0006, this difference is statistically significant, meaning it is unlikely due to chance and reflects a real effect.

📍 Business Impact:
If rolled out at scale, this strategy is expected to:
Reactivate more inactive customers
Reduce churn rate
Recover revenue that would have been lost
Improve 30-day customer return performance

✅ Recommendation (Final):
Scale the retention offer to the broader at-risk segment.
Prioritize customers inactive 90+ days with:
Personalized email / SMS offer
Time-bound incentive
Follow-up to measure repeat behavior


🤖 AI Insight Automation 
A lightweight rules engine generates recommendations such as:
Reason: 180+ days inactivity, low repeat orders
Action: Send reactivation offer / incentive
Confidence: High

| Insight Task          | File                        |
| --------------------- | --------------------------- |
| Generate insights     | `ai_insights.py`            |
| Save to table         | `upsert_ai_insights.py`     |
| View used by Power BI | `automated_ai_insights.sql` |


📂 Repository Structure
sales-intelligence-customer-analytics/
│
├── datasets/                        # Source CRM/ERP data (CSV)
├── analytics/                       # SQL for analysis, KPIs, insights
│   ├── churn_analysis.sql
│   ├── customer_value_segments.sql
│   ├── revenue_at_risk.sql
│
├── dashboards/                      # Power BI reports + screenshots
│
├── ab_testing/                      # A/B assignment → results → significance
│   ├── sql/
│   ├── code/
│
├── ai_insights/                     # Insight generation & upload
│   ├── ai_insights.py
│   ├── upsert_ai_insights.py
│
├── docs/                            # BRD, use cases, user stories
│
└── README.md

🛠️ Tools Used
SQL Server → analysis queries & logic
Power BI → stakeholder reporting
Python → automated insights & data updates
A/B Testing → decision validation

📩 Contact
If you'd like a walkthrough or want to discuss this project for a role, feel free to reach out.

