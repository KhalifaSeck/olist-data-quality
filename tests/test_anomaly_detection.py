import pandas as pd
import numpy as np
from datetime import date, timedelta


def _make_df(days=60, spike_day=None, spike_val=None, seed=42):
    np.random.seed(seed)  
    dates = [date(2024, 1, 1) + timedelta(days=i) for i in range(days)]
    rev   = [1000 + np.random.normal(0, 30) for _ in dates]
    if spike_day is not None:
        rev[spike_day] = spike_val
    return pd.DataFrame({
        "date":        pd.to_datetime(dates),
        "revenue":     rev,
        "order_count": [10] * days
    })


def test_no_anomaly_stable():
    """Données stables → pas d'anomalie avec seuil élevé."""
    from monitoring.anomaly_detection import detect_zscore_anomalies
    df = _make_df(60, seed=42)
    # Seuil à 3.0 pour éviter les faux positifs sur données stables
    assert len(detect_zscore_anomalies(df, "revenue", warn=3.0, crit=4.0)) == 0


def test_detects_spike():
    """Spike massif → au moins une anomalie."""
    from monitoring.anomaly_detection import detect_zscore_anomalies
    df = _make_df(60, spike_day=55, spike_val=99999)
    assert len(detect_zscore_anomalies(df, "revenue")) >= 1


def test_wow_drop_detected():
    """Chute WoW > 30% → anomalie détectée."""
    from monitoring.anomaly_detection import detect_wow_drop
    dates = pd.date_range("2024-01-01", periods=14)
    df = pd.DataFrame({"date": dates, "revenue": [5000]*7 + [1000]*7})
    assert len(detect_wow_drop(df, "revenue", threshold=0.30)) >= 1


def test_wow_no_false_positive():
    """Chute WoW < 30% → pas d'anomalie."""
    from monitoring.anomaly_detection import detect_wow_drop
    dates = pd.date_range("2024-01-01", periods=14)
    df = pd.DataFrame({"date": dates, "revenue": [5000]*7 + [4900]*7})
    assert len(detect_wow_drop(df, "revenue", threshold=0.30)) == 0