# DS 4320 Project 1: Next-Day S&P 500 Return Direction Modeling (Relational D1)

## Executive Summary

This repository contains Project 1 for DS 4320: a relational dataset (D1) with **four normalized tables** (tickers, daily_prices, daily_features, calendar), each exported as **CSV and Parquet**. D1 covers a **large S&P 500 universe** back to 1995 from Stooq (see `[data/sp500_universe_stooq_candidates.csv](data/sp500_universe_stooq_candidates.csv)`); regenerated files are **over 1 GB combined** and should be **hosted on UVA OneDrive** (link below), not committed to GitHub. The Python pipeline loads **CSV** into **DuckDB**, runs SQL joins, fits a pooled **Logistic Regression** (`statsmodels.Logit`) to predict next-day return direction (up/down), and visualizes log-odds factor coefficients with 95 % confidence intervals for factor significance analysis.

Name: Dailin Li  
NetID: esd4uq  
DOI: placeholder - add Zenodo or Figshare DOI when published
Press release: [press_release.md](press_release.md)  
Data (CSV + Parquet): [Link to the UVA Onedrive](https://myuva-my.sharepoint.com/:f:/g/personal/esd4uq_virginia_edu/IgCDxaIa4zERSKLURXKSjxkXAVPPBxN1ofQ0FZzqh9AaWfM?e=VWCCbM)  
Pipeline: [pipeline/project1_pipeline.ipynb](pipeline/project1_pipeline.ipynb) · [Markdown export](pipeline/project1_pipeline.md) - placeholder - add Markdown export when published
License: [LICENSE](LICENSE) (MIT)

**Environment:** `pip install -r requirements.txt` (includes `pyarrow` for Parquet export in `build_project1_data.py`).

## Problem Definition

### Item 1

The general problem is how to forecast stock prices. Specifically, we predict whether the next-day return is positive (up/down classification) across the S&P 500 universe. The relational dataset D1 is built from an S&P 500 candidate list with a long history to meet course scale requirements.

### Item 2 — Rationale for refinement

Narrowing the problem from "stock forecasting" to "next-day return regression on an S&P 500 universe using a relational feature dataset" makes it more tractable and reproducible. OLS linear regression produces interpretable coefficient estimates alongside standard errors and exact 95 % confidence intervals (\(\hat{\beta} \pm 1.96 \cdot \text{SE}\)), making it straightforward to assess which technical-indicator features have statistically meaningful associations with future returns. We construct a relational dataset (D1) with four normalized tables (tickers, daily_prices, daily_features, calendar) and train a model using lagged price-based features: 1-day return, 5-day rolling volatility, 5- and 20-day moving average deviations, 20-day momentum, and volume percent change. A strict date-based train/test split prevents look-ahead bias.

### Item 3 — Motivation

Equity return forecasting is one of the most studied problems in finance, yet it remains hard because the noisiness of market data and the randomness of contributing factors. Simple price-based features, such as moving averages, volatility, lagged returns have nonetheless been shown in the academic literature to carry small but measurable predictive content. S&P500 stocks are an ideal testbed as their data retain a high degree of accessibility, attract general attention, and retain high liquidity. Building a reproducible, transparent pipeline — from raw OHLCV data, to a normalized relational dataset, to a trained regression model — has practical value for retail investors and risk managers who want to understand what price signals can (and cannot) tell us about short-term movements. It also addresses the issue of data bias in the financial industry and demonstrates a rigorous practice in data science.

### Item 4 — Press release headline and link

**Headline:** [Simple Price Signals Can Forecast Next-Day S&P500 Returns — With Limits](press_release.md)

---

## Domain Exposition

### Item 1 — Terminology


| Term                | Definition                                                                                                 |
| ------------------- | ---------------------------------------------------------------------------------------------------------- |
| Adjusted close      | - Close adjusted for dividends and stock splits - Used for comparable returns; Stooq export aligns with D1 |
| S&P 500             | - Large-cap U.S. equity index (500 constituent stocks)                                                      |
| Look-ahead bias     | - Using future data in features or training - Mitigated with strict date-based train/test splits           |
| MAE                 | - Mean absolute error - Average absolute deviation between predicted and actual return                     |
| Momentum            | - Short-horizon persistence of return direction - Often captured via lagged return features                |
| Moving Average (MA) | - Rolling mean of close over a window (e.g. MA_5, MA_20) - Trend-smoothing indicator                       |
| OHLCV               | - Open, High, Low, Close, Volume - Standard daily price/volume fields for a traded equity                  |
| Return (1d)         | - Day-over-day percentage change in adjusted close - (close_t - close_{t-1}) / close_{t-1}                 |
| RMSE                | - Root mean squared error - Primary regression metric; penalizes large errors more than MAE                |
| Survivorship bias   | - Sample skewed toward stocks that still trade - Noted as a limitation in index-style universes           |
| Ticker              | Short symbol identifying a listed equity on an exchange (e.g. AAPL, META, GOOGL).                          |
| Volatility          | - Rolling standard deviation of daily returns (e.g. 5-day window) - Measures short-term price risk         |


### Item 2 — Domain paragraph

The project's domain is quantitative finance and financial data science, specifically in the short-horizon equity return forecasting profession. Financial data scientists in this domain use structured historical market data such as OHLCV prices and derived technical indicators to build predictive models for trading signals, risk management, and portfolio construction. The domain requires clear operational definitions (what "return" means, which adjusted price to use), rigorous data handling (no look-ahead bias, strict temporal splits), and transparent documentation of provenance and known biases (survivorship bias, market regime change).

### Item 3 — Background reading folder

[https://github.com/dylanlidailin/DS4320-Project1/tree/main/Background_reading](https://github.com/dylanlidailin/DS4320-Project1/tree/main/Background_reading)

### Item 4 — Readings summary table


| Title                                                                                         | Brief Description                                                                                                                                                           | Link                                                                                                                                                                                              |
| --------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Research on the Optimal Prediction Model of Stock Returns (Tech basket case study)           | Compares Linear Regression, Random Forest, and XGBoost for return prediction; finds simpler models often outperform complex ones. (Used as general background on model comparisons, not as the project universe.) | [126015296.pdf](Background_reading/126015296.pdf)                                                                                                                                                 |
| Understanding Look-Ahead Bias and How to Avoid It in Trading Strategies                       | Explains how look-ahead bias contaminates backtests and ML models in finance; outlines proper walk-forward validation and train/test practices.                             | [Understanding Look-Ahead Bias and How to Avoid It in Trading Strategies.pdf](Background_reading/Understanding%20Look-Ahead%20Bias%20and%20How%20to%20Avoid%20It%20in%20Trading%20Strategies.pdf) |
| Combining CNN and Transformers for Financial Time Series Prediction                           | J.P. Morgan AI Research paper combining CNNs and Transformers for short- and long-term stock return dependencies; demonstrates strong performance on S&P 500 intraday data. | [cnn_transformer_stock.pdf](Background_reading/cnn_transformer_stock.pdf)                                                                                                                         |
| Hybrid Machine Learning Models for Stock Market Forecasting: Integrating Technical Indicators | Evaluates hybrid ML models (LSTM-CNN) using technical indicators (MA, RSI, MACD) for long-term stock forecasting; benchmarks RMSE, MAE, and R² across approaches.           | [hybrid_ml_technical_indicators.pdf](Background_reading/hybrid_ml_technical_indicators.pdf)                                                                                                       |
| Scrooge: Analyzing Yahoo Financial Data In DuckDB                                             | Demonstrates using the Scrooge DuckDB extension to query Yahoo Finance historical OHLCV data with SQL; directly relevant to the D1 relational pipeline in this project.     | [duckdb_yahoo_finance.pdf](Background_reading/duckdb_yahoo_finance.pdf)                                                                                                                           |


## Data Creation

### Item 1 — Provenance

I created D1 for next-day **S&P 500** modeling using public daily data from Stooq ([https://stooq.com](https://stooq.com)). D1 is built from an S&P 500 candidate list in `[data/sp500_universe_stooq_candidates.csv](data/sp500_universe_stooq_candidates.csv)`, with history from **1995-01-01** through **2024-12-31** (clipped per symbol to available Stooq history). The relational layout is unchanged: four tables — tickers, daily_prices, daily_features, calendar — each written as **CSV and Parquet** by [data/build_project1_data.py](data/build_project1_data.py). The script verifies that the **eight files total more than 1 GB** (course scale rubric); expect a long run time reading bulk Stooq files. **Commit the script and universe CSV only**; upload the generated files to **OneDrive** and link them in the README above.

The feature table is derived from prices using lagged return, rolling volatility, moving-average levels/deviations, volume change, and next-day return target fields.

### Item 2 — Code table


| File                      | Brief description                                                                                                                              | Link                                                        |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| build_project1_data.py    | Downloads Stooq daily OHLCV for `tech_universe_stooq.csv`, builds D1 (four tables as CSV + Parquet), exits with error if combined size < 1 GB. | [build_project1_data.py](data/build_project1_data.py)       |
| build_project1_data.ipynb | Same pipeline for **Google Colab** (upload `tech_universe_stooq.csv`, set `OUT_DIR` if needed).                                                | [build_project1_data.ipynb](data/build_project1_data.ipynb) |
| tech_universe_stooq.csv   | Curated Stooq `.us` symbols and metadata used to scale D1.                                                                                     | [tech_universe_stooq.csv](data/tech_universe_stooq.csv)     |
| project1_pipeline.ipynb   | Loads CSV tables into DuckDB, runs SQL joins, fits a baseline linear model, plots coefficients.                                                | [project1_pipeline.ipynb](pipeline/project1_pipeline.ipynb) |


### Item 3 — Bias identification

Using an S&P 500-style universe can introduce bias because the constituent list is not the full equity market and can embed survivorship/selection effects depending on how the list is constructed. The period (2019-2024) contains unusual market regimes (pandemic crash/rebound, rate shocks), which can distort learned relationships. Data source conventions also matter: vendor-specific handling of splits, bad ticks, and symbol mapping can introduce systematic differences. Finally, engineered features based only on price/volume exclude fundamentals, macro variables, and news flow, which can create omitted-variable bias in downstream modeling.

### Item 4 — Bias mitigation

I mitigate these biases by using strict time-based train/test splits (past to future only), retaining symbol/date keys so rows are traceable back to raw prices, and documenting every transformation from raw OHLCV to engineered features. I frame results as a proof-of-concept for this specific S&P 500 slice rather than universal market prediction. In analysis, I report out-of-sample metrics and interpret model outputs cautiously as weak signals, not causal effects.

### Item 5 — Rationale and uncertainty

*wenti - what counts as numerical uncertainty* CI!

Key judgement calls were: (1) using Stooq as a free reproducible source, (2) using an S&P 500-style universe for scale and interpretability, (3) setting the date window to 1995-2024, and (4) creating a normalized four-table schema instead of one flat file. I also explicitly chose a simple technical-indicator feature set and a next-day-return target so the pipeline remains transparent and reproducible.

Main uncertainty comes from market non-stationarity (relationships change over time), potential vendor differences in historical pricing conventions, and sensitivity of short-horizon return models to feature definitions and split boundaries.

## Metadata

### Item 1 — Logical schema (tables and keys)


| Table            | Primary key   | Key relationships                                                          |
| ---------------- | ------------- | -------------------------------------------------------------------------- |
| `tickers`        | `ticker_id`   | Parent table for symbols used by `daily_prices` and `daily_features`.      |
| `daily_prices`   | `price_id`    | `ticker_id` → `tickers.ticker_id`; one row per symbol-date trading record. |
| `daily_features` | `price_id`    | `price_id` → `daily_prices.price_id`; derived features per trading row.    |
| `calendar`       | `calendar_id` | Date dimension keyed by `trade_date` for time-based slicing.               |


### Item 2 — Data table (CSVs)


| Table            | Brief description                                                   | Link                                                                                      |
| ---------------- | ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `tickers`        | Symbol dimension (one row per successful download in the universe). | CSV: `data/tickers.csv` · Parquet: `data/tickers.parquet` (generate locally; same schema) |
| `daily_prices`   | Daily OHLCV + adjusted close per ticker-date.                       | CSV: `data/daily_prices.csv` · Parquet: `data/daily_prices.parquet`                       |
| `daily_features` | Engineered features and next-day return target keyed by `price_id`. | CSV: `data/daily_features.csv` · Parquet: `data/daily_features.parquet`                   |
| `calendar`       | Trading-date dimension.                                             | CSV: `data/calendar.csv` · Parquet: `data/calendar.parquet`                               |


### Item 3 — Data dictionary

See the full table in `[HW8/hw8-esd4uq.ipynb](../HW8/hw8-esd4uq.ipynb)` §8.2 Metadata Item 3, or the same columns documented inline in the pipeline notebook. Features include: `ticker_id`, `symbol`, `provider_symbol`, `company_name`, `sector`, `price_id`, `trade_date`, OHLCV, `adj_close_price`, `return_1d`, `volatility_5d`, `ma_5`, `ma_20`, `ma_5_dev`, `ma_20_dev`, `volume_pct_change`, `target_return_next_day`, and calendar fields.

### Item 4 — Numerical uncertainty


| Numerical feature                                                         | Uncertainty source                                                          | Quantification approach                                                                                                   |
| ------------------------------------------------------------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `open_price`, `high_price`, `low_price`, `close_price`, `adj_close_price` | Vendor rounding/adjustment conventions and occasional historical revisions. | Compare sampled dates against source endpoint; track max absolute difference and percentage difference during validation. |
| `volume`                                                                  | Reporting corrections and possible outlier spikes.                          | Report distribution (median, IQR, 99th percentile), and flag extreme z-score/IQR outliers by ticker.                      |
| `return_1d`, `target_return_next_day`                                     | Sensitive to close-price revisions and non-stationary market regimes.       | Report rolling mean/std by year; provide train/test drift summary and outlier-day counts.                                 |
| `volatility_5d`                                                           | Window-size sensitivity and missing values in early rows.                   | Count NA rows by ticker and compare volatility summaries under alternate windows (e.g., 5 vs 10 days).                    |
| `ma_5`, `ma_20`, `ma_5_dev`, `ma_20_dev`                                  | Choice of moving-average horizon changes scale/signals.                     | Document chosen windows and summarize feature correlation stability by subperiod.                                         |
| `volume_pct_change`                                                       | Heavy-tailed behavior near low-volume days.                                 | Report robust stats (median/IQR) and winsorized sensitivity checks.                                                       |


## Data

[Link to the UVA Onedrive](https://myuva-my.sharepoint.com/:f:/g/personal/esd4uq_virginia_edu/IgCDxaIa4zERSKLURXKSjxkXAVPPBxN1ofQ0FZzqh9AaWfM?e=VWCCbM)

## Problem Solution Pipeline


| Deliverable     | Link / note                                                                                                        |
| --------------- | ------------------------------------------------------------------------------------------------------------------ |
| Notebook        | [pipeline/project1_pipeline.ipynb](pipeline/project1_pipeline.ipynb)                                               |
| Markdown export | [pipeline/project1_pipeline.md](pipeline/project1_pipeline.md) *(generated via `jupyter nbconvert --to markdown`)* |
| DuckDB load     | See first code cells in the notebook                                                                               |
| SQL queries     | Example joins and filters in the notebook                                                                          |
| Model           | `statsmodels.Logit` on 6 lagged technical features (pooled — factor significance analysis)                                                          |
| Visualization   | Log-odds factor significance forest plot with 95 % CIs                                                                          |


**Homework copy:** The same pipeline logic also appears in `[HW8/hw8-esd4uq.ipynb](../HW8/hw8-esd4uq.ipynb)` under `# 8.2 Project 1` for course submission.

- Mint a **DOI** (e.g. Zenodo) and replace the placeholder above  