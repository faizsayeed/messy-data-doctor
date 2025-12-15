from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import os


def generate_python_cleaning_script(filename, suggestions):
    """
    Generate a reproducible Python cleaning script.
    """
    script_name = filename.replace(".csv", "_cleaning.py")

    lines = [
        "import pandas as pd",
        "",
        f"df = pd.read_csv('{filename}')",
        "",
        "# Cleaning steps",
    ]

    for s in suggestions:
        if s["type"] == "missing":
            col = s["column"]
            lines.append(f"df['{col}'].fillna(df['{col}'].median(), inplace=True)")

    lines.append("")
    lines.append("df.to_csv('cleaned_output.csv', index=False)")

    return script_name, "\n".join(lines)


def generate_pdf_report(filename, diagnosis, health, insights, output_path, df=None):
    """
    Generate a PDF data quality report WITH charts.
    """
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    y = height - 2 * cm

    # ======================
    # TITLE
    # ======================
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, y, "Data Quality Report")
    y -= 1.2 * cm

    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y, f"Dataset: {filename}")
    y -= 1 * cm

    # ======================
    # SCORE
    # ======================
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Data Quality Score")
    y -= 0.8 * cm

    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y, f"Overall Score: {health['total']} / 100")
    y -= 1.2 * cm

    # ======================
    # DIAGNOSIS
    # ======================
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Missing Values (%)")
    y -= 0.6 * cm

    c.setFont("Helvetica", 9)
    for col, pct in diagnosis["missing_percent"].items():
        c.drawString(2 * cm, y, f"{col}: {pct}%")
        y -= 0.4 * cm
        if y < 2 * cm:
            c.showPage()
            y = height - 2 * cm

    # ======================
    # CHARTS (NEW PART)
    # ======================
    if df is not None:
        c.showPage()
        y = height - 2 * cm

        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, y, "Numeric Column Distributions")
        y -= 1 * cm

        for col in df.select_dtypes(include="number").columns:
            # create temp image
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                plt.figure()
                df[col].dropna().plot(kind="hist", bins=20, title=col)
                plt.tight_layout()
                plt.savefig(tmp.name)
                plt.close()

                # add image to PDF
                c.drawImage(tmp.name, 2 * cm, y - 7 * cm, width=16 * cm, height=6 * cm)
                y -= 7.5 * cm

                os.remove(tmp.name)

                if y < 3 * cm:
                    c.showPage()
                    y = height - 2 * cm

    # ======================
    # INSIGHTS
    # ======================
    c.showPage()
    y = height - 2 * cm

    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Auto-Generated Insights")
    y -= 0.8 * cm

    c.setFont("Helvetica", 9)
    for insight in insights:
        c.drawString(2 * cm, y, f"- {insight}")
        y -= 0.5 * cm
        if y < 2 * cm:
            c.showPage()
            y = height - 2 * cm

    c.save()
