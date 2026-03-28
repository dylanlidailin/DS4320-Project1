# Simple Price Signals Can Forecast Next-Day FAANG Returns — With Limits

## Hook

Millions of investors trade FAANG stocks every day, relying on news, gut feel, or simple rules. But what if a reproducible data pipeline — built from nothing more than publicly available daily price history — could identify which technical signals actually predict tomorrow's return, and by how much?

## Problem Statement

Stock prices are noisy. Short-term movements are driven by news, sentiment, and randomness that no model can fully capture. Yet decades of academic research show that simple price-based features — lagged returns, rolling volatility, moving averages — carry weak but measurable predictive content. We focused on the FAANG basket (Meta, Apple, Amazon, Netflix, Alphabet), assembled five years of daily OHLCV data into a normalized relational dataset with four tables, and asked: which features correlate most strongly with next-day return, and can a simple linear regression model exploit this relationship honestly out-of-sample?

## Solution Description

We built a four-table relational dataset (tickers, daily prices, engineered features, trading calendar) from free public OHLCV data for five FAANG stocks from 2019 to 2024. Using DuckDB to join and query these tables, we trained a linear regression model to predict each stock's next-day return using only features available at the prior close — 1-day lagged return, 5-day rolling volatility, and short- and long-term moving average deviations. The [pipeline notebook](pipeline/project1_pipeline.ipynb) produces coefficient plots and out-of-sample metrics. Results are modest and consistent with what the literature predicts for liquid large-cap equities.

## Chart

See the pipeline notebook: it generates a horizontal bar chart of linear regression coefficients on held-out 2024 data (`pipeline/project1_pipeline.ipynb`, final code cell). That figure is the primary visualization supporting this release.
