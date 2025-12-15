def generate_diagnosis_report(df):
    report = {}

    report["rows"] = df.shape[0]
    report["columns"] = df.shape[1]
    report["missing_percent"] = (df.isnull().mean() * 100).round(2).to_dict()
    report["duplicates"] = int(df.duplicated().sum())
    report["dtypes"] = df.dtypes.astype(str).to_dict()

    severity = {}
    for col, pct in report["missing_percent"].items():
        if pct == 0:
            severity[col] = "good"
        elif pct < 20:
            severity[col] = "warning"
        else:
            severity[col] = "critical"

    report["severity"] = severity
    return report
