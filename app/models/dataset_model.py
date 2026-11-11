from functools import lru_cache
import os
import kagglehub
import pandas as pd
from app.utils.errors import DatasetError

DATASET = "agungpambudi/trends-product-coffee-shop-sales-revenue-dataset"

@lru_cache(maxsize=1)
def load_dataset() -> pd.DataFrame:
    """Descarga y carga el CSV una sola vez por proceso."""
    try:
        path = kagglehub.dataset_download(DATASET)
        csv_file = None

        for root, _, filenames in os.walk(path):
            for filename in filenames:
                if filename.lower().endswith(".csv"):
                    csv_file = os.path.join(root, filename)
                    break
            if csv_file:
                break

        if not csv_file:
            raise DatasetError("Kaggle no proporcionó ningún archivo CSV.")

        df = pd.read_csv(csv_file, sep="|")

        required = {"transaction_date", "store_id", "product_id", "unit_price"}
        missing = required.difference(df.columns)
        if missing:
            raise DatasetError(
                f"Faltan columnas obligatorias en el CSV: {sorted(missing)}"
            )

        df["transaction_date"] = pd.to_datetime(
            df["transaction_date"], errors="coerce"
        )
        df = df.dropna(subset=["transaction_date", "store_id", "product_id"])
        return df

    except DatasetError:
        raise
    except Exception as exc:
        raise DatasetError(f"No se pudo descargar o leer el dataset de Kaggle: {exc}")
