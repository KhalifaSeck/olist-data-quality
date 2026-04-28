import pandas as pd
import numpy as np


def test_column_normalization():
    """Les noms de colonnes doivent être en minuscules sans espaces."""
    df = pd.DataFrame(columns=["Order ID", "Customer Name"])
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]
    assert list(df.columns) == ["order_id", "customer_name"]


def test_nan_to_none():
    """Les NaN doivent être convertis en None."""
    row = pd.Series({"order_id": "123", "price": np.nan})
    result = tuple(str(v) if pd.notna(v) else None for v in row)
    assert result == ("123", None)