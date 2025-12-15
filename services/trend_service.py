def detect_trends_and_insights(df):
    insights = []
    for col in df.select_dtypes(include="number").columns:
        insights.append(f"{col} analyzed for trends.")
    return insights
