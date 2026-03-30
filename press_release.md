# Simple Price Signals Can Forecast Next-Day FAANG Returns — With Limits

## Hook

Millions of investors trade FAANG stocks every day, relying on news, gut feel, or simple rules. But what if a reproducible data pipeline — built from nothing more than publicly available daily price history — could identify which technical signals actually predict tomorrow's return, and by how much?

## Problem Statement

Stock prices are noisy. Short-term movements are driven by news, sentiment, and randomness that no model can fully capture. Yet decades of academic research show that simple price-based features — lagged returns, rolling volatility, moving averages — carry weak but measurable predictive content. We focused on the FAANG basket (Meta, Apple, Amazon, Netflix, Alphabet), assembled five years of daily OHLCV data into a normalized relational dataset with four tables, and asked: which features correlate most strongly with next-day return, and can a simple linear regression model exploit this relationship honestly out-of-sample?

## Solution Description

*wenti - how audience-centred should this solution be?*

If you follow FAANG or you are learning financial data science, you can treat this project as a transparent teaching example: you see exactly which inputs go in, how they are joined in SQL, and how a simple linear model behaves out-of-sample. You get a four-table relational dataset (tickers, daily prices, engineered features, trading calendar) built from free public OHLCV data for five FAANG names from 2019 to 2024, plus a [pipeline notebook](pipeline/project1_pipeline.ipynb) you can rerun end-to-end. In your own run, DuckDB joins those tables; a linear regression then predicts next-day return using only information you would have had at the prior close — 1-day lagged return, 5-day rolling volatility, moving-average deviations, and volume change — so you can judge whether the relationship is strong or mostly noise. The reported test-period error and coefficients are there for you to inspect, not to promise profits: short-horizon returns stay hard to forecast, and this work is for education and research transparency, not personalized investment advice.

## Chart

Open the [pipeline notebook](pipeline/project1_pipeline.ipynb) (final code cell): you will see a horizontal bar chart of fitted linear regression coefficients estimated on training data and evaluated on held-out 2024 rows. Read it like this: each bar is one feature; the bar extends left or right of zero to show whether a one-unit move in that feature is associated with higher or lower next-day return in this pooled model; longer bars mean a larger fitted weight in magnitude. Compare bar length and direction to see which signals the model leaned on in-sample — then read the printed test metrics beside it to see how much of that structure survives out-of-sample. This figure supports understanding and discussion, not a buy-or-sell signal; markets change, and past fit does not guarantee future performance.
