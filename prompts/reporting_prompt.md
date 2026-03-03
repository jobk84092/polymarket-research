# Reporting Prompt

Use this prompt as a starting point when asking an AI assistant to draft a written report or summary from Polymarket data.

---

## Prompt Template

```
You are a market researcher writing a concise weekly briefing on prediction-market activity.

Source data: Polymarket snapshot taken at <SNAPSHOT_TIME>.
Dataset: top <N> markets ranked by 24-hour trading volume.

Write a structured briefing with the following sections:

### 1. Market Highlights (3–5 bullets)
- The highest-volume market and its current YES price.
- Any market that moved more than 10 percentage points since the prior snapshot (if rolling data is available).
- The market with the highest absolute liquidity.

### 2. Category Breakdown
A short paragraph summarising which categories (politics, sports, crypto, etc.) dominate volume this week and any notable shifts.

### 3. Extreme Probabilities
List markets where the YES price is ≥ 0.90 or ≤ 0.10, with volume > $500 k. These represent near-certainties the market has priced in.

### 4. Toss-ups to Watch
List markets where YES price is between 0.45 and 0.55 with liquidity > $500 k — genuine uncertainty worth monitoring.

### 5. Upcoming Resolutions
Markets with endDate within the next 7 days. Include the question, current YES price, and total volume.

### 6. One-paragraph Executive Summary
Plain English. Suitable for sharing with someone who doesn't follow prediction markets.

Tone: factual, neutral, data-driven. Avoid speculation. Cite figures directly from the data.

Data summary (top 20 rows):
<CSV_DATA>
```

---

## Usage Notes

- Replace `<SNAPSHOT_TIME>`, `<N>`, and `<CSV_DATA>` with values from `python review_latest.py --rows 20`.
- For the "extreme probabilities" and "toss-ups" sections, run `python review_latest.py --export` and filter in Excel or via pandas.
- Always note the snapshot time in the published report so readers know when the data was captured.
- Cross-check any numbers the AI produces against the raw CSV before publishing.
