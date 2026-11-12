# Sales Analytics - Observed Results

> Synthetic demonstration data. These figures are not company results.

## Headline metrics

| Metric | Observed value |
| --- | --- |
| Orders in dataset | 800 |
| Completed orders | 671 |
| Completion rate | 83.9% |
| Order date range | 2024-01-02 to 2025-12-31 |
| Units sold (completed) | 3,720 |
| Gross revenue before discounts | $585,061.00 |
| Realised revenue (after discounts) | $559,338.00 |
| Average order value | $833.59 |
| Active customers | 139 |
| Best month | 2025-11 ($50,918.80) |
| Top product | Aurora Laptop 14 ($72,369.50) |
| Top category | Electronics (55.12% share) |
| Latest month-over-month growth | -36.49% |

## Last six months

| month | orders | units_sold | revenue |
| --- | --- | --- | --- |
| 2025-07 | 34 | 149 | 26,433.60 |
| 2025-08 | 34 | 198 | 35,937.85 |
| 2025-09 | 33 | 211 | 32,949.70 |
| 2025-10 | 36 | 153 | 22,735.20 |
| 2025-11 | 37 | 249 | 50,918.80 |
| 2025-12 | 49 | 260 | 32,340.55 |

## Top five products

| revenue_rank | product_name | category | units_sold | revenue |
| --- | --- | --- | --- | --- |
| 1 | Aurora Laptop 14 | Electronics | 83 | 72,369.50 |
| 2 | Aurora Laptop 16 | Electronics | 58 | 65,345.50 |
| 3 | Nova Phone X | Electronics | 71 | 43,839.95 |
| 4 | Lumen Projector | Electronics | 69 | 36,096.75 |
| 5 | Nova Tablet 11 | Electronics | 89 | 33,675.60 |

## Category performance

| category | units_sold | revenue | gross_margin | margin_pct | revenue_share_pct |
| --- | --- | --- | --- | --- | --- |
| Electronics | 807 | 308,303.85 | 84,689.85 | 27.47 | 55.12 |
| Office | 788 | 98,195.90 | 38,906.90 | 39.62 | 17.56 |
| Software | 547 | 66,911.30 | 54,347.30 | 81.22 | 11.96 |
| Accessories | 907 | 49,757.60 | 26,262.60 | 52.78 | 8.90 |
| Home | 671 | 36,169.35 | 16,908.35 | 46.75 | 6.47 |

## Customer revenue tiers (1 = highest)

| revenue_tier | customers | total_revenue | avg_revenue_per_customer |
| --- | --- | --- | --- |
| 1 | 35 | 294,349.75 | 8,409.99 |
| 2 | 35 | 142,967.55 | 4,084.79 |
| 3 | 35 | 85,630.95 | 2,446.60 |
| 4 | 34 | 36,389.75 | 1,070.29 |

## Method notes

- Revenue = quantity x unit price x (1 - discount percentage).
- Cancelled and returned orders are excluded from revenue metrics.
- Cost and margin use the product unit cost stored in the catalogue.
- All values come from `data/sales.db`, built from the synthetic CSV files.
- Monthly percentages use calendar months, not fiscal periods.
