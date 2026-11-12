PRAGMA foreign_keys = ON;

CREATE TABLE customers (
    customer_id   TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    segment       TEXT NOT NULL CHECK (segment IN ('Consumer', 'SMB', 'Enterprise')),
    country       TEXT NOT NULL,
    city          TEXT NOT NULL,
    signup_date   TEXT NOT NULL
);

CREATE TABLE products (
    product_id   TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category     TEXT NOT NULL,
    unit_price   REAL NOT NULL CHECK (unit_price > 0),
    unit_cost    REAL NOT NULL CHECK (unit_cost >= 0)
);

CREATE TABLE orders (
    order_id    TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    order_date  TEXT NOT NULL,
    channel     TEXT NOT NULL CHECK (channel IN ('Web', 'Retail', 'Partner', 'Phone')),
    status      TEXT NOT NULL CHECK (status IN ('completed', 'cancelled', 'returned')),
    sales_rep   TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
);

CREATE TABLE order_items (
    order_item_id TEXT PRIMARY KEY,
    order_id      TEXT NOT NULL,
    product_id    TEXT NOT NULL,
    quantity      INTEGER NOT NULL CHECK (quantity > 0),
    unit_price    REAL NOT NULL CHECK (unit_price > 0),
    discount_pct  REAL NOT NULL CHECK (discount_pct >= 0 AND discount_pct < 1),
    FOREIGN KEY (order_id) REFERENCES orders (order_id),
    FOREIGN KEY (product_id) REFERENCES products (product_id)
);

CREATE INDEX idx_orders_date ON orders (order_date);
CREATE INDEX idx_orders_customer ON orders (customer_id);
CREATE INDEX idx_items_order ON order_items (order_id);
CREATE INDEX idx_items_product ON order_items (product_id);
