# FinTrack ETL

ETL pipeline built with Python and Pandas that transforms FinTrack's transaction data into monthly financial reports, loaded back into PostgreSQL. Automated with cron inside a Docker container.

## What it does

This pipeline connects to FinTrack's PostgreSQL database and produces two reporting tables that FinTrack's API can later query directly, without recalculating aggregations on every request:

- **`reportes_mensuales`** — monthly balance per user (total income, expenses, savings, and net balance)
- **`reportes_categorias`** — monthly spending/income breakdown per user and category

## Tech Stack

- Python
- Pandas
- SQLAlchemy
- PostgreSQL (Neon cloud)
- Docker
- cron (automated daily execution inside the container)

## How the pipeline works

**Extract** — Reads raw transactions, categories, and active users from PostgreSQL using `pd.read_sql()` with a SQLAlchemy engine.

**Transform** — Using Pandas:
- Converts transaction dates into monthly periods
- Merges transactions with users and categories
- Aggregates amounts with `groupby()` + `unstack()`, grouped by user, month, and movement type (income/expense/savings)
- Calculates net balance (income − expenses)

**Load** — Before inserting new data, existing rows in the target table are deleted (not dropped) to keep report tables idempotent — running the pipeline multiple times never produces duplicate rows. Table names are validated against a whitelist before any delete operation, to avoid unsafe dynamic SQL.

## Running with Docker

Make sure you have Docker installed.

**Required environment variables** (create a `.env` file in the project root):

```
STRING_NEON_FINTRACK=your_postgresql_connection_string
```

**Steps:**

1. Clone the repository
2. Build the image:
   ```bash
   docker build -t fintrack-etl .
   ```
3. Run the container:
   ```bash
   docker run -d --name fintrack-cron --env-file .env fintrack-etl
   ```

## Automation

The container runs a `cron` job that automatically executes the pipeline every day, updating both report tables with the latest transaction data — no manual execution needed. The container stays alive indefinitely, waiting for its scheduled time (configured in UTC).

## Related project

This pipeline processes data produced by [FinTrack API](https://github.com/codewithpatrick0/fintrack), a personal finance tracking system built with FastAPI.