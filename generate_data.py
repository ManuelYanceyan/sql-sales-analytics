"""Generate a reproducible synthetic sales dataset and SQLite database.

All customers, products, sales representatives and transactions in this
project are fictional. The generator is seeded, so the same seed always
produces exactly the same CSV files.
"""

from __future__ import annotations

import argparse
import calendar
import csv
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "sales.db"

SEED = 42
N_ORDERS = 800
N_CUSTOMERS = 140
START_SIGNUP = date(2022, 1, 1)
ORDER_YEARS = (2024, 2025)

SEGMENTS = ("Consumer", "SMB", "Enterprise")
SEGMENT_WEIGHTS = (55, 35, 10)

COUNTRIES = {
    "Peru": ("Lima", "Huancayo", "Arequipa", "Trujillo"),
    "Chile": ("Santiago", "Valparaiso"),
    "Colombia": ("Bogota", "Medellin"),
    "Mexico": ("CDMX", "Guadalajara"),
    "Argentina": ("Buenos Aires", "Cordoba"),
}
COUNTRY_WEIGHTS = (50, 15, 15, 12, 8)

FIRST_NAMES = (
    "Valeria", "Jorge", "Camila", "Andres", "Daniela", "Luis", "Mariana",
    "Pablo", "Renata", "Sergio", "Elena", "Miguel", "Paula", "Ricardo",
    "Teresa", "Oscar", "Natalia", "Hugo", "Ines", "Bruno",
)
LAST_NAMES = (
    "Mendez", "Castro", "Rojas", "Vargas", "Salazar", "Paredes", "Fuentes",
    "Navarro", "Cordero", "Molina", "Aguilar", "Ponce", "Herrera", "Soto",
    "Campos",
)

SALES_REPS = (
    "Ana Torres", "Diego Salas", "Lucia Ramos",
    "Mateo Rojas", "Sofia Vega", "Rafael Paredes",
)
CHANNELS = ("Web", "Retail", "Partner", "Phone")
CHANNEL_WEIGHTS = (40, 25, 20, 15)
ORDER_STATUSES = ("completed", "cancelled", "returned")
STATUS_WEIGHTS = (86, 8, 6)

# (product_name, category, unit_price, unit_cost)
CATALOG = (
    ("Aurora Laptop 14", "Electronics", 899.00, 640.00),
    ("Aurora Laptop 16", "Electronics", 1199.00, 860.00),
    ("Nova Tablet 11", "Electronics", 399.00, 270.00),
    ("Nova Phone X", "Electronics", 649.00, 470.00),
    ("Vertex Monitor 27", "Electronics", 329.00, 215.00),
    ("Pulse Speaker", "Electronics", 89.00, 48.00),
    ("Orbit Webcam", "Electronics", 59.00, 31.00),
    ("Quantum SSD 1TB", "Electronics", 129.00, 82.00),
    ("Helix Router", "Electronics", 99.00, 57.00),
    ("Lumen Projector", "Electronics", 549.00, 390.00),
    ("Nimbus Mouse", "Accessories", 29.00, 12.00),
    ("Nimbus Keyboard", "Accessories", 79.00, 38.00),
    ("Cobalt USB-C Hub", "Accessories", 49.00, 22.00),
    ("Trail Backpack", "Accessories", 69.00, 30.00),
    ("Aero Headset", "Accessories", 119.00, 62.00),
    ("Grip Stand", "Accessories", 39.00, 15.00),
    ("Shield Sleeve", "Accessories", 34.00, 14.00),
    ("Flux Charger", "Accessories", 45.00, 19.00),
    ("Beacon Dock", "Accessories", 89.00, 41.00),
    ("Echo Stylus", "Accessories", 25.00, 9.00),
    ("Meridian Desk", "Office", 349.00, 210.00),
    ("Meridian Chair", "Office", 289.00, 175.00),
    ("Linea Lamp", "Office", 59.00, 26.00),
    ("Linea Shelf", "Office", 129.00, 64.00),
    ("Folio Cabinet", "Office", 219.00, 130.00),
    ("Folio Whiteboard", "Office", 149.00, 78.00),
    ("Compact Printer", "Office", 199.00, 128.00),
    ("Paper Pack", "Office", 12.00, 5.00),
    ("Archivo Binder", "Office", 9.00, 3.00),
    ("Grid Planner", "Office", 18.00, 7.00),
    ("Terra Mug", "Home", 14.00, 5.00),
    ("Terra Kettle", "Home", 49.00, 23.00),
    ("Halo Purifier", "Home", 229.00, 145.00),
    ("Halo Fan", "Home", 69.00, 33.00),
    ("Cozy Throw", "Home", 39.00, 16.00),
    ("Cozy Cushion", "Home", 29.00, 11.00),
    ("Verde Planter", "Home", 24.00, 9.00),
    ("Verde Vase", "Home", 32.00, 12.00),
    ("Orbit Office Suite", "Software", 199.00, 35.00),
    ("Orbit Security", "Software", 89.00, 15.00),
    ("Cloud Backup", "Software", 129.00, 28.00),
    ("Insight BI Starter", "Software", 249.00, 45.00),
    ("MailFlow Pro", "Software", 59.00, 9.00),
    ("FormCraft", "Software", 39.00, 6.00),
)

# A light seasonal pattern keeps the monthly analysis interesting.
MONTH_WEIGHTS = (6, 6, 7, 7, 8, 7, 7, 8, 9, 10, 11, 14)


def _weighted_choice(rng: random.Random, options, weights):
    return rng.choices(options, weights=weights, k=1)[0]


def _write_csv(path: Path, fieldnames, rows) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _generate_customers(rng: random.Random, count: int) -> list[dict]:
    combinations = [(first, last) for first in FIRST_NAMES for last in LAST_NAMES]
    rng.shuffle(combinations)
    countries = tuple(COUNTRIES)
    rows = []

    for index, (first, last) in enumerate(combinations[:count], start=1):
        country = _weighted_choice(rng, countries, COUNTRY_WEIGHTS)
        city = rng.choice(COUNTRIES[country])
        segment = _weighted_choice(rng, SEGMENTS, SEGMENT_WEIGHTS)
        signup = START_SIGNUP + timedelta(days=rng.randrange(0, 730))
        rows.append(
            {
                "customer_id": f"CUST-{index:04d}",
                "customer_name": f"{first} {last}",
                "segment": segment,
                "country": country,
                "city": city,
                "signup_date": signup.isoformat(),
            }
        )
    return rows


def _generate_orders(
    rng: random.Random, customers: list[dict], count: int
) -> tuple[list[dict], list[dict]]:
    dates = []
    for _ in range(count):
        year = ORDER_YEARS[0] if rng.random() < 0.45 else ORDER_YEARS[1]
        month = _weighted_choice(rng, range(1, 13), MONTH_WEIGHTS)
        day = rng.randint(1, calendar.monthrange(year, month)[1])
        dates.append(date(year, month, day))
    dates.sort()

    product_indexes = list(range(len(CATALOG)))
    orders = []
    items = []
    item_counter = 0

    for index, order_date in enumerate(dates, start=1):
        order_id = f"ORD-{index:05d}"
        customer = rng.choice(customers)
        channel = _weighted_choice(rng, CHANNELS, CHANNEL_WEIGHTS)
        status = _weighted_choice(rng, ORDER_STATUSES, STATUS_WEIGHTS)
        orders.append(
            {
                "order_id": order_id,
                "customer_id": customer["customer_id"],
                "order_date": order_date.isoformat(),
                "channel": channel,
                "status": status,
                "sales_rep": rng.choice(SALES_REPS),
            }
        )

        number_of_items = rng.choices((1, 2, 3, 4), weights=(45, 30, 18, 7), k=1)[0]
        chosen_products = rng.sample(product_indexes, k=number_of_items)

        for product_index in chosen_products:
            item_counter += 1
            _product_name, _category, price, _cost = CATALOG[product_index]

            if channel == "Partner":
                discount = rng.choices((0.05, 0.10, 0.15), weights=(20, 50, 30), k=1)[0]
            elif channel == "Web":
                discount = rng.choices((0.0, 0.05, 0.10), weights=(50, 30, 20), k=1)[0]
            elif channel == "Phone":
                discount = rng.choices((0.0, 0.10), weights=(80, 20), k=1)[0]
            else:
                discount = rng.choices((0.0, 0.05), weights=(70, 30), k=1)[0]

            items.append(
                {
                    "order_item_id": f"ITEM-{item_counter:06d}",
                    "order_id": order_id,
                    "product_id": f"PROD-{product_index + 1:03d}",
                    "quantity": rng.randint(1, 5),
                    "unit_price": f"{price:.2f}",
                    "discount_pct": f"{discount:.2f}",
                }
            )

    return orders, items


def generate_dataset(
    out_dir: Path | str = DATA_DIR,
    n_orders: int = N_ORDERS,
    seed: int = SEED,
    n_customers: int = N_CUSTOMERS,
) -> dict[str, int]:
    """Write customers, products, orders and order_items CSV files."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    rng = random.Random(seed)
    customers = _generate_customers(rng, n_customers)
    products = [
        {
            "product_id": f"PROD-{index:03d}",
            "product_name": name,
            "category": category,
            "unit_price": f"{price:.2f}",
            "unit_cost": f"{cost:.2f}",
        }
        for index, (name, category, price, cost) in enumerate(CATALOG, start=1)
    ]
    orders, items = _generate_orders(rng, customers, n_orders)

    _write_csv(
        out / "customers.csv",
        ("customer_id", "customer_name", "segment", "country", "city", "signup_date"),
        customers,
    )
    _write_csv(
        out / "products.csv",
        ("product_id", "product_name", "category", "unit_price", "unit_cost"),
        products,
    )
    _write_csv(
        out / "orders.csv",
        ("order_id", "customer_id", "order_date", "channel", "status", "sales_rep"),
        orders,
    )
    _write_csv(
        out / "order_items.csv",
        ("order_item_id", "order_id", "product_id", "quantity", "unit_price", "discount_pct"),
        items,
    )

    return {
        "customers": len(customers),
        "products": len(products),
        "orders": len(orders),
        "order_items": len(items),
    }


def _read_dicts(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build_database(data_dir: Path | str = DATA_DIR, db_path: Path | str = DB_PATH) -> Path:
    """Load the generated CSV files into a fresh SQLite database."""
    data_dir = Path(data_dir)
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    schema = (BASE_DIR / "schema.sql").read_text(encoding="utf-8")

    customers = _read_dicts(data_dir / "customers.csv")
    products = _read_dicts(data_dir / "products.csv")
    orders = _read_dicts(data_dir / "orders.csv")
    items = _read_dicts(data_dir / "order_items.csv")

    connection = sqlite3.connect(db_path)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(schema)

        connection.executemany(
            "INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)",
            [
                (
                    row["customer_id"], row["customer_name"], row["segment"],
                    row["country"], row["city"], row["signup_date"],
                )
                for row in customers
            ],
        )
        connection.executemany(
            "INSERT INTO products VALUES (?, ?, ?, ?, ?)",
            [
                (
                    row["product_id"], row["product_name"], row["category"],
                    float(row["unit_price"]), float(row["unit_cost"]),
                )
                for row in products
            ],
        )
        connection.executemany(
            "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)",
            [
                (
                    row["order_id"], row["customer_id"], row["order_date"],
                    row["channel"], row["status"], row["sales_rep"],
                )
                for row in orders
            ],
        )
        connection.executemany(
            "INSERT INTO order_items VALUES (?, ?, ?, ?, ?, ?)",
            [
                (
                    row["order_item_id"], row["order_id"], row["product_id"],
                    int(row["quantity"]), float(row["unit_price"]),
                    float(row["discount_pct"]),
                )
                for row in items
            ],
        )
        connection.commit()
    finally:
        connection.close()

    return db_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(DATA_DIR), help="Directory for generated CSV files")
    parser.add_argument("--db", default=str(DB_PATH), help="SQLite database path")
    parser.add_argument("--orders", type=int, default=N_ORDERS, help="Number of synthetic orders")
    parser.add_argument("--seed", type=int, default=SEED, help="Random seed")
    args = parser.parse_args()

    counts = generate_dataset(args.out, n_orders=args.orders, seed=args.seed)
    build_database(args.out, args.db)

    print("Synthetic dataset generated:")
    for name, value in counts.items():
        print(f"  {name:12s} {value:>5d}")
    print(f"  database     {args.db}")


if __name__ == "__main__":
    main()
