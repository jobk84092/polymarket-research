# Analysis Prompt

Use this prompt as a starting point when asking an AI assistant (ChatGPT, Claude, Cursor, etc.) to analyse a Polymarket CSV snapshot.

---

## Prompt Template

```
You are a quantitative analyst reviewing prediction-market data from Polymarket.

I have a CSV snapshot with the following columns:
- snapshot_time  : UTC timestamp of when the data was pulled
- market_id      : unique integer market identifier
- question       : the market question (e.g. "Will X happen before Y?")
- slug           : URL slug
- category       : market category (may be null)
- endDate        : resolution date (ISO 8601)
- volume24hr     : rolling 24-hour trading volume in USD
- volume_total   : total lifetime trading volume in USD
- liquidity      : current liquidity in USD (may be null)
- outcomes       : JSON list of outcome labels (e.g. ["Yes","No"])
- outcomePrices  : JSON list of current implied probabilities (0–1, e.g. ["0.72","0.28"])

The snapshot was taken at: <SNAPSHOT_TIME>
Number of markets: <N>

Tasks:
1. Summarise the top 10 markets by 24h volume. For each, note the question, volume24hr, and the current YES price from outcomePrices.
2. Identify any markets where the YES price is between 0.40 and 0.60 (i.e. genuine toss-ups) with high liquidity.
3. Flag any markets with a volume24hr > $1 M and a YES price above 0.85 or below 0.15 (extreme conviction).
4. Group markets by category (where available) and show total liquidity per category.
5. Provide a plain-English paragraph summarising the most interesting findings.

Data (paste CSV here or describe the top rows):
<CSV_DATA>
```

---

## Usage Notes

- Replace `<SNAPSHOT_TIME>`, `<N>`, and `<CSV_DATA>` with real values.
- To get the data quickly: `python review_latest.py --rows 50 --export` then open `reports/review_top.csv`.
- For deeper analysis, open `notebooks/analysis.ipynb` which already loads and charts the CSVs.
- Keep sensitive market slugs or positions out of external AI tools if trading on this data.
