import numpy as np
import pandas as pd

def analyze_data(df):
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    all_cols = df.columns.tolist()

    stats = {}
    variance = {}
    missing = {}
    outliers = {}

    for col in numeric_cols:
        series = df[col].dropna()

        stats[col] = {
            "min": float(series.min()),
            "mean": float(series.mean()),
            "max": float(series.max())
        }

        variance[col] = float(series.var())
        missing[col] = int(df[col].isnull().sum())

        # Outlier detection (IQR)
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outliers[col] = int(((series < lower) | (series > upper)).sum())

    # Missing for NON-numeric columns too
    for col in df.columns:
        if col not in missing:
            missing[col] = int(df[col].isnull().sum())

    correlation = df[numeric_cols].corr().round(2).fillna(0).to_dict()

    return {
        "columns": all_cols,          # ✅ ALL columns (FIX)
        "numeric_columns": numeric_cols,
        "stats": stats,
        "variance": variance,
        "missing": missing,
        "outliers": outliers,
        "correlation": correlation
    }
