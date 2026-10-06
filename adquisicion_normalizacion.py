"""Adquisición y normalización de datos de ventas (CSV + Excel -> Parquet)."""
from pathlib import Path

import pandas as pd

DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")
CSV_PATH = DATA_DIR / "transacciones.csv"
XLSX_PATH = DATA_DIR / "productos.xlsx"
PARQUET_PATH = OUTPUT_DIR / "ventas_consolidadas.parquet"


def cargar_datos() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Lee las dos fuentes. `with` cierra el motor de Excel (openpyxl)."""
    transacciones = pd.read_csv(CSV_PATH)
    with pd.ExcelFile(XLSX_PATH, engine="openpyxl") as xls:
        productos = pd.read_excel(xls, sheet_name="productos")
    print(f"CSV: {transacciones.shape} | Excel: {productos.shape}")
    return transacciones, productos


def limpiar_transacciones(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Tipos: fecha -> datetime (inválidas pasan a NaT); numéricos -> numeric
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["id_producto"] = pd.to_numeric(df["id_producto"], errors="coerce")
    df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce")

    # Nulos en campos críticos: se eliminan (no se puede inventar producto/fecha/cantidad)
    antes = len(df)
    df = df.dropna(subset=["id_producto", "cantidad", "fecha"])
    print(f"Transacciones descartadas por nulos/invalidas: {antes - len(df)}")

    # Tipos finales (Int64 evita problemas en el merge)
    df["id_producto"] = df["id_producto"].astype("int64")
    df["cantidad"] = df["cantidad"].astype("int64")
    return df


def limpiar_productos(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["id_producto"] = pd.to_numeric(df["id_producto"], errors="coerce")
    df["precio_unitario"] = pd.to_numeric(df["precio_unitario"], errors="coerce")
    df = df.dropna(subset=["id_producto", "nombre_producto", "precio_unitario"])
    df["id_producto"] = df["id_producto"].astype("int64")
    return df.drop_duplicates(subset="id_producto")


def main() -> None:
    transacciones, productos = cargar_datos()
    transacciones = limpiar_transacciones(transacciones)
    productos = limpiar_productos(productos)

    # Merge: inner descarta transacciones cuyo producto no está en el maestro
    ventas = transacciones.merge(productos, on="id_producto", how="inner", validate="m:1")
    print(f"Filas tras merge: {len(ventas)}")

    # Columna calculada
    ventas["total_venta"] = ventas["cantidad"] * ventas["precio_unitario"]

    # Verificación de calidad: sin nulos en campos críticos
    criticos = ["id_producto", "cantidad", "fecha", "precio_unitario", "total_venta"]
    assert ventas[criticos].notna().all().all(), "Hay nulos en campos críticos"
    assert pd.api.types.is_datetime64_any_dtype(ventas["fecha"])

    # Exportación a Parquet
    OUTPUT_DIR.mkdir(exist_ok=True)
    ventas.to_parquet(PARQUET_PATH, engine="pyarrow", index=False)
    print(f"Archivo generado: {PARQUET_PATH}")
    print(ventas.dtypes)
    print(ventas.head())


if __name__ == "__main__":
    main()
