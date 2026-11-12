from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

import generate_data as gd


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_generate_dataset_writes_expected_row_counts(tmp_path):
    counts = gd.generate_dataset(tmp_path, n_orders=120, seed=11)

    assert counts["customers"] == 140
    assert counts["products"] == 44
    assert counts["orders"] == 120
    assert counts["order_items"] > 120
    assert len(read_rows(tmp_path / "orders.csv")) == 120
    assert len(read_rows(tmp_path / "customers.csv")) == 140
    assert len(read_rows(tmp_path / "products.csv")) == 44


def test_generation_is_deterministic(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    gd.generate_dataset(first, n_orders=80, seed=123)
    gd.generate_dataset(second, n_orders=80, seed=123)

    for filename in ("customers.csv", "products.csv", "orders.csv", "order_items.csv"):
        assert (first / filename).read_bytes() == (second / filename).read_bytes()


def test_different_seeds_produce_different_orders(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    gd.generate_dataset(first, n_orders=80, seed=1)
    gd.generate_dataset(second, n_orders=80, seed=2)

    assert (first / "orders.csv").read_bytes() != (second / "orders.csv").read_bytes()


def test_database_has_valid_relationships_and_values(tmp_path):
    gd.generate_dataset(tmp_path, n_orders=150, seed=5)
    db_path = tmp_path / "sales.db"
    gd.build_database(tmp_path, db_path)

    with sqlite3.connect(db_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
        assert connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 150
        assert connection.execute(
            "SELECT COUNT(*) FROM orders WHERE status NOT IN ('completed', 'cancelled', 'returned')"
        ).fetchone()[0] == 0
        assert connection.execute(
            "SELECT COUNT(*) FROM order_items WHERE quantity <= 0 OR unit_price <= 0"
        ).fetchone()[0] == 0
        assert connection.execute(
            "SELECT COUNT(*) FROM order_items WHERE discount_pct < 0 OR discount_pct >= 1"
        ).fetchone()[0] == 0

        orphan_orders = connection.execute(
            """
            SELECT COUNT(*) FROM orders o
            LEFT JOIN customers c ON c.customer_id = o.customer_id
            WHERE c.customer_id IS NULL
            """
        ).fetchone()[0]
        assert orphan_orders == 0

        orphan_items = connection.execute(
            """
            SELECT COUNT(*) FROM order_items oi
            LEFT JOIN orders o ON o.order_id = oi.order_id
            LEFT JOIN products p ON p.product_id = oi.product_id
            WHERE o.order_id IS NULL OR p.product_id IS NULL
            """
        ).fetchone()[0]
        assert orphan_items == 0
