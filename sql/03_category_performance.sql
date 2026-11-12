-- Revenue, gross margin and revenue share by product category.
WITH category_sales AS (
    SELECT
        p.category,
        SUM(oi.quantity) AS units_sold,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_pct)) AS revenue,
        SUM(oi.quantity * p.unit_cost) AS cost
    FROM order_items AS oi
    JOIN orders AS o
        ON o.order_id = oi.order_id
    JOIN products AS p
        ON p.product_id = oi.product_id
    WHERE o.status = 'completed'
    GROUP BY p.category
)
SELECT
    category,
    units_sold,
    ROUND(revenue, 2) AS revenue,
    ROUND(revenue - cost, 2) AS gross_margin,
    ROUND(100.0 * (revenue - cost) / revenue, 2) AS margin_pct,
    ROUND(100.0 * revenue / SUM(revenue) OVER (), 2) AS revenue_share_pct
FROM category_sales
ORDER BY revenue DESC;
