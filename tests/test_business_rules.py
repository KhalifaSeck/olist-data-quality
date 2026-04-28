import pandas as pd
from datetime import datetime, timedelta

now = datetime.now()


def test_delivery_before_purchase():
    """Livraison avant achat → 1 violation."""
    df = pd.DataFrame({
        "order_id":     ["A", "B", "C"],
        "purchased_at": [
            now - timedelta(days=5),
            now - timedelta(days=2),
            now - timedelta(days=1)
        ],
        "delivered_at": [
            now - timedelta(days=1),
            now - timedelta(days=3),
            None
        ],
    })
    v = df[df["delivered_at"].notna() & (df["delivered_at"] < df["purchased_at"])]
    assert len(v) == 1
    assert v.iloc[0]["order_id"] == "B"


def test_zero_revenue():
    """Commande livrée avec revenue=0 → 1 violation."""
    df = pd.DataFrame({
        "order_id":     ["X", "Y", "Z"],
        "order_status": ["delivered", "delivered", "canceled"],
        "revenue":      [150.0, 0.0, 0.0],
    })
    v = df[(df["order_status"] == "delivered") & (df["revenue"] == 0)]
    assert len(v) == 1
    assert v.iloc[0]["order_id"] == "Y"