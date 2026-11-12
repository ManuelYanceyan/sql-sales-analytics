-- Sales representative leaderboard with a dense rank.
WITH rep_sales AS (
    SELECT
        o.sales_rep,
        COUNT(DISTINCT o.order_id) AS completed_orders,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_pct)) AS revenue
    FROM orders AS o
    JOIN order_items AS oi
        ON oi.order_id = o.order_id
    WHERE o.status = 'completed'
    GROUP BY o.sales_rep
)
SELECT
    DENSE_RANK() OVER (ORDER BY revenue DESC) AS revenue_rank,
    sales_rep,
    completed_orders,
    ROUND(revenue, 2) AS revenue,
    ROUND(revenue / completed_orders, 2) AS avg_order_value
FROM rep_sales
ORDER BY revenue DESC;
