# Pre-entrega: Adquisición y Normalización con Pandas

Integra datos de ventas de dos departamentos en formatos distintos
(**CSV** de transacciones y **Excel** de catálogo de productos) en un único
dataset limpio, exportado a **Parquet**.

## Estructura

```
├── data/
│   ├── transacciones.csv      # id_transaccion, id_producto, cantidad, fecha
│   └── productos.xlsx         # id_producto, nombre_producto, precio_unitario
├── output/
│   └── ventas_consolidadas.parquet
├── generar_datos.py           # crea los archivos fuente de ejemplo
├── adquisicion_normalizacion.py  # pipeline principal
├── requirements.txt
└── README.md
```

## Librerías necesarias

`pandas`, `openpyxl` (lectura de .xlsx), `pyarrow` (escritura de Parquet). Python 3.9+.

## Pasos para reproducir

```bash
# 1. Clonar el repositorio
git clone <URL-DE-TU-REPO>
cd <nombre-del-repo>

# 2. (Opcional) Entorno virtual
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. (Opcional) Regenerar los datos de ejemplo
python generar_datos.py

# 5. Ejecutar el pipeline
python adquisicion_normalizacion.py
```

El resultado queda en `output/ventas_consolidadas.parquet`.

## Qué hace el pipeline

1. **Adquisición:** lee el CSV con `read_csv` y el Excel con `read_excel` (dentro de un `with` para cerrar el motor).
2. **Tipos:** convierte `fecha` a `datetime64` (valores inválidos → `NaT`) e `id_producto` a entero en ambas fuentes, para evitar el error de merge string vs. entero.
3. **Nulos:** se eliminan filas con `id_producto`, `cantidad` o `fecha` nulos, ya que son campos críticos que no pueden imputarse con sentido.
4. **Merge:** `inner join` por `id_producto` (relación muchos-a-uno, validada con `validate="m:1"`). Se descartan transacciones de productos inexistentes en el maestro.
5. **Columna calculada:** `total_venta = cantidad * precio_unitario`.
6. **Exportación:** `to_parquet` con `pyarrow`.

## Columnas del dataset final

`id_transaccion`, `id_producto`, `cantidad`, `fecha`, `nombre_producto`, `precio_unitario`, `total_venta`
