# SQL Sales Analytics

Un proyecto de datos pequeño y autocontenido que construye un **conjunto de
datos de ventas sintético**, lo carga en **SQLite** y responde preguntas de
negocio comunes con **SQL**.

Todo se genera desde código: no se usa información real de empresas, clientes
ni transacciones. La misma semilla siempre produce el mismo conjunto de datos,
por lo que los resultados son reproducibles.

## Qué demuestra este proyecto

- Diseño de un esquema relacional pequeño (clientes, productos, pedidos y líneas de pedido).
- Generación de datos sintéticos reproducibles con el módulo `random` de Python.
- Carga de datos CSV en SQLite y aplicación de relaciones mediante claves foráneas.
- Escritura de SQL analítico: `JOIN`, `GROUP BY`, `CTE`, funciones de ventana
  (`RANK`, `DENSE_RANK`, `NTILE`, `LAG`, `SUM() OVER ()`).
- Ejecución de consultas desde Python y exportación de reportes CSV + Markdown.
- Pruebas de la generación de datos y de los resultados de las consultas con `pytest`.

## Estructura del proyecto

```
sql-sales-analytics/
├── generate_data.py        # crea los CSV y la base de datos SQLite
├── run_analysis.py         # ejecuta todos los SQL y escribe los reportes
├── schema.sql              # definición de tablas, restricciones e índices
├── conftest.py             # permite importar el proyecto en las pruebas
├── requirements.txt
├── sql/                    # una pregunta analítica por archivo
│   ├── 01_monthly_revenue.sql
│   ├── 02_top_products.sql
│   ├── 03_category_performance.sql
│   ├── 04_customer_segments.sql
│   ├── 05_sales_rep_performance.sql
│   ├── 06_monthly_growth.sql
│   ├── 07_customer_value_tiers.sql
│   └── 08_regional_performance.sql
├── tests/
│   ├── test_generate_data.py
│   └── test_queries.py
├── data/                   # CSV generados (+ sales.db)
└── results/                # tablas CSV generadas + summary.md
```

## Requisitos

- Python 3.12
- `pandas` y `pytest` (ver `requirements.txt`)

SQLite viene incluido con Python, así que no hay nada más que instalar.

## Cómo ejecutar

Desde la carpeta del proyecto:

```bash
# 1. Genera los datos sintéticos y construye la base de datos
python generate_data.py

# 2. Ejecuta todos los análisis y escribe results/ (tablas CSV + summary.md)
python run_analysis.py
```

`run_analysis.py` construye la base de datos automáticamente si todavía no
existe, por lo que el paso 2 también funciona por sí solo. Opciones útiles:

```bash
python run_analysis.py --regenerate            # reconstruye los datos desde cero
python run_analysis.py --orders 2000 --seed 7  # otro tamaño/semilla del conjunto
```

## Cómo ejecutar las pruebas

```bash
python -m pytest -q
```

Las pruebas comprueban que la generación es determinista, que la base de datos
tiene relaciones y valores válidos y que cada consulta devuelve resultados
coherentes e internamente consistentes.

## Las preguntas analíticas

| Archivo | Pregunta |
| --- | --- |
| `01_monthly_revenue.sql` | ¿Cuánto ingreso y cuántos pedidos hay por mes? |
| `02_top_products.sql` | ¿Qué 10 productos generan más ingresos? |
| `03_category_performance.sql` | Ingresos, margen y participación por categoría de producto. |
| `04_customer_segments.sql` | ¿Cómo se comparan los segmentos Consumer / SMB / Enterprise? |
| `05_sales_rep_performance.sql` | Ranking de representantes de ventas. |
| `06_monthly_growth.sql` | Crecimiento de ingresos mes a mes. |
| `07_customer_value_tiers.sql` | Clientes divididos en cuartiles de ingresos. |
| `08_regional_performance.sql` | Ingresos y actividad de clientes por país. |

## Notas metodológicas

- **Ingreso** = `quantity × unit_price × (1 − discount_pct)`.
- Solo los pedidos con `status = 'completed'` cuentan como ventas; los pedidos
  cancelados y devueltos se excluyen de los ingresos.
- El margen usa el `unit_cost` del producto almacenado en el catálogo.
- Los meses son meses calendario (`strftime('%Y-%m', order_date)`).

## Ejemplo de salida

`results/summary.md` se genera en cada ejecución. Con la semilla por defecto
(42) y 800 pedidos, comienza así:

| Métrica | Valor observado |
| --- | --- |
| Pedidos en el conjunto | 800 |
| Pedidos completados | 671 |
| Ingreso realizado (después de descuentos) | $559,338.00 |
| Valor medio del pedido | $833.59 |
| Producto principal | Aurora Laptop 14 ($72,369.50) |
| Categoría principal | Electronics (55.12% de participación) |

Estas cifras son sintéticas y solo demuestran que el flujo de trabajo funciona.

## Licencia / aviso sobre los datos

El conjunto de datos es ficticio y se genera localmente. No representa a ninguna
empresa, mercado ni resultado de negocio real.
