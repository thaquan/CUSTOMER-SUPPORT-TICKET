# Customer Support Analytics - Interview Guide

## How to use this guide

Use the 90-second version for an initial recruiter screen. Use the deeper answers when an interviewer asks about modeling, data quality, SQL, DAX, or dashboard decisions. Keep answers conversational and adapt them to the role.

## 30-second project summary

> I built an end-to-end customer-support analytics project using Python, SQL Server, dimensional modeling, DAX, and Power BI. I transformed 8,469 raw tickets into a validated star schema, added 21 automated tests and 34 SQL validation checks, and designed a five-page Power BI report with 35 measures. The main challenge was preserving analytical integrity because the source lacks a ticket-created timestamp and contains 1,365 negative temporal cycles.

## 90-second interview pitch

> The business scenario was a Customer Experience team that needed to understand ticket demand, backlog, satisfaction, resolution performance, and customer segments.
>
> I first audited 8,469 raw records and built a reproducible Python pipeline. The Silver layer standardizes categories, validates data types and timestamps, creates analytical flags, and pseudonymizes customer identity. The Gold layer produces one ticket-level fact table and seven dimensions.
>
> I then implemented separate staging and analytics schemas in SQL Server, with typed constraints, foreign keys, indexes, 34 model-validation checks, and eight reusable analysis outputs. In Power BI I built seven relationships and 35 explicit DAX measures across five pages.
>
> The most important decision was not to hide source limitations. The dataset has no ticket-created timestamp, so time analysis is labeled as purchase-cohort analysis. It also has 1,365 cases where resolution precedes first response. I flag those rows and exclude them from duration measures rather than taking an absolute value. The result is a portfolio project that demonstrates both technical delivery and responsible analytical communication.

## Architecture explanation

### Why Bronze, Silver, and Gold?

> Bronze preserves the source for traceability. Silver applies reusable cleaning and row-level quality flags while retaining local audit fields. Gold enforces the analytical grain, separates dimensions, removes public PII, and gives SQL Server and Power BI a stable contract. The separation makes failures easier to diagnose and prevents report logic from becoming a substitute for data engineering.

### Why use a star schema?

> A star schema gives Power BI clear filter propagation, reusable dimensions, simpler DAX, and a controlled ticket grain. It also makes data-quality checks explicit: each ticket ID must be unique and every foreign key must resolve to one dimension row.

### What is the fact-table grain?

> One row per validated support ticket. I verify that there are 8,469 fact rows and 8,469 unique ticket IDs.

### Why does DimCustomerProfile not represent a unique customer?

> The public model intentionally excludes customer identity. The dimension contains unique combinations of age, gender, and age band. It supports demographic analysis without implying that each row is a person or exposing name/email data.

## Data-quality questions

### Why did you not use `abs()` on negative durations?

> Taking an absolute value would manufacture a plausible number without evidence about which timestamp is wrong. I preserve a `dq_negative_resolution_cycle` flag and set the analytical duration to blank. That keeps the issue measurable while protecting average and median cycle KPIs.

### Why are there only 1,404 valid resolution cycles?

> Duration requires valid first-response and resolution timestamps in the correct order. Negative or otherwise invalid cycles are excluded. I expose both the valid sample count and the negative-cycle count so users can judge metric coverage.

### How is CSAT handled?

> CSAT accepts only valid values from 1 to 5. `Average CSAT` uses valid responses, and `Low CSAT Rate` divides ratings of 1 or 2 by valid CSAT responses. I also show `CSAT Response Rate` because only 32.70% of tickets contain a response.

### How did you handle PII?

> Customer name and email remain local in the Silver audit layer but are excluded from Gold, SQL analytics, and Power BI. The pipeline creates a deterministic pseudonymous customer key for controlled processing, while the public model exposes only demographic profiles.

### What automated checks exist?

> There are 21 Python unit/integration tests, 34 SQL validation checks, versioned Silver and Gold JSON quality summaries, PBIR validation, and rendered screenshot review for all five pages.

## SQL questions

### Why separate staging and analytics schemas?

> Staging accepts CSV-shaped text and provides a controlled landing area. Analytics converts those values into typed tables with constraints, keys, and relationships. This separation makes load failures auditable and prevents malformed source values from silently entering the analytical model.

### What SQL constraints did you use?

> Primary keys enforce fact and dimension identity, unique constraints enforce dimension grain, foreign keys enforce relationships, and check constraints protect age, date attributes, CSAT, and nonnegative duration rules. Fact foreign keys are indexed for joins.

### How would you make the load incremental?

> I would replace full truncation with a staged upsert. Dimensions would use deterministic business keys or hashes to detect new members. Fact records would be merged on `ticket_id`, with audit timestamps, batch IDs, rejected-row tables, and idempotent transaction handling.

### How would this move to production?

> I would parameterize paths and connections, store secrets outside code, orchestrate jobs, add schema-drift alerts, write quality metrics to an observability table, and deploy database changes through migrations. I would also separate development, test, and production workspaces.

## Power BI and DAX questions

### Why use explicit measures?

> Explicit measures define one reusable business meaning, control formatting, and reduce inconsistent ad-hoc aggregation across pages. The model has 35 measures grouped by business purpose.

### Explain Resolution Rate.

> `Closed Tickets` filters the current context to rows where `is_closed` is true. `Resolution Rate` divides that result by `Total Tickets` using `DIVIDE`, which handles a zero denominator safely.

### Why use median as well as average duration?

> Duration distributions can be skewed. Average describes total burden, while median provides a more robust typical case. Both use only validated nonnegative cycles.

### Why is the trend labeled purchase cohort?

> The source has `Date of Purchase` but no `ticket_created_at`. Using purchase date as a ticket-arrival trend would be misleading. The report therefore compares tickets associated with purchase cohorts and says explicitly that ticket creation date is unavailable.

### What does a cohort delta mean?

> It compares the latest selected purchase-year cohort with the previous purchase-year cohort while preserving other filters. Rate deltas use percentage points; volume and duration changes use percentages where appropriate.

### How did you improve accessibility?

> Each page has consistent navigation. All focusable visuals have alt text and a unique tab order. Labels disclose sample coverage and ambiguous metrics, and ranked charts replace overly dense visuals where needed.

## Business interpretation questions

### What would you recommend first?

> I would first review the 783 Critical/High backlog tickets because they combine unresolved status and urgency. I would also investigate the drivers of low CSAT, but only after checking sample size and collecting qualitative context.

### Is Chat the best channel?

> Chat has the highest observed average CSAT and lowest observed low-CSAT rate among channels, but the analysis is descriptive. Channel selection, ticket complexity, customer mix, and operational processes could confound the result.

### Is Canon EOS the worst product?

> No. It has the highest observed ticket volume, but a defect rate requires a sales or installed-base denominator. I describe it as support demand, not product quality.

### What data would you request next?

> Ticket-created timestamp, SLA targets, agent/team assignments, queue events, product sales volume, order value, contact reason history, reopen events, support cost, and survey-send metadata.

## Trade-offs and lessons learned

### What was the hardest part?

> The hardest part was designing useful time analysis without a ticket-created timestamp. The solution was to preserve purchase-date analysis but rename and explain it as cohort analysis rather than presenting a false operational trend.

### What would you improve with more time?

> I would add incremental loading, a cloud-accessible data source for scheduled refresh, mobile layout, automated semantic-model tests, deployment pipelines, and a public demo tenant. I would not add complexity before fixing source timestamp quality.

### What are you most proud of?

> The quality issues are first-class analytical outputs rather than hidden exceptions. The dashboard communicates not only KPI values but also whether the data supports the interpretation.

## Questions to ask the interviewer

- How does your team define ticket backlog and SLA compliance?
- Which data-quality failures create the most operational risk today?
- How are metric definitions governed across SQL and Power BI?
- Does the team use import, DirectQuery, or composite models, and why?
- How are reports tested before deployment?
- What distinguishes an effective analyst on this team after six months?

## Final reminders

- Say **purchase cohort**, not ticket trend.
- Say **first-response-to-resolution cycle**, not first-response time.
- State sample sizes before comparing CSAT or duration.
- Describe segment differences as associations, not causes.
- Do not call ticket volume a defect rate.
- Lead with the business decision, then explain the technical implementation.
