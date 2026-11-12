from __future__ import annotations

import sqlite3

import pandas as pd
import pytest

import generate_data as gd
import run_analysis as ra

COMPLETED_ORDER_COUNT = "SELECT COUNT(*) FROM orders WHERE status = 'completed'"


@pytest.fixture(scope="session")
def project_db(tmp_path_factory):
    data_dir = tmp_path_factory.mktemp("sales_data")
    gd.generate_dataset(data_dir, n_orders=160, seed=21)
    db_path = data_dir / "sales.db"
    gd.build_database(data_dir, db_path)
    return db_path


@pytest.fixture(scope="session")
def frames(project_db, tmp_path_factory):
    out_dir = tmp_path_factory.mktemp("results")
    frames, summary = ra.run_all(project_db, out_dir=out_dir)
    return frames, summary


def query(project_db, sql: str):
    with sqlite3.connect(project_db) as connection:
        return pd.read_sql_query(sql, connection)


def test_every_query_returns_rows(frames):
    result_frames, summary = frames
    assert len(result_frames) == 8
    for name, frame in result_frames.items():
        assert not frame.empty, f"{name} returned no rows"
    assert "Synthetic demonstration data" in summary


def test_monthly_revenue_matches_independent_total(project_db, frames):
    result_frames, _ = frames
    monthly = result_frames["01_monthly_revenue"]
    expected = query(
        project_db,
        """
        SELECT ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_pct)), 2) AS revenue
        FROM order_items oi
        JOIN orders o ON o.order_id = oi.order_id
        WHERE o.status = 'completed'
        """,
    ).iloc[0, 0]

    assert len(monthly) == query(
        project_db,
        "SELECT COUNT(DISTINCT strftime('%Y-%m', order_date)) FROM orders WHERE status = 'completed'",
    ).iloc[0, 0]
    assert monthly["revenue"].sum() == pytest.approx(expected, abs=0.05)
    assert monthly["orders"].sum() == query(project_db, COMPLETED_ORDER_COUNT).iloc[0, 0]
    assert monthly["month"].is_monotonic_increasing


def test_top_products_sorted_and_limited(frames):
    result_frames, _ = frames
    products = result_frames["02_top_products"]

    assert len(products) == 10
    assert products["revenue"].is_monotonic_decreasing
    assert products["revenue_rank"].iloc[0] == 1
    assert products["revenue"].iloc[0] > 0


def test_category_shares_sum_to_100(frames):
    result_frames, _ = frames
    categories = result_frames["03_category_performance"]

    assert categories["revenue_share_pct"].sum() == pytest.approx(100.0, abs=0.2)
    assert (categories["margin_pct"] > 0).all()
    assert categories["revenue"].is_monotonic_decreasing


def test_regional_totals_match_completed_orders(project_db, frames):
    result_frames, _ = frames
    regions = result_frames["08_regional_performance"]
    completed = query(project_db, COMPLETED_ORDER_COUNT).iloc[0, 0]

    assert regions["completed_orders"].sum() == completed
    assert regions["revenue"].sum() == pytest.approx(
        result_frames["01_monthly_revenue"]["revenue"].sum(), abs=0.05
    )
    assert regions["revenue_share_pct"].sum() == pytest.approx(100.0, abs=0.2)
    assert regions["revenue"].is_monotonic_decreasing
    assert (regions["avg_order_value"] > 0).all()


def test_customer_segment_totals_match_completed_orders(project_db, frames):
    result_frames, _ = frames
    segments = result_frames["04_customer_segments"]
    completed = query(project_db, COMPLETED_ORDER_COUNT).iloc[0, 0]

    assert segments["completed_orders"].sum() == completed
    assert segments["revenue"].sum() == pytest.approx(
        result_frames["01_monthly_revenue"]["revenue"].sum(), abs=0.05
    )
    assert (segments["avg_order_value"] > 0).all()


def test_sales_rep_totals_match_completed_orders(project_db, frames):
    result_frames, _ = frames
    reps = result_frames["05_sales_rep_performance"]
    completed = query(project_db, COMPLETED_ORDER_COUNT).iloc[0, 0]

    assert reps["completed_orders"].sum() == completed
    assert reps["revenue_rank"].iloc[0] == 1
    assert reps["revenue_rank"].is_monotonic_increasing


def test_month_over_month_growth_is_correct(frames):
    result_frames, _ = frames
    growth = result_frames["06_monthly_growth"]

    assert pd.isna(growth["mom_growth_pct"].iloc[0])
    for index in range(1, len(growth)):
        previous = growth["previous_month_revenue"].iloc[index]
        current = growth["revenue"].iloc[index]
        expected = 100.0 * (current - previous) / previous
        assert growth["mom_growth_pct"].iloc[index] == pytest.approx(expected, abs=0.02)


def test_customer_tiers_partition_customers(frames, project_db):
    result_frames, _ = frames
    tiers = result_frames["07_customer_value_tiers"]

    assert len(tiers) == 4
    assert tiers["customers"].sum() == query(
        project_db,
        "SELECT COUNT(DISTINCT customer_id) FROM orders WHERE status = 'completed'",
    ).iloc[0, 0]


def test_results_are_reproducible(project_db, tmp_path):
    _, first_summary = ra.run_all(project_db, out_dir=tmp_path / "one")
    _, second_summary = ra.run_all(project_db, out_dir=tmp_path / "two")

    assert first_summary == second_summary
    for name in (
        "01_monthly_revenue",
        "02_top_products",
        "07_customer_value_tiers",
        "08_regional_performance",
    ):
        assert (tmp_path / "one" / f"{name}.csv").read_bytes() == (
            tmp_path / "two" / f"{name}.csv"
        ).read_bytes()
