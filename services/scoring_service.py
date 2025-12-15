import pandas as pd

def calculate_data_quality_score(df):
    total_rows = len(df)
    total_cells = df.shape[0] * df.shape[1]

    # ==========================
    # 1️⃣ Completeness (25)
    # ==========================
    missing_cells = df.isnull().sum().sum()
    completeness = max(0, 25 * (1 - missing_cells / total_cells))

    # ==========================
    # 2️⃣ Uniqueness (25)
    # ==========================
    dup_rows = df.duplicated().sum()
    uniqueness = max(0, 25 * (1 - dup_rows / total_rows))

    # ==========================
    # 3️⃣ Consistency (25)
    # ==========================
    inconsistent_cols = 0
    for col in df.columns:
        if df[col].dtype == "object":
            try:
                pd.to_numeric(df[col])
                inconsistent_cols += 1
            except:
                pass

    consistency = max(0, 25 * (1 - inconsistent_cols / len(df.columns)))

    # ==========================
    # 4️⃣ Validity (25) – Outliers
    # ==========================
    outlier_cells = 0
    numeric_cols = df.select_dtypes(include="number").columns

    for col in numeric_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outlier_cells += ((df[col] < lower) | (df[col] > upper)).sum()

    validity = max(0, 25 * (1 - outlier_cells / total_cells))

    # ==========================
    total_score = round(completeness + uniqueness + consistency + validity, 1)

    return {
        "total": total_score,
        "completeness": round(completeness, 1),
        "uniqueness": round(uniqueness, 1),
        "consistency": round(consistency, 1),
        "validity": round(validity, 1),
    }
