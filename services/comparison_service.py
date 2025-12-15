def compare_datasets(df_old, df_new):
    return {
        "rows_before": len(df_old),
        "rows_after": len(df_new),
        "insights": ["Comparison completed"]
    }
