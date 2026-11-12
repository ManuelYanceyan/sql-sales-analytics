-- Revenue and customer activity by country, based on completed orders only.
WITH regional_sales AS (
    SELECT
        c.country,
        COUNT(DISTINCT c.customer_id) AS customers,
        COUNT(DISTINCT o.order_id) AS completed_orders,
        SUM(oi.quantity) AS units_sold,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_pct)) AS revenue
    FROM customers AS c
    JOIN orders AS o
        ON o.customer_id = c.customer_id
    JOIN order_items AS oi
        ON oi.order_id = o.order_id
    WHERE o.status = 'completed'
    GROUP BY c.country
)
SELECT
    country,
    customers,
    completed_orders,
    units_sold,
    ROUND(revenue, 2) AS revenue,
    ROUND(revenue / completed_orders, 2) AS avg_order_value,
    ROUND(100.0 * revenue / SUM(revenue) OVER (), 2) AS revenue_share_pct
FROM regional_sales
ORDER BY revenue DESC;
