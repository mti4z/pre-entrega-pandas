"""Genera los archivos fuente de ejemplo (CSV de transacciones y Excel de productos).

Se incluyen a propósito algunos problemas típicos (nulos, fechas inválidas,
IDs con distinto tipo) para que la etapa de limpieza tenga sentido.
"""
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
DATA = Path("data")
DATA.mkdir(exist_ok=True)

# --- Maestro de productos (Excel) ---
productos = pd.DataFrame({
    "id_producto": range(1, 11),
    "nombre_producto": ["Teclado", "Mouse", "Monitor 24\"", "Notebook", "Auriculares",
                        "Webcam", "Impresora", "Pendrive 64GB", "Disco SSD 1TB", "Parlantes"],
    "precio_unitario": [12500, 6800, 145000, 780000, 21000, 18500, 98000, 7200, 54000, 16500],
})
productos.to_excel(DATA / "productos.xlsx", index=False, sheet_name="productos")

# --- Transacciones (CSV) ---
n = 200
trans = pd.DataFrame({
    "id_transaccion": range(1, n + 1),
    # id_producto 11 no existe en el maestro (caso de producto huérfano)
    "id_producto": rng.integers(1, 12, n).astype(str),
    "cantidad": rng.integers(1, 6, n).astype(float),
    "fecha": pd.date_range("2024-01-01", periods=n, freq="D").strftime("%Y-%m-%d"),
})
trans.loc[[5, 40], "cantidad"] = np.nan          # cantidad nula
trans.loc[[12], "id_producto"] = np.nan          # id nulo
trans.loc[[20], "fecha"] = "fecha-invalida"      # fecha corrupta
trans.to_csv(DATA / "transacciones.csv", index=False)
print("Archivos generados en ./data")
