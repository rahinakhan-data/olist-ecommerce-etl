# Capstone Project: End-to-End ETL Pipeline for E-Commerce Analytics

**Program:** AlgoMind Academy — Data Engineering / Data Analyst Track
**Duration:** 3 Weeks
**Type:** Individual Capstone Project

---

## 1. Problem Statement

A retail analytics team needs a reliable, repeatable pipeline to turn scattered raw e-commerce data (orders, customers, products, sellers, payments, reviews) into a clean, query-ready dataset that business teams can use for reporting and decision-making.

**Your task:** Design and build a complete **ETL (Extract → Transform → Load) pipeline** that:
1. Extracts raw data from multiple related source files.
2. Cleans, validates, and transforms it into an analytics-ready schema.
3. Loads the result into a structured database (data warehouse style).
4. Is automated, logged, documented, and reproducible — not a one-off notebook.

The final deliverable is a working pipeline (script or orchestrated DAG) + a clean database + a short analytical report proving the data is usable.

---

## 2. Dataset & Metadata

**Dataset:** Brazilian E-Commerce Public Dataset by Olist (Kaggle)
**Source:** https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
**License:** CC BY-NC-SA 4.0 (free for academic/portfolio use)

| File | Rows (approx) | Description |
|---|---|---|
| `olist_orders_dataset.csv` | 99,441 | Order status, timestamps (purchase, approval, delivery) |
| `olist_order_items_dataset.csv` | 112,650 | Line items per order, price, freight value |
| `olist_customers_dataset.csv` | 99,441 | Customer ID, city, state, zip prefix |
| `olist_sellers_dataset.csv` | 3,095 | Seller ID, city, state |
| `olist_products_dataset.csv` | 32,951 | Product category, dimensions, weight |
| `olist_order_payments_dataset.csv` | 103,886 | Payment type, installments, value |
| `olist_order_reviews_dataset.csv` | 99,224 | Review score, comment, timestamps |
| `olist_geolocation_dataset.csv` | 1,000,163 | Zip prefix to lat/lng mapping |
| `product_category_name_translation.csv` | 71 | Portuguese → English category names |

**Why this dataset:** it's relational (forces real joins), has realistic messiness (nulls, duplicate zip codes, mixed languages, inconsistent timestamps), and is large enough to require proper engineering rather than a quick pandas hack.

**Alternate datasets** (if you want the student to choose): Superstore Sales (Kaggle), Northwind (SQL sample DB), or a public REST API such as `https://fakestoreapi.com` for an API-extraction variant.

---

## 3. Tech Stack (recommended)

- **Language:** Python 3.10+
- **Extract/Transform:** `pandas`, `sqlalchemy`
- **Load target:** PostgreSQL (or SQLite for a lighter setup) — Docker recommended
- **Orchestration:** Apache Airflow (or a simple `schedule`/cron script if Airflow is too heavy for the timeline)
- **Validation:** `great_expectations` or manual assertion checks
- **Logging:** Python `logging` module, log files per run
- **Version control:** Git + GitHub repo, one commit per milestone

---

## 4. Week-by-Week Plan

### Week 1 — Setup + Extract Layer
**Goal:** Working extraction layer that pulls all 9 files into a raw staging area, with logging and validation.

| Day | Task |
|---|---|
| 1 | Set up GitHub repo, folder structure (`/extract`, `/transform`, `/load`, `/logs`, `/config`), virtual env, install dependencies. Download dataset, inspect each file's schema manually. |
| 2 | Write `extract.py`: functions to read each CSV into a pandas DataFrame with explicit dtype handling. Add logging (start/end, row counts, errors). |
| 3 | Add data profiling: for each table, log null counts, duplicate counts, and basic stats. Save a "raw data profile" report. |
| 4 | Set up a local Postgres instance (Docker) as the staging database. Load raw (unmodified) tables into a `staging` schema. |
| 5 | Write a `run_extract.py` entry point that runs the whole extract step end-to-end with error handling. Push to GitHub. |

**Week 1 deliverable:** Raw data loaded into a `staging` schema in Postgres, with a data profiling report and clean extract logs.

---

### Week 2 — Transform Layer
**Goal:** Clean, validated, joined, analytics-ready tables.

| Day | Task |
|---|---|
| 1 | Design the target schema (star schema): fact table `fact_orders` + dimension tables `dim_customers`, `dim_products`, `dim_sellers`, `dim_date`. Draw the schema diagram before coding. |
| 2 | Write cleaning functions: handle nulls, fix data types (dates, currency), translate product categories to English, deduplicate rows. |
| 3 | Build the join logic: orders → order_items → payments → reviews → customers → products → sellers into `fact_orders`. |
| 4 | Add derived columns: delivery delay (actual vs estimated delivery date), order value, review sentiment flag (score ≥4 = positive). Add data quality assertions (e.g., no negative prices, no future dates). |
| 5 | Write `transform.py` + `run_transform.py`. Log every transformation step with before/after row counts. Push to GitHub. |

**Week 2 deliverable:** Fully transformed star schema in a `transform` staging area, with a data quality report showing what was fixed/dropped and why.

---

### Week 3 — Load, Orchestrate, and Report
**Goal:** Automated, scheduled pipeline + final analytical output + documentation.

| Day | Task |
|---|---|
| 1 | Write `load.py`: load final fact/dimension tables into a `warehouse` schema in Postgres. Handle incremental vs. full-refresh logic (pick one, justify the choice). |
| 2 | Orchestrate: wire extract → transform → load into a single Airflow DAG (or a scheduled script) with retries and failure alerts (even just an email/log alert). |
| 3 | Write 5–8 analytical SQL queries against the warehouse (e.g., revenue by state, top product categories, average delivery delay by region, review score vs. delivery delay correlation). |
| 4 | Build a short report/dashboard (a Jupyter notebook, a simple Power BI/Streamlit dashboard, or a markdown report with charts) presenting the findings. |
| 5 | Write final `README.md`: architecture diagram, setup instructions, schema diagram, how to run the pipeline, known limitations, and next steps. Final GitHub push + short recorded walkthrough (5 min). |

**Week 3 deliverable:** End-to-end automated pipeline + populated warehouse + analytical report + complete documentation.

---

## 5. Final Submission Checklist

- [ ] GitHub repo with clear commit history (not one giant final commit)
- [ ] `extract.py`, `transform.py`, `load.py` (or equivalent modules) — no logic in notebooks only
- [ ] Star schema diagram (image or draw.io link)
- [ ] Data quality / profiling report (raw vs. cleaned)
- [ ] Orchestration setup (Airflow DAG screenshot, or scheduler script)
- [ ] 5–8 analytical SQL queries with results
- [ ] Final report or dashboard with 3–5 key insights
- [ ] `README.md` with setup + run instructions
- [ ] Short (5 min) walkthrough video or live demo

## 6. Evaluation Rubric (suggested weights)

| Criterion | Weight |
|---|---|
| Correctness of extract/transform/load logic | 30% |
| Code quality, structure, logging, error handling | 20% |
| Data quality handling (nulls, duplicates, validation) | 15% |
| Orchestration/automation | 15% |
| Analytical insights + reporting | 10% |
| Documentation + presentation | 10% |

---

## 7. Step-by-Step Guidance Notes (for weekly check-ins)

- **Week 1 check-in:** Verify the student is not just loading data raw with `df.to_sql()` — they should show intentional dtype handling and logging, not defaults.
- **Week 2 check-in:** The star schema design is the most common bottleneck — review the diagram *before* they start coding the joins to avoid rework.
- **Week 3 check-in:** Push them to pick one orchestration approach and finish it rather than half-building Airflow and falling back to a plain script under time pressure — a completed simple version beats an incomplete complex one.
