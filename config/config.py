# import requires libraries and module
import pandas as pd
from pathlib import Path

BASE_DIR = Path().resolve()
DATA_DIR = BASE_DIR / 'data'
LOG_DIR = BASE_DIR / 'logs'

SCHEMA = {
            "olist_customers_dataset.csv" : {
                    "customer_id" : "string",
                    "customer_unique_id": "string",
                    "customer_zip_code_prefix": "string",
                    "customer_city" : "string",
                    "customer_state" : "string"
            },
            "olist_geolocation_dataset.csv" : {
                    "geolocation_zip_code_prefix" : "string",
                    "geolocation_lat" : "float64",
                    "geolocation_lng" : "float64",
                    "geolocation_city" : "string",
                    "geolocation_state" : "string"
            },
            "olist_order_items_dataset.csv" : {
                "order_id" : "string",
                "order_item_id" : "int64",
                "product_id" : "string",
                "seller_id" : "string",
                "shipping_limit_date" : "string",
                "price" : "float64",
                "freight_value" : "float64"

            },
            "olist_order_payments_dataset.csv" : {
                "order_id" : "string",
                "payment_sequential" : "int64",
                "payment_type" : "string",
                "payment_installments" : "int64",
                "payment_value" : "float64"

            },
            "olist_order_reviews_dataset.csv" : {
                "review_id" : "string",
                "order_id" : "string",
                "review_score" : "int64",
                "review_comment_title" : "string",
                "review_comment_message" : "string",
                "review_creation_date" : "string",
                "review_answer_timestamp" : "string"
            },
            "olist_orders_dataset.csv" : {
                "order_id" : "string",
                "customer_id" : "string",
                "order_status" : "string",
                "order_purchase_timestamp" : "string",
                "order_approved_at" : "string",
                "order_delivered_carrier_date" : "string",
                "order_delivered_customer_date" : "string",
                "order_estimated_delivery_date" : "string"
            },
            "olist_products_dataset.csv" : {
                "product_id" : "string",
                "product_category_name" : "string",
                "product_name_lenght" : "float64",
                "product_description_lenght" : "float64",
                "product_photos_qty" : "float64",
                "product_weight_g": "float64",
                "product_length_cm" : "float64",
                "product_height_cm": "float64",
                "product_width_cm" : "float64"
            },
            "olist_sellers_dataset.csv" : {
                "seller_id" : "string",
                "seller_zip_code_prefix" :"string",
                "seller_city" :"string",
                "seller_state" : "string"
            },
            "product_category_name_translation.csv" :{
                "product_category_name": "string",
                "product_category_name_english" : "string"
            }
    }




