-- Customer-segment performance based on completed orders only.
SELECT
    c.segment,
    COUNT(DISTINCT c.customer_id) AS customers,
    COUNT(DISTINCT o.order_id) AS completed_orders,
    ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_pct)), 2) AS revenue,
    ROUND(
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_pct))
        / COUNT(DISTINCT o.order_id),
        2
    ) AS avg_order_value,
    ROUND(
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_pct))
        / COUNT(DISTINCT c.customer_id),
        2
    ) AS revenue_per_customer
FROM customers AS c
JOIN orders AS o
    ON o.customer_id = c.customer_id
JOIN order_items AS oi
    ON oi.order_id = o.order_id
WHERE o.status = 'completed'
GROUP BY c.segment
ORDER BY revenue DESC;
