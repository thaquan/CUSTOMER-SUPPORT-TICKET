# Customer Support Analytics - Portfolio Case Study

## Executive summary

This project converts 8,469 raw customer-support records into a reproducible analytical product spanning Python, SQL Server, dimensional modeling, DAX, and Power BI. The final deliverable is a five-page report that helps a Customer Experience team examine support demand, backlog, CSAT, resolution performance, and customer segments while keeping source-data limitations visible.

The work emphasizes analytical integrity. It does not disguise 1,365 negative temporal cycles, treat purchase dates as ticket-created dates, calculate product defect rates without sales denominators, or expose customer names and email addresses in the public model.

## Business problem

An online technology retailer needs a consistent view of its customer-support workload. Operational stakeholders want to know:

- how much work remains unresolved;
- which priorities, channels, products, and issue types generate demand;
- where customer satisfaction is weak;
- how long validated resolution cycles take;
- which customer and purchase cohorts deserve investigation.

The source is a public CC0 dataset rather than internal company data, so the project is framed as a realistic analytical simulation.

## Delivery architecture

```text
Kaggle CSV
   -> Bronze: immutable local source
   -> Python/pandas cleaning and validation
   -> Silver: analysis-ready ticket records
   -> Gold: FactTicket plus seven dimensions
   -> SQL Server: staging and typed analytics schemas
   -> Power BI: semantic model, 35 DAX measures, five report pages
   -> Power BI Service: private My Workspace deployment
```

Raw and generated CSV files remain local. Versioned JSON summaries record the Silver and Gold quality outcomes. The SQL and PBIP definitions are stored as source-controlled text.

## Data engineering approach

The Silver pipeline standardizes names and categories, removes exact duplicates, detects conflicting ticket identifiers, validates age and CSAT types, parses dates and timestamps, creates analytical flags, and generates deterministic pseudonymous customer keys.

The Gold pipeline produces a star schema with one ticket-level fact and dimensions for customer profile, product, issue, channel, priority, status, and purchase date. Validation prevents duplicate fact grain, orphaned foreign keys, broken dimension grain, and public PII leakage.

Latest validated evidence:

| Quality result | Value |
|---|---:|
| Raw rows | 8,469 |
| Silver rows | 8,469 |
| Gold fact rows | 8,469 |
| Duplicate ticket IDs | 0 |
| Missing Gold foreign keys | 0 |
| Invalid age, CSAT, date, or timestamp parses | 0 |
| Negative resolution cycles | 1,365 |

## Analytical model

`FactTicket` has a one-row-per-ticket grain and 21 fields. Seven many-to-one relationships connect it to conformed dimensions. A dedicated `_Measures` table contains 35 explicit DAX measures grouped into ticket volume, customer experience, resolution cycle, data quality, and purchase-cohort comparison folders.

Important semantic choices include:

- backlog means any ticket not classified as Closed;
- CSAT metrics use valid respondents and disclose response coverage;
- resolution cycle measures use the interval from first response to resolution;
- invalid negative cycles remain flagged and blank in duration metrics;
- year-over-year comparisons are purchase cohorts because ticket creation date is unavailable.

## Key findings

- The model contains 8,469 tickets: 2,769 closed and 5,700 unresolved, producing a 32.70% resolution rate and a 67.30% backlog rate.
- There are 2,769 valid CSAT responses, a 32.70% response rate. Average CSAT is 2.99, while 1,102 responses are rated 1 or 2, producing a 39.80% low-CSAT rate.
- Only 1,404 tickets have a valid resolution-cycle value. The average valid cycle is 454.68 minutes and the median is 380.50 minutes.
- Email has the highest observed channel volume at 2,143 tickets. Chat has the highest observed average CSAT at 3.08 and the lowest low-CSAT rate at 36.35% among channels.
- Refund Request / Hardware issue is the largest issue combination with 129 tickets.
- Canon EOS has the highest observed product ticket volume at 240 tickets, but this cannot be interpreted as a defect rate without product sales volume.
- The 1,365 negative temporal cycles represent 16.12% of all tickets and are excluded from valid duration calculations.

All segment findings are descriptive and should be used to prioritize investigation rather than claim causation.

## Power BI report design

The report uses five purpose-specific pages:

1. **Executive Overview** - purchase-cohort KPIs, demand, backlog, channel mix, and product context.
2. **Support Operations** - global workload, urgent backlog, priority risk, subject-level operations, and channel status mix.
3. **Customer Experience & CSAT** - response coverage, average score, low-score concentration, and the CSAT distribution.
4. **Resolution Performance** - validated-cycle coverage, duration, temporal-quality disclosure, and priority comparisons.
5. **Customer Segments** - demographic workload, product backlog ranking, CSAT sample context, and a segment risk map.

Every page includes navigation. Focusable visuals have alt text and unique tab order. Dense product visuals use ranked charts or tables with explicit scrolling cues.

## Recommendations

1. **Prioritize higher-urgency backlog.** Review the 783 Critical/High unresolved tickets first and monitor their share of backlog.
2. **Improve survey coverage.** A 32.70% CSAT response rate limits how confidently satisfaction findings generalize to all tickets.
3. **Investigate low-CSAT concentrations.** Use subject, channel, and product segments to select cases for qualitative review rather than infer causation from aggregate rates.
4. **Repair temporal instrumentation.** Add a reliable `ticket_created_at`, preserve event provenance, and prevent resolution timestamps from preceding first response.
5. **Add business denominators.** Product sales volume, agent capacity, SLA targets, and support cost would enable defect-rate, productivity, SLA, and financial analysis.

## Limitations

- The source has no explicit ticket-created timestamp.
- Purchase date describes the purchased product, not ticket arrival.
- The source time-field labels are ambiguous, although their values behave as timestamps.
- The dataset does not include agent, SLA, sales volume, revenue, or support-cost fields.
- CSAT analysis covers respondents only.
- Public screenshots are used because the university Power BI tenant blocks anonymous `Publish to web`; the report is deployed privately in Power BI Service.

## Outcome

The project demonstrates an end-to-end analytical workflow rather than a standalone dashboard. It combines reproducible transformations, quality gates, dimensional modeling, SQL validation, reusable DAX, accessible report design, deployment evidence, and transparent communication of uncertainty.
