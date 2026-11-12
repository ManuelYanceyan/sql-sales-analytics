"""Run the SQL analyses and write reproducible CSV and Markdown outputs."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

import pandas as pd

from generate_data import DATA_DIR, DB_PATH, build_database, generate_dataset

BASE_DIR = Path(__file__).resolve().parent
SQL_DIR = BASE_DIR / "sql"
RESULTS_DIR = BASE_DIR / "results"


def ensure_database(db_path: Path | str = DB_PATH, data_dir: Path | str = DATA_DIR) -> Path:
    """Return an existing database, building it from CSV or fresh data if needed."""
    db_path = Path(db_path)
    data_dir = Path(data_dir)
    if db_path.exists():
        return db_path

    if not (data_dir / "orders.csv").exists():
        generate_dataset(data_dir)
    build_database(data_dir, db_path)
    return db_path


def run_query_file(connection: sqlite3.Connection, query_path: Path) -> pd.DataFrame:
    return pd.read_sql_query(query_path.read_text(encoding="utf-8"), connection)


def _money(value: float) -> str:
    return f"${value:,.2f}"


def _format(value) -> str:
    if isinstance(value, float):
        if value.is_integer():
            return f"{int(value):,}"
        return f"{value:,.2f}"
    return str(value)


def markdown_table(frame: pd.DataFrame) -> str:
    columns = list(frame.columns)
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for _, row in frame.iterrows():
        lines.append("| " + " | ".join(_format(row[column]) for column in columns) + " |")
    return "\n".join(lines)


def _scalar(connection: sqlite3.Connection, query: str):
    return connection.execute(query).fetchone()[0]


def build_summary(db_path: Path | str, frames: dict[str, pd.DataFrame]) -> str:
    with sqlite3.connect(db_path) as connection:
        total_orders = _scalar(connection, "SELECT COUNT(*) FROM orders")
        completed_orders = _scalar(
            connection, "SELECT COUNT(*) FROM orders WHERE status = 'completed'"
        )
        date_range = connection.execute(
            "SELECT MIN(order_date), MAX(order_date) FROM orders"
        ).fetchone()
        units_sold = _scalar(
            connection,
            """
            SELECT COALESCE(SUM(oi.quantity), 0)
            FROM order_items AS oi
            JOIN orders AS o ON o.order_id = oi.order_id
            WHERE o.status = 'completed'
            """,
        )
        revenue = _scalar(
            connection,
            """
            SELECT COALESCE(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_pct)), 0)
            FROM order_items AS oi
            JOIN orders AS o ON o.order_id = oi.order_id
            WHERE o.status = 'completed'
            """,
        )
        gross_revenue = _scalar(
            connection,
            """
            SELECT COALESCE(SUM(oi.quantity * oi.unit_price), 0)
            FROM order_items AS oi
            JOIN orders AS o ON o.order_id = oi.order_id
            WHERE o.status = 'completed'
            """,
        )
        active_customers = _scalar(
            connection,
            "SELECT COUNT(DISTINCT customer_id) FROM orders WHERE status = 'completed'",
        )

    monthly = frames["01_monthly_revenue"]
    products = frames["02_top_products"]
    categories = frames["03_category_performance"]
    growth = frames["06_monthly_growth"]
    tiers = frames["07_customer_value_tiers"]

    best_month = monthly.loc[monthly["revenue"].idxmax()]
    top_product = products.iloc[0]
    top_category = categories.iloc[0]
    last_growth = growth.iloc[-1]

    metrics = pd.DataFrame(
        [
            ("Orders in dataset", f"{total_orders:,}"),
            ("Completed orders", f"{completed_orders:,}"),
            ("Completion rate", f"{100.0 * completed_orders / total_orders:.1f}%"),
            ("Order date range", f"{date_range[0]} to {date_range[1]}"),
            ("Units sold (completed)", f"{int(units_sold):,}"),
            ("Gross revenue before discounts", _money(gross_revenue)),
            ("Realised revenue (after discounts)", _money(revenue)),
            ("Average order value", _money(revenue / completed_orders)),
            ("Active customers", f"{active_customers:,}"),
            ("Best month", f"{best_month['month']} ({_money(best_month['revenue'])})"),
            ("Top product", f"{top_product['product_name']} ({_money(top_product['revenue'])})"),
            ("Top category", f"{top_category['category']} ({top_category['revenue_share_pct']:.2f}% share)"),
            ("Latest month-over-month growth", f"{last_growth['mom_growth_pct']:.2f}%"),
        ],
        columns=["Metric", "Observed value"],
    )

    top_five = products.head(5)[["revenue_rank", "product_name", "category", "units_sold", "revenue"]]
    last_six_months = monthly.tail(6)
    tier_view = tiers.rename(columns={"revenue_quartile": "revenue_tier"}).copy()
    tier_view["revenue_tier"] = tier_view["revenue_tier"].astype(int)

    return "\n".join(
        [
            "# Sales Analytics - Observed Results",
            "",
            "> Synthetic demonstration data. These figures are not company results.",
            "",
            "## Headline metrics",
            "",
            markdown_table(metrics),
            "",
            "## Last six months",
            "",
            markdown_table(last_six_months),
            "",
            "## Top five products",
            "",
            markdown_table(top_five),
            "",
            "## Category performance",
            "",
            markdown_table(categories),
            "",
            "## Customer revenue tiers (1 = highest)",
            "",
            markdown_table(tier_view),
            "",
            "## Method notes",
            "",
            "- Revenue = quantity x unit price x (1 - discount percentage).",
            "- Cancelled and returned orders are excluded from revenue metrics.",
            "- Cost and margin use the product unit cost stored in the catalogue.",
            "- All values come from `data/sales.db`, built from the synthetic CSV files.",
            "- Monthly percentages use calendar months, not fiscal periods.",
        ]
    ) + "\n"


def run_all(
    db_path: Path | str = DB_PATH,
    sql_dir: Path | str = SQL_DIR,
    out_dir: Path | str = RESULTS_DIR,
) -> tuple[dict[str, pd.DataFrame], str]:
    """Execute every SQL file, save CSVs and write a Markdown summary."""
    db_path = ensure_database(db_path)
    sql_dir = Path(sql_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    frames: dict[str, pd.DataFrame] = {}
    with sqlite3.connect(db_path) as connection:
        for query_path in sorted(sql_dir.glob("*.sql")):
            frame = run_query_file(connection, query_path)
            frames[query_path.stem] = frame
            frame.to_csv(out_dir / f"{query_path.stem}.csv", index=False)

    summary = build_summary(db_path, frames)
    (out_dir / "summary.md").write_text(summary, encoding="utf-8")
    return frames, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default=str(DATA_DIR), help="Directory with CSV files")
    parser.add_argument("--db", default=None, help="SQLite database path")
    parser.add_argument("--sql-dir", default=str(SQL_DIR), help="Directory with .sql files")
    parser.add_argument("--out-dir", default=str(RESULTS_DIR), help="Directory for outputs")
    parser.add_argument("--refresh", action="store_true", help="Rebuild the database from CSV")
    parser.add_argument("--regenerate", action="store_true", help="Regenerate synthetic data first")
    parser.add_argument("--orders", type=int, default=800, help="Number of orders to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    db_path = Path(args.db) if args.db else data_dir / "sales.db"

    if args.regenerate:
        generate_dataset(data_dir, n_orders=args.orders, seed=args.seed)
        build_database(data_dir, db_path)
    elif args.refresh and db_path.exists():
        db_path.unlink()

    frames, summary = run_all(db_path=db_path, sql_dir=args.sql_dir, out_dir=args.out_dir)
    print(summary)
    print(f"Wrote {len(frames)} result tables to {args.out_dir}")


if __name__ == "__main__":
    main()
