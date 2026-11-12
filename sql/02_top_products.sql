-- Top 10 products by realised revenue, with a window-function rank.
WITH product_sales AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        SUM(oi.quantity) AS units_sold,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_pct)) AS revenue
    FROM order_items AS oi
    JOIN orders AS o
        ON o.order_id = oi.order_id
    JOIN products AS p
        ON p.product_id = oi.product_id
    WHERE o.status = 'completed'
    GROUP BY p.product_id, p.product_name, p.category
)
SELECT
    RANK() OVER (ORDER BY revenue DESC) AS revenue_rank,
    product_name,
    category,
    units_sold,
    ROUND(revenue, 2) AS revenue
FROM product_sales
ORDER BY revenue DESC, product_name
LIMIT 10;
