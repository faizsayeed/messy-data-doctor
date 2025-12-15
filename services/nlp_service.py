def process_nl_query(query, df):
    q = query.lower().strip()

    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    if not numeric_cols:
        return {"answer": "No numeric columns found in the dataset."}

    # ==========================
    # Detect mentioned column
    # ==========================
    selected_col = None
    for col in numeric_cols:
        if col.lower() in q:
            selected_col = col
            break

    # ==========================
    # HIGHEST / MAX
    # ==========================
    if "highest" in q or "maximum" in q or "max" in q:
        if not selected_col:
            return {
                "answer": (
                    "Please specify a column. "
                    f"Available numeric columns: {', '.join(numeric_cols)}"
                )
            }
        val = df[selected_col].max()
        return {
            "answer": f"The highest value in '{selected_col}' is {val}."
        }

    # ==========================
    # LOWEST / MIN
    # ==========================
    if "lowest" in q or "minimum" in q or "min" in q:
        if not selected_col:
            return {
                "answer": (
                    "Please specify a column. "
                    f"Available numeric columns: {', '.join(numeric_cols)}"
                )
            }
        val = df[selected_col].min()
        return {
            "answer": f"The lowest value in '{selected_col}' is {val}."
        }

    # ==========================
    # MEAN / AVERAGE
    # ==========================
    if "mean" in q or "average" in q:
        if not selected_col:
            return {
                "answer": (
                    "Please specify a column for average. "
                    f"Available numeric columns: {', '.join(numeric_cols)}"
                )
            }
        val = round(df[selected_col].mean(), 2)
        return {
            "answer": f"The average value of '{selected_col}' is {val}."
        }

    # ==========================
    # MISSING VALUES
    # ==========================
    if "missing" in q or "null" in q:
        if selected_col:
            cnt = df[selected_col].isnull().sum()
            return {
                "answer": f"Column '{selected_col}' has {cnt} missing values."
            }

        missing = df.isnull().sum()
        summary = ", ".join(
            [f"{c}: {v}" for c, v in missing.items() if v > 0]
        )
        return {
            "answer": summary or "No missing values found in the dataset."
        }

    # ==========================
    # CORRELATION
    # ==========================
    if "correlation" in q:
        corr = df[numeric_cols].corr().round(2)
        return {
            "answer": "Correlation matrix between numeric columns:",
            "table": corr.reset_index().to_dict(orient="records")
        }

    # ==========================
    # TREND
    # ==========================
    if "trend" in q:
        if not selected_col:
            return {
                "answer": (
                    "Please specify a column to analyze trend. "
                    f"Available numeric columns: {', '.join(numeric_cols)}"
                )
            }

        trend = (
            "increasing"
            if df[selected_col].iloc[-1] > df[selected_col].iloc[0]
            else "decreasing"
        )

        return {
            "answer": f"The overall trend of '{selected_col}' is {trend}."
        }

    # ==========================
    # FALLBACK
    # ==========================
    return {
        "answer": (
            "I understood the question, but this analysis is not supported yet.\n"
            "Try: highest value in Ozone, average Wind, correlation, trend of Temp"
        )
    }
