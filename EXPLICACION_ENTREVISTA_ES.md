# Guía de entrevista — SQL Sales Analytics

> Proyecto de portafolio con datos 100 % sintéticos. No representa experiencia
> laboral, clientes reales ni resultados de una empresa.

## Explicación de 20–30 segundos

"Este proyecto simula dos años de ventas de una empresa ficticia: 800 pedidos,
140 clientes y 44 productos. Genero los datos de forma reproducible con una
semilla fija, los cargo en SQLite y respondo preguntas de negocio con SQL:
ingresos mensuales, productos top, margen por categoría, segmentos de clientes,
ranking de vendedores, crecimiento mes a mes, cuartiles de valor de cliente y
desempeño por país.
Uso joins, CTEs y funciones de ventana como RANK, LAG y NTILE. Además tengo
pruebas que validan integridad referencial, cálculos y reproducibilidad."

## Puntos que conviene saber explicar

1. **Separación de capas:** los CSV son la fuente reproducible; `sales.db` es
   un artefacto reconstruible. El esquema vive en `schema.sql`.
2. **Ingresos realizados vs. pedidos:** solo los pedidos `completed` cuentan.
   Los cancelados y devueltos se conservan para representar el flujo real.
3. **Descuentos:** el ingreso es `cantidad * precio * (1 - descuento)`. El costo
   no lleva descuento, por eso el margen baja cuando aumentan los descuentos.
4. **Funciones de ventana:** `RANK` para productos, `DENSE_RANK` para vendedores,
   `LAG` para crecimiento mensual y `NTILE(4)` para cuartiles de clientes.
5. **Pruebas:** no solo comprueban que la consulta corra; comparan totales con
   una agregación independiente y verifican que dos ejecuciones produzcan los
   mismos CSV.

## Preguntas probables y respuestas breves

**¿Por qué usaste SQLite?**
Es suficiente para un dataset pequeño, no requiere servidor y permite demostrar
SQL real. El esquema y las consultas se trasladan a SQL Server o PostgreSQL con
cambios menores de sintaxis (por ejemplo, `strftime`).

**¿Qué limitación tiene el análisis?**
Los datos son sintéticos y el margen es simplificado: no incluye impuestos,
envíos, comisiones de pago ni costos indirectos. Los cuartiles usan solo ingresos,
no rentabilidad ni recencia.

**¿Cómo garantizas que los resultados son reproducibles?**
La generación usa `random.Random(seed)`, los archivos se escriben en orden fijo y
una prueba compara los CSV de dos generaciones y de dos ejecuciones del análisis.

**¿Qué harías con más tiempo?**
Añadiría una capa de tests de datos con Great Expectations o dbt, cálculo de
retención por cohortes, comparación año contra año y un tablero en Power BI
conectado a la base.

## Comandos para demostrar en vivo

```powershell
python generate_data.py
python run_analysis.py
python -m pytest -q tests
```

Mostrar `results/summary.md` y abrir una consulta, por ejemplo
`sql/06_monthly_growth.sql`, para explicar `LAG`.
