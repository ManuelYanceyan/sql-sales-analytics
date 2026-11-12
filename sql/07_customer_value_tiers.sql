-- Customers divided into revenue quartiles with NTILE.
WITH customer_revenue AS (
    SELECT
        c.customer_id,
        c.segment,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_pct)) AS revenue
    FROM customers AS c
    JOIN orders AS o
        ON o.customer_id = c.customer_id
    JOIN order_items AS oi
        ON oi.order_id = o.order_id
    WHERE o.status = 'completed'
    GROUP BY c.customer_id, c.segment
),
tiered AS (
    SELECT
        customer_id,
        segment,
        revenue,
        NTILE(4) OVER (ORDER BY revenue DESC) AS revenue_quartile
    FROM customer_revenue
)
SELECT
    revenue_quartile,
    COUNT(*) AS customers,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(AVG(revenue), 2) AS avg_revenue_per_customer
FROM tiered
GROUP BY revenue_quartile
ORDER BY revenue_quartile;
