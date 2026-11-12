# Diccionario de datos sintéticos

Todos los registros son ficticios y se generan con `generate_data.py`. La
ejecución por defecto usa la semilla `42` y produce 800 pedidos. No se incluye
información real de clientes, productos ni empleados.

## customers.csv

| Columna | Tipo | Descripción |
| --- | --- | --- |
| `customer_id` | texto | Clave primaria, formato `CUST-0001` |
| `customer_name` | texto | Nombre completo ficticio |
| `segment` | texto | `Consumer`, `SMB` o `Enterprise` |
| `country` | texto | País de facturación ficticio |
| `city` | texto | Ciudad dentro del país |
| `signup_date` | fecha ISO | Fecha de creación de la cuenta (2022-2023) |

## products.csv

| Columna | Tipo | Descripción |
| --- | --- | --- |
| `product_id` | texto | Clave primaria, formato `PROD-001` |
| `product_name` | texto | Nombre de producto ficticio |
| `category` | texto | Electronics, Accessories, Office, Home o Software |
| `unit_price` | real | Precio de lista en USD |
| `unit_cost` | real | Costo unitario usado para calcular el margen bruto |

## orders.csv

| Columna | Tipo | Descripción |
| --- | --- | --- |
| `order_id` | texto | Clave primaria, formato `ORD-00001` |
| `customer_id` | texto | Clave foránea a `customers` |
| `order_date` | fecha ISO | Fecha del pedido en 2024-2025 |
| `channel` | texto | Web, Retail, Partner o Phone |
| `status` | texto | `completed`, `cancelled` o `returned` |
| `sales_rep` | texto | Representante de ventas ficticio |

## order_items.csv

| Columna | Tipo | Descripción |
| --- | --- | --- |
| `order_item_id` | texto | Clave primaria, formato `ITEM-000001` |
| `order_id` | texto | Clave foránea a `orders` |
| `product_id` | texto | Clave foránea a `products` |
| `quantity` | entero | Unidades pedidas, 1-5 |
| `unit_price` | real | Precio de venta por unidad antes del descuento |
| `discount_pct` | real | Descuento como decimal (`0.10` = 10%) |

## Definición de ingresos

```text
line_revenue = quantity * unit_price * (1 - discount_pct)
realised_revenue = suma(line_revenue) para pedidos con status = 'completed'
```

`data/sales.db` se genera a partir de estos archivos CSV y se excluye del control
de versiones porque es un artefacto binario reconstruible.
