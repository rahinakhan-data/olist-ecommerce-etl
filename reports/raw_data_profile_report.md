# Raw Data Profile Report 
---

Table : `olist_customers_dataset.csv`

Total Rows: 99441 
Total Columns: 5 
Duplicate Records: 0 
Null Values Summary
| column_name              |   null_counts |   null_percentage |
|:-------------------------|--------------:|------------------:|
| customer_id              |             0 |                 0 |
| customer_unique_id       |             0 |                 0 |
| customer_zip_code_prefix |             0 |                 0 |
| customer_city            |             0 |                 0 |
| customer_state           |             0 |                 0 |

Descriptive Statistics Summary
No numerical columns available for summary.



Table : `olist_geolocation_dataset.csv`

Total Rows: 1000163 
Total Columns: 5 
Duplicate Records: 261831 
Null Values Summary
| column_name                 |   null_counts |   null_percentage |
|:----------------------------|--------------:|------------------:|
| geolocation_zip_code_prefix |             0 |                 0 |
| geolocation_lat             |             0 |                 0 |
| geolocation_lng             |             0 |                 0 |
| geolocation_city            |             0 |                 0 |
| geolocation_state           |             0 |                 0 |

Descriptive Statistics Summary
|      |   geolocation_lat |   geolocation_lng |
|:-----|------------------:|------------------:|
| min  |            -36.61 |           -101.47 |
| mean |            -21.18 |            -46.39 |
| max  |             45.07 |            121.11 |



Table : `olist_order_items_dataset.csv`

Total Rows: 112650 
Total Columns: 7 
Duplicate Records: 0 
Null Values Summary
| column_name         |   null_counts |   null_percentage |
|:--------------------|--------------:|------------------:|
| order_id            |             0 |                 0 |
| order_item_id       |             0 |                 0 |
| product_id          |             0 |                 0 |
| seller_id           |             0 |                 0 |
| shipping_limit_date |             0 |                 0 |
| price               |             0 |                 0 |
| freight_value       |             0 |                 0 |

Descriptive Statistics Summary
|      |   price |   freight_value |
|:-----|--------:|----------------:|
| min  |    0.85 |            0    |
| mean |  120.65 |           19.99 |
| max  | 6735    |          409.68 |



Table : `olist_order_payments_dataset.csv`

Total Rows: 103886 
Total Columns: 5 
Duplicate Records: 0 
Null Values Summary
| column_name          |   null_counts |   null_percentage |
|:---------------------|--------------:|------------------:|
| order_id             |             0 |                 0 |
| payment_sequential   |             0 |                 0 |
| payment_type         |             0 |                 0 |
| payment_installments |             0 |                 0 |
| payment_value        |             0 |                 0 |

Descriptive Statistics Summary
|      |   payment_sequential |   payment_installments |   payment_value |
|:-----|---------------------:|-----------------------:|----------------:|
| min  |                 1    |                   0    |             0   |
| mean |                 1.09 |                   2.85 |           154.1 |
| max  |                29    |                  24    |         13664.1 |



Table : `olist_order_reviews_dataset.csv`

Total Rows: 99224 
Total Columns: 7 
Duplicate Records: 0 
Null Values Summary
| column_name             |   null_counts |   null_percentage |
|:------------------------|--------------:|------------------:|
| review_id               |             0 |              0    |
| order_id                |             0 |              0    |
| review_score            |             0 |              0    |
| review_comment_title    |         87656 |             88.34 |
| review_comment_message  |         58247 |             58.7  |
| review_creation_date    |             0 |              0    |
| review_answer_timestamp |             0 |              0    |

Descriptive Statistics Summary
|      |   review_score |
|:-----|---------------:|
| min  |           1    |
| mean |           4.09 |
| max  |           5    |



Table : `olist_orders_dataset.csv`

Total Rows: 99441 
Total Columns: 8 
Duplicate Records: 0 
Null Values Summary
| column_name                   |   null_counts |   null_percentage |
|:------------------------------|--------------:|------------------:|
| order_id                      |             0 |              0    |
| customer_id                   |             0 |              0    |
| order_status                  |             0 |              0    |
| order_purchase_timestamp      |             0 |              0    |
| order_approved_at             |           160 |              0.16 |
| order_delivered_carrier_date  |          1783 |              1.79 |
| order_delivered_customer_date |          2965 |              2.98 |
| order_estimated_delivery_date |             0 |              0    |

Descriptive Statistics Summary
No numerical columns available for summary.



Table : `olist_products_dataset.csv`

Total Rows: 32951 
Total Columns: 9 
Duplicate Records: 0 
Null Values Summary
| column_name                |   null_counts |   null_percentage |
|:---------------------------|--------------:|------------------:|
| product_id                 |             0 |              0    |
| product_category_name      |           610 |              1.85 |
| product_name_lenght        |           610 |              1.85 |
| product_description_lenght |           610 |              1.85 |
| product_photos_qty         |           610 |              1.85 |
| product_weight_g           |             2 |              0.01 |
| product_length_cm          |             2 |              0.01 |
| product_height_cm          |             2 |              0.01 |
| product_width_cm           |             2 |              0.01 |

Descriptive Statistics Summary
|      |   product_name_lenght |   product_description_lenght |   product_photos_qty |   product_weight_g |   product_length_cm |   product_height_cm |
|:-----|----------------------:|-----------------------------:|---------------------:|-------------------:|--------------------:|--------------------:|
| min  |                  5    |                          4   |                 1    |               0    |                7    |                2    |
| mean |                 48.48 |                        771.5 |                 2.19 |            2276.47 |               30.82 |               16.94 |
| max  |                 76    |                       3992   |                20    |           40425    |              105    |              105    |



Table : `olist_sellers_dataset.csv`

Total Rows: 3095 
Total Columns: 4 
Duplicate Records: 0 
Null Values Summary
| column_name            |   null_counts |   null_percentage |
|:-----------------------|--------------:|------------------:|
| seller_id              |             0 |                 0 |
| seller_zip_code_prefix |             0 |                 0 |
| seller_city            |             0 |                 0 |
| seller_state           |             0 |                 0 |

Descriptive Statistics Summary
No numerical columns available for summary.



Table : `product_category_name_translation.csv`

Total Rows: 71 
Total Columns: 2 
Duplicate Records: 0 
Null Values Summary
| column_name                   |   null_counts |   null_percentage |
|:------------------------------|--------------:|------------------:|
| product_category_name         |             0 |                 0 |
| product_category_name_english |             0 |                 0 |

Descriptive Statistics Summary
No numerical columns available for summary.



