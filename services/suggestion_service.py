import pandas as pd

def generate_cleaning_suggestions(df):
    suggestions = []

    total_rows = len(df)

    # ==========================
    # 1️⃣ Missing Values
    # ==========================
    missing_percent = (df.isnull().sum() / total_rows) * 100

    for col, pct in missing_percent.items():
        if pct > 0:
            severity = "high" if pct > 20 else "medium"

            strategy = "median" if df[col].dtype != "object" else "mode"

            suggestions.append({
                "column": col,
                "issue": "missing_values",
                "severity": severity,
                "message": f"Column '{col}' has {pct:.1f}% missing values.",
                "recommendation": f"Fill missing values using {strategy}."
            })

    # ==========================
    # 2️⃣ Duplicate Rows
    # ==========================
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        suggestions.append({
            "column": "ALL",
            "issue": "duplicates",
            "severity": "high",
            "message": f"Dataset contains {dup_count} duplicate rows.",
            "recommendation": "Remove duplicate rows."
        })

    # ==========================
    # 3️⃣ Data Type Issues
    # ==========================
    for col in df.columns:
        if df[col].dtype == "object":
            try:
                pd.to_numeric(df[col])
                suggestions.append({
                    "column": col,
                    "issue": "datatype",
                    "severity": "medium",
                    "message": f"Column '{col}' looks numeric but is stored as text.",
                    "recommendation": "Convert column to numeric type."
                })
            except:
                pass

    # ==========================
    # 4️⃣ Outliers (IQR)
    # ==========================
    numeric_cols = df.select_dtypes(include="number").columns

    for col in numeric_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outliers = df[(df[col] < lower) | (df[col] > upper)]

        if len(outliers) > 0:
            suggestions.append({
                "column": col,
                "issue": "outliers",
                "severity": "medium",
                "message": f"Column '{col}' contains {len(outliers)} outliers.",
                "recommendation": "Consider capping or removing outliers using IQR."
            })

    return suggestions
