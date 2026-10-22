-- =====================================================================================================
-- WEEK 3 - DAY 3: ANALYTICAL SQL QUERIES FOR OLIST WAREHOUSE
-- =====================================================================================================

-- 1. Total revenue by customer state
-- COMMENT: This query shows total sales from each state. 
-- It helps us find our biggest markets and where most customers live.
SELECT 
    c.customer_state,
    ROUND(SUM(f.price)::NUMERIC, 2) AS total_revenue
FROM warehouse.dim_customers c 
JOIN warehouse.fact_orders f ON c.customer_id = f.customer_id
GROUP BY c.customer_state  
ORDER BY total_revenue DESC;


-- 2. Top 10 product categories by revenue
-- COMMENT: This query shows the top 10 best-selling product categories. 
-- It helps the business team manage stock and decide what products to promote.
SELECT 
    p.product_category_name_english,
    ROUND(SUM(f.price)::NUMERIC, 2) AS revenue
FROM warehouse.dim_products p 
JOIN warehouse.fact_orders f ON p.product_id = f.product_id
GROUP BY p.product_category_name_english
ORDER BY revenue DESC
LIMIT 10;


-- 3. Monthly revenue trend (use dim_date)
-- COMMENT: This query shows how sales change month by month and year by year. 
-- It helps us see if sales go up during festival seasons or holidays.
SELECT 
    d.year, 
    d.month,
    ROUND(SUM(f.price)::NUMERIC, 2) AS revenue
FROM warehouse.dim_date d 
JOIN warehouse.fact_orders f ON d.date_key = f.order_purchase_date_key
GROUP BY d.year, d.month
ORDER BY d.year ASC, d.month ASC;  


-- 4. Average delivery delay by seller state
-- COMMENT: This query calculates the average delivery delay days for each seller state. 
-- It helps us find which states have slow shipping performance.
SELECT 
    s.seller_state,
    ROUND(AVG(f.delivery_delay_days)::NUMERIC, 2) AS average_delivery_delay
FROM warehouse.dim_sellers s 
JOIN warehouse.fact_orders f ON s.seller_id = f.seller_id
GROUP BY s.seller_state
ORDER BY average_delivery_delay DESC;


-- 5. Share of orders by payment type
-- COMMENT: This query shows the percentage of orders paid by credit card, voucher, etc. 
-- It helps us know which payment method our customers prefer the most.
SELECT 
    f.payment_type,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(COUNT(DISTINCT f.order_id)::NUMERIC / (SELECT COUNT(DISTINCT order_id) FROM warehouse.fact_orders) * 100, 2) AS payment_share_percentage,
    ROUND(SUM(f.payment_value)::NUMERIC, 2) AS total_payment_value
FROM warehouse.fact_orders f
GROUP BY f.payment_type
ORDER BY payment_share_percentage DESC;


-- 6. Average review score vs. delivery delay (does late delivery hurt reviews?)
-- COMMENT: This query checks if late delivery makes customers unhappy. 
-- It compares review ratings against on-time and late deliveries.
SELECT
    CASE
        WHEN f.delivery_delay_days = 0 THEN 'OnTime / Early'
        WHEN f.delivery_delay_days BETWEEN 1 AND 3 THEN '1-3 Days Late'
        WHEN f.delivery_delay_days BETWEEN 4 AND 7 THEN '4-7 Days Late'
        ELSE 'More than a Week Late'
    END AS delivery_performance,
    ROUND(AVG(f.review_score)::NUMERIC, 2) AS average_review_score,
    COUNT(f.order_id) AS total_orders
FROM warehouse.fact_orders f
WHERE f.review_score IS NOT NULL
GROUP BY 1
ORDER BY average_review_score DESC;


-- 7. Top 10 sellers by revenue
-- COMMENT: This query identifies the top 10 sellers who make the most money. 
-- The business can give rewards or support to keep these top sellers happy.
SELECT 
    s.seller_id, s.seller_city, s.seller_state,
    ROUND(SUM(f.price)::NUMERIC, 2) AS revenue
FROM warehouse.dim_sellers s 
JOIN warehouse.fact_orders f ON s.seller_id = f.seller_id
GROUP BY s.seller_id, s.seller_city, s.seller_state
ORDER BY revenue DESC
LIMIT 10;


-- 8. Order status breakdown (delivered, canceled, etc.)
-- COMMENT: This query shows the percentage of delivered, canceled, or processing orders. 
-- It highlights the cancellation rate and general business health.
SELECT 
    f.order_status,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(COUNT(DISTINCT f.order_id)::NUMERIC / (SELECT COUNT(DISTINCT order_id) FROM warehouse.fact_orders) * 100, 2) AS share_percentage
FROM warehouse.fact_orders f
GROUP BY f.order_status
ORDER BY share_percentage DESC;



