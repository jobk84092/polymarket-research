# AI Rules

Guardrails, quality standards, and usage policies for AI-assisted work in this repository.

## Allowed Tools and Models

- **Cursor** (with GPT-4o or Claude Sonnet) for code generation and refactoring.
- **ChatGPT / Claude** for ad-hoc analysis, prompt drafting, and data interpretation.
- AI-generated code **must be reviewed and tested by a human** before merging.

## Prompting Standards

- Always provide context: include the file name, the task goal, and any relevant constraints.
- Use the prompt templates in `prompts/` as starting points — keep them updated as the project evolves.
- When asking AI to write or modify a script, include the current `requirements.txt` so it knows which libraries are available.

## Citation and Evidence Requirements

- AI-generated analysis conclusions must cite the specific CSV snapshot used (filename + snapshot timestamp).
- If an AI suggests a number (e.g. total 24h volume, price level), cross-check it against `review_latest.py` or the raw CSV before publishing.
- Any AI-generated chart or summary included in a report must note "AI-assisted" in the caption.

## Code Quality

- All AI-generated Python must pass `ruff` (linting) and `black` (formatting) before committing.
- Run `pre-commit run --all-files` before pushing.
- Do not commit AI-generated code that contains `TODO`, `FIXME`, or placeholder strings like `<your_value_here>`.

## Data Handling

- Do not paste raw market data (CSVs, JSON responses) into external AI tools — use anonymised snippets or schema descriptions only.
- Never share Telegram bot tokens, API keys, or chat IDs with any AI assistant.

## Red-team / Safety Checks

- Before running any AI-suggested shell command, review it for destructive operations (`rm -rf`, `git push --force`, etc.).
- Test AI-generated API requests against the Gamma API sandbox or with a `limit=5` before full runs.

## Approval Workflow

1. Draft the AI-assisted change in a feature branch.
2. Self-review: does the output match what the prompt asked for?
3. Run tests / manual verification (`python review_latest.py`, notebook).
4. Commit and open a PR. Add the label **ai-assisted** to the PR.
5. Merge only after human review is complete.
