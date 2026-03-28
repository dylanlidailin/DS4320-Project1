# DS 4320 Project 1: Next-Day FAANG Return Modeling (Relational D1)

## Executive Summary

This repository contains **Project 1** for DS 4320: a **relational dataset (D1)** with **four normalized CSV tables** for five FAANG stocks (2019–2024), plus a **Python pipeline** that loads data into **DuckDB**, runs SQL joins, fits a **linear regression** baseline for next-day returns, and visualizes coefficients. Content is migrated from HW7 (problem definition, domain, press release) and HW8 §8.2 (data creation, metadata, pipeline check). Homework notebooks remain under `HW7/` and `HW8/`; this folder is the canonical project layout for the course rubric.

**Name:** Dylan Li  
**NetID:** esd4uq  
**DOI:** *(add Zenodo or Figshare DOI when published)*  
**Press release:** [press_release.md](press_release.md)  
**Data (CSV files):** [data/](data/) — also mirror on **UVA OneDrive** and paste your share link here: *(OneDrive URL TBD)*  
**Pipeline:** [pipeline/project1_pipeline.ipynb](pipeline/project1_pipeline.ipynb) · [Markdown export](pipeline/project1_pipeline.md)  
**License:** [LICENSE](LICENSE) (MIT)

---

## Problem Definition

### Item 1 — General and specific problem

The general problem is forecasting daily stock returns using publicly available market data. Specifically, using five years of daily OHLCV data (2019–2024) for the five FAANG stocks — Meta, Apple, Amazon, Netflix, and Alphabet — we construct a relational dataset (D1) with four normalized tables (`tickers`, `daily_prices`, `daily_features`, `calendar`) and train a regression model to predict each stock's next-day return using lagged price-based features: 1-day return, 5-day rolling volatility, and 5- and 20-day moving average deviations. A strict date-based train/test split prevents look-ahead bias.

### Item 2 — Rationale for refinement

Narrowing the problem from "stock forecasting" to "next-day return regression on a five-stock FAANG basket using a relational feature dataset" makes it tractable, reproducible, and honest. FAANG stocks are among the most liquid and data-rich equities available, ensuring consistent data quality and a coherent market segment. Predicting the actual return value (regression) rather than only direction provides a richer target with interpretable evaluation metrics (RMSE, MAE). Structuring data as a relational model — rather than a single flat file — enforces data discipline, separates raw prices from derived features, and satisfies the course requirement for a normalized relational D1. Strict temporal splits (train on past, evaluate on future-only) yield honest out-of-sample performance estimates.

### Item 3 — Motivation

Equity return forecasting is one of the most studied problems in finance, yet it remains hard: markets are noisy, conditions shift, and most signals are weak. Simple price-based technical features — moving averages, volatility, lagged returns — have nonetheless been shown in the academic literature to carry small but measurable predictive content. FAANG stocks are an ideal testbed: data is freely available, widely followed, and highly liquid. Building a reproducible, transparent pipeline — from raw OHLCV data, to a normalized relational dataset, to a trained regression model — has practical value for retail investors and risk managers who want to understand what price signals can (and cannot) tell us about short-term movements. It also demonstrates rigorous data science practice on real financial time series, including explicit handling of known biases.

### Item 4 — Press release headline and link

**Headline:** [Simple Price Signals Can Forecast Next-Day FAANG Returns — With Limits](press_release.md)

---

## Domain Exposition

### Item 1 — Terminology

- **FAANG:** Meta (formerly Facebook), Apple, Amazon, Netflix, Alphabet (Google) — five major U.S. technology stocks.
- **OHLCV:** Open, High, Low, Close, Volume; the standard daily price/volume columns for a traded equity.
- **Adjusted close:** Closing price adjusted for dividends and stock splits; used for consistent return calculations across time (here aligned with the Stooq export used for D1).
- **Return (1d):** Day-over-day percentage change in adjusted close: (close_t − close_{t−1}) / close_{t−1}.
- **Volatility:** Rolling standard deviation of daily returns over a window (e.g., 5 days); measures price risk.
- **Moving Average (MA):** Rolling mean of closing prices over a window (e.g., MA_5, MA_20); a trend-smoothing indicator.
- **Momentum:** Tendency of returns to persist in direction over a short window; often captured via lagged return features.
- **Look-ahead bias:** Error from using future data in feature engineering or model training; prevented via strict date-based splits.
- **Survivorship bias:** Bias from only including currently listed stocks; noted as a limitation since all FAANG names remain active.
- **RMSE:** Root Mean Squared Error; primary regression evaluation metric; penalizes large errors more than MAE.
- **MAE:** Mean Absolute Error; average absolute deviation between predicted and actual return.
- **Relational model:** Data organized in multiple normalized tables linked by primary/foreign keys; used in D1 design.
- **DuckDB:** In-process SQL OLAP database used to query relational CSV tables directly in Python notebooks.

### Item 2 — Domain paragraph

The project sits in the domain of quantitative finance and financial data science, specifically short-horizon equity return forecasting. Practitioners in this domain use structured historical market data — OHLCV prices and derived technical indicators — to build predictive models for trading signals, risk management, and portfolio construction. The domain requires clear operational definitions (what "return" means, which adjusted price to use), rigorous data handling (no look-ahead bias, strict temporal splits), and transparent documentation of provenance and known biases (survivorship bias, market regime change). For this project, we use five years of daily OHLCV data for the FAANG basket, construct a normalized relational dataset (D1) with four tables queryable via DuckDB, and train an interpretable linear regression model to forecast next-day returns — demonstrating reproducible data science practice on a real financial time series.

### Item 3 — Background reading folder

https://github.com/dylanlidailin/DS4320/tree/main/Project1/Background_reading

### Item 4 — Readings summary table

| Title | Brief Description | Link |
|-------|-------------------|------|
| Research on the Optimal Prediction Model of Stock Returns of FAANG+M | Compares Linear Regression, Random Forest, and XGBoost for return prediction on the FAANG+M basket; finds simpler models often outperform complex ones. | [126015296.pdf](Background_reading/126015296.pdf) |
| Understanding Look-Ahead Bias and How to Avoid It in Trading Strategies | Explains how look-ahead bias contaminates backtests and ML models in finance; outlines proper walk-forward validation and train/test practices. | [Understanding Look-Ahead Bias and How to Avoid It in Trading Strategies.pdf](Background_reading/Understanding%20Look-Ahead%20Bias%20and%20How%20to%20Avoid%20It%20in%20Trading%20Strategies.pdf) |
| Combining CNN and Transformers for Financial Time Series Prediction | J.P. Morgan AI Research paper combining CNNs and Transformers for short- and long-term stock return dependencies; demonstrates strong performance on S&P 500 intraday data. | [cnn_transformer_stock.pdf](Background_reading/cnn_transformer_stock.pdf) |
| Hybrid Machine Learning Models for Stock Market Forecasting: Integrating Technical Indicators | Evaluates hybrid ML models (LSTM-CNN) using technical indicators (MA, RSI, MACD) for long-term stock forecasting; benchmarks RMSE, MAE, and R² across approaches. | [hybrid_ml_technical_indicators.pdf](Background_reading/hybrid_ml_technical_indicators.pdf) |
| Scrooge: Analyzing Yahoo Financial Data In DuckDB | Demonstrates using the Scrooge DuckDB extension to query Yahoo Finance historical OHLCV data with SQL; directly relevant to the D1 relational pipeline in this project. | [duckdb_yahoo_finance.pdf](Background_reading/duckdb_yahoo_finance.pdf) |

---

## Data Creation

### Item 1 — Provenance

I created a Project 1 dataset for next-day FAANG return modeling using public daily market data from Stooq (https://stooq.com). I pulled daily OHLCV files for META, AAPL, AMZN, NFLX, and GOOGL over 2019-01-01 to 2024-12-31, then standardized and filtered them into a relational dataset.

The final dataset is D1 with four CSV tables (`tickers`, `daily_prices`, `daily_features`, `calendar`) under [`data/`](data/). The feature table is derived from prices using lagged return, rolling volatility, moving-average levels/deviations, and next-day return target fields. Regenerate with [`data/build_project1_data.py`](data/build_project1_data.py).

### Item 2 — Code table

| File | Brief description | Link |
|------|-------------------|------|
| `build_project1_data.py` | Downloads Stooq daily OHLCV data and builds the four relational CSV tables for D1. | [build_project1_data.py](data/build_project1_data.py) |
| `project1_pipeline.ipynb` | Loads CSV tables into DuckDB, runs SQL joins, fits a baseline linear model, plots coefficients. | [project1_pipeline.ipynb](pipeline/project1_pipeline.ipynb) |

### Item 3 — Bias identification

Bias can be introduced because this dataset only includes five large U.S. tech stocks (FAANG), so it is not representative of the full equity market. The period (2019-2024) contains unusual market regimes (pandemic crash/rebound, rate shocks), which can distort learned relationships. Data source conventions also matter: vendor-specific handling of splits, bad ticks, and symbol mapping can introduce systematic differences. Finally, engineered features based only on price/volume exclude fundamentals, macro variables, and news flow, which can create omitted-variable bias in downstream modeling.

### Item 4 — Bias mitigation

I mitigate these biases by using strict time-based train/test splits (past to future only), retaining symbol/date keys so rows are traceable back to raw prices, and documenting every transformation from raw OHLCV to engineered features. I also frame results as a proof-of-concept for this specific FAANG slice rather than universal market prediction. In analysis, I report out-of-sample metrics and interpret model outputs cautiously as weak signals, not causal effects.

### Item 5 — Rationale and uncertainty

Key judgement calls were: (1) using Stooq as a free reproducible source, (2) restricting to FAANG for consistency with the project scope, (3) setting the date window to 2019-2024, and (4) creating a normalized four-table schema instead of one flat file. I also explicitly chose a simple baseline feature set and a next-day-return target so the pipeline remains transparent and reproducible.

Main uncertainty comes from market non-stationarity (relationships change over time), potential vendor differences in historical pricing conventions, and sensitivity of short-horizon return models to feature definitions and split boundaries.

---

## Metadata

### Item 1 — Logical schema (tables and keys)

| Table | Primary key | Key relationships |
|------|-------------|-------------------|
| `tickers` | `ticker_id` | Parent table for symbols used by `daily_prices` and `daily_features`. |
| `daily_prices` | `price_id` | `ticker_id` → `tickers.ticker_id`; one row per symbol-date trading record. |
| `daily_features` | `price_id` | `price_id` → `daily_prices.price_id`; derived features per trading row. |
| `calendar` | `calendar_id` | Date dimension keyed by `trade_date` for time-based slicing. |

### Item 2 — Data table (CSVs)

| Table | Brief description | Link |
|------|-------------------|------|
| `tickers.csv` | Symbol lookup for FAANG tickers and company metadata. | [tickers.csv](data/tickers.csv) |
| `daily_prices.csv` | Daily OHLCV price table for each ticker-date. | [daily_prices.csv](data/daily_prices.csv) |
| `daily_features.csv` | Engineered lagged-return and moving-window feature table. | [daily_features.csv](data/daily_features.csv) |
| `calendar.csv` | Trading-date calendar dimension with year/month/weekday flags. | [calendar.csv](data/calendar.csv) |

### Item 3 — Data dictionary

See the full table in [`HW8/hw8-esd4uq.ipynb`](../HW8/hw8-esd4uq.ipynb) §8.2 Metadata Item 3, or the same columns documented inline in the pipeline notebook. Features include: `ticker_id`, `symbol`, `provider_symbol`, `company_name`, `sector`, `price_id`, `trade_date`, OHLCV, `adj_close_price`, `return_1d`, `volatility_5d`, `ma_5`, `ma_20`, `ma_5_dev`, `ma_20_dev`, `volume_pct_change`, `target_return_next_day`, and calendar fields.

### Item 4 — Numerical uncertainty

| Numerical feature | Uncertainty source | Quantification approach |
|-------------------|--------------------|-------------------------|
| `open_price`, `high_price`, `low_price`, `close_price`, `adj_close_price` | Vendor rounding/adjustment conventions and occasional historical revisions. | Compare sampled dates against source endpoint; track max absolute difference and percentage difference during validation. |
| `volume` | Reporting corrections and possible outlier spikes. | Report distribution (median, IQR, 99th percentile), and flag extreme z-score/IQR outliers by ticker. |
| `return_1d`, `target_return_next_day` | Sensitive to close-price revisions and non-stationary market regimes. | Report rolling mean/std by year; provide train/test drift summary and outlier-day counts. |
| `volatility_5d` | Window-size sensitivity and missing values in early rows. | Count NA rows by ticker and compare volatility summaries under alternate windows (e.g., 5 vs 10 days). |
| `ma_5`, `ma_20`, `ma_5_dev`, `ma_20_dev` | Choice of moving-average horizon changes scale/signals. | Document chosen windows and summarize feature correlation stability by subperiod. |
| `volume_pct_change` | Heavy-tailed behavior near low-volume days. | Report robust stats (median/IQR) and winsorized sensitivity checks. |

---

## Problem Solution Pipeline

| Deliverable | Link / note |
|-------------|-------------|
| Notebook | [pipeline/project1_pipeline.ipynb](pipeline/project1_pipeline.ipynb) |
| Markdown export | [pipeline/project1_pipeline.md](pipeline/project1_pipeline.md) *(generated via `jupyter nbconvert --to markdown`)* |
| DuckDB load | See first code cells in the notebook |
| SQL queries | Example joins and filters in the notebook |
| Model | `sklearn.linear_model.LinearRegression` on lagged technical features |
| Visualization | Coefficient bar chart (2024 holdout) |

**Homework copy:** The same pipeline logic also appears in [`HW8/hw8-esd4uq.ipynb`](../HW8/hw8-esd4uq.ipynb) under `# 8.2 Project 1` for course submission.

---

## Rubric checklist (remaining work)

- [ ] Add **UVA OneDrive** link next to data in this README  
- [ ] Mint a **DOI** (e.g. Zenodo) and replace the placeholder above  
- [ ] Expand **error handling** and **logging to file** in Python per rubric  
- [ ] Optional: **parquet** export and scale notes if pursuing those points  
