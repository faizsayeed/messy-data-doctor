from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_from_directory,
    send_file,
    jsonify
)

import os
import io
import json
import zipfile
import base64
import pandas as pd

# ==============================
# SERVICE IMPORTS
# ==============================
from services.diagnosis_service import generate_diagnosis_report
from services.scoring_service import calculate_data_quality_score
from services.analytics_service import analyze_data
from services.cleaning_service import clean_data
from services.suggestion_service import generate_cleaning_suggestions
from services.nlp_service import process_nl_query
from services.trend_service import detect_trends_and_insights
from services.export_service import generate_python_cleaning_script, generate_pdf_report
from services.comparison_service import compare_datasets
from services.versioning_service import save_new_version, get_versions, load_version

# ==============================
# APP SETUP
# ==============================
app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_FOLDER = os.path.join(BASE_DIR, "storage", "raw")
CLEANED_FOLDER = os.path.join(BASE_DIR, "storage", "versions")
EXPORT_FOLDER = os.path.join(BASE_DIR, "storage", "exports")

os.makedirs(RAW_FOLDER, exist_ok=True)
os.makedirs(CLEANED_FOLDER, exist_ok=True)
os.makedirs(EXPORT_FOLDER, exist_ok=True)

app.config.update(
    RAW_FOLDER=RAW_FOLDER,
    CLEANED_FOLDER=CLEANED_FOLDER,
    EXPORT_FOLDER=EXPORT_FOLDER
)

# ==============================
# ROUTES
# ==============================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files.get("file")

        if not file or not file.filename.endswith(".csv"):
            return "Invalid file format", 400

        filename = file.filename
        raw_path = os.path.join(app.config["RAW_FOLDER"], filename)
        cleaned_path = os.path.join(app.config["CLEANED_FOLDER"], filename)

        # 🔥 IMPORTANT FIX
        # If same file is uploaded again, RESET previous cleaned version
        if os.path.exists(cleaned_path):
            os.remove(cleaned_path)

        file.save(raw_path)

        return redirect(url_for("report", filename=filename))

    return render_template("upload.html", title="Upload Dataset")



@app.route("/report/<filename>")
def report(filename):
    raw_path = os.path.join(RAW_FOLDER, filename)
    cleaned_path = os.path.join(CLEANED_FOLDER, filename)

    if not os.path.exists(raw_path):
        return "File not found", 404

    raw_df = pd.read_csv(raw_path)

    if os.path.exists(cleaned_path):
        df = pd.read_csv(cleaned_path)
        data_source = "cleaned"
    else:
        df = raw_df
        data_source = "original"

    return render_template(
        "report.html",
        filename=filename,
        data_source=data_source,
        diagnosis=generate_diagnosis_report(df),
        analytics=analyze_data(df),
        suggestions=generate_cleaning_suggestions(df),
        trends=detect_trends_and_insights(df),
        before_score=calculate_data_quality_score(raw_df),
        after_score=calculate_data_quality_score(df)
    )


@app.route("/clean/<filename>")
def clean(filename):
    raw_path = os.path.join(RAW_FOLDER, filename)
    df = pd.read_csv(raw_path)

    missing = request.args.get("missing")
    outliers = request.args.get("outliers")
    duplicates = request.args.get("duplicates")

    # Missing values
    for col in df.select_dtypes(include="number"):
        if missing == "mean":
            df[col].fillna(df[col].mean(), inplace=True)
        elif missing == "median":
            df[col].fillna(df[col].median(), inplace=True)
        elif missing == "mode":
            df[col].fillna(df[col].mode()[0], inplace=True)

    # Outliers
    if outliers == "cap":
        for col in df.select_dtypes(include="number"):
            q1, q3 = df[col].quantile([0.25, 0.75])
            iqr = q3 - q1
            df[col] = df[col].clip(q1 - 1.5*iqr, q3 + 1.5*iqr)

    elif outliers == "remove":
        for col in df.select_dtypes(include="number"):
            q1, q3 = df[col].quantile([0.25, 0.75])
            iqr = q3 - q1
            df = df[(df[col] >= q1 - 1.5*iqr) & (df[col] <= q3 + 1.5*iqr)]

    # Duplicates
    if duplicates == "remove":
        df.drop_duplicates(inplace=True)

    save_new_version(df, filename, "Custom cleaning applied", CLEANED_FOLDER)

    return redirect(url_for("report", filename=filename))


@app.route("/apply_suggestion/<filename>", methods=["POST"])
def apply_suggestion(filename):
    issue = request.form.get("issue")
    column = request.form.get("column")

    raw_path = os.path.join(app.config["RAW_FOLDER"], filename)
    cleaned_path = os.path.join(app.config["CLEANED_FOLDER"], filename)

    # Load latest version
    if os.path.exists(cleaned_path):
        df = pd.read_csv(cleaned_path)
    else:
        df = pd.read_csv(raw_path)

    # =============================
    # HANDLE MISSING VALUES SAFELY
    # =============================
    if issue == "missing_values":

        # NUMERIC COLUMN → MEDIAN
        if pd.api.types.is_numeric_dtype(df[column]):
            df[column].fillna(df[column].median(), inplace=True)

        # TEXT / CATEGORY COLUMN → MODE
        else:
            mode_val = df[column].mode()
            if not mode_val.empty:
                df[column].fillna(mode_val[0], inplace=True)

    # =============================
    # DUPLICATES
    # =============================
    elif issue == "duplicates":
        df.drop_duplicates(inplace=True)

    # =============================
    # OUTLIERS (NUMERIC ONLY)
    # =============================
    elif issue == "outliers" and pd.api.types.is_numeric_dtype(df[column]):
        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        df[column] = df[column].clip(lower, upper)

    # =============================
    # SAVE CLEANED VERSION
    # =============================
    save_new_version(
        df,
        filename,
        action=f"Applied {issue} fix on {column}",
        base_dir=app.config["CLEANED_FOLDER"]
    )

    return redirect(url_for("report", filename=filename))



@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(CLEANED_FOLDER, filename, as_attachment=True)


@app.route("/ask/<filename>", methods=["POST"])
def ask(filename):
    path = os.path.join(
        CLEANED_FOLDER if os.path.exists(os.path.join(CLEANED_FOLDER, filename)) else RAW_FOLDER,
        filename
    )
    df = pd.read_csv(path)
    return process_nl_query(request.form["query"], df)


@app.route("/export/python/<filename>")
def export_python(filename):
    df = pd.read_csv(os.path.join(RAW_FOLDER, filename))
    name, code = generate_python_cleaning_script(filename, generate_cleaning_suggestions(df))

    path = os.path.join(EXPORT_FOLDER, name)
    with open(path, "w") as f:
        f.write(code)

    return send_from_directory(EXPORT_FOLDER, name, as_attachment=True)


@app.route("/export/pdf/<filename>")
def export_pdf(filename):
    raw_path = os.path.join(RAW_FOLDER, filename)
    df = pd.read_csv(raw_path)

    pdf_name = filename.replace(".csv", "_report.pdf")
    pdf_path = os.path.join(EXPORT_FOLDER, pdf_name)

    generate_pdf_report(
    filename,
    generate_diagnosis_report(df),
    calculate_data_quality_score(df),
    detect_trends_and_insights(df),
    pdf_path,
    df=df   # 🔥 THIS IS THE KEY
)


    return send_from_directory(EXPORT_FOLDER, pdf_name, as_attachment=True)


@app.route("/compare/<filename>")
def compare(filename):
    return render_template(
        "compare.html",
        comparison=compare_datasets(
            pd.read_csv(os.path.join(RAW_FOLDER, filename)),
            pd.read_csv(os.path.join(CLEANED_FOLDER, filename))
        ),
        filename=filename
    )


@app.route("/versions/<filename>")
def versions(filename):
    return render_template("versions.html", versions=get_versions(filename), filename=filename)


@app.route("/undo/<filename>/<int:version>")
def undo(filename, version):
    df = load_version(filename, version, CLEANED_FOLDER)
    df.to_csv(os.path.join(CLEANED_FOLDER, filename), index=False)
    return redirect(url_for("report", filename=filename))
@app.route("/apply_all/<filename>", methods=["POST"])
def apply_all_suggestions(filename):

    raw_path = os.path.join(app.config["RAW_FOLDER"], filename)
    cleaned_path = os.path.join(app.config["CLEANED_FOLDER"], filename)

    # Load latest data
    if os.path.exists(cleaned_path):
        df = pd.read_csv(cleaned_path)
    else:
        df = pd.read_csv(raw_path)

    suggestions = generate_cleaning_suggestions(df)

    for s in suggestions:
        issue = s["issue"]
        column = s["column"]

        # =============================
        # MISSING VALUES
        # =============================
        if issue == "missing_values":

            if column != "ALL":
                if pd.api.types.is_numeric_dtype(df[column]):
                    df[column].fillna(df[column].median(), inplace=True)
                else:
                    mode = df[column].mode()
                    if not mode.empty:
                        df[column].fillna(mode[0], inplace=True)

        # =============================
        # DUPLICATES
        # =============================
        elif issue == "duplicates":
            df.drop_duplicates(inplace=True)

        # =============================
        # OUTLIERS
        # =============================
        elif issue == "outliers" and pd.api.types.is_numeric_dtype(df[column]):

            q1 = df[column].quantile(0.25)
            q3 = df[column].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr

            df[column] = df[column].clip(lower, upper)

    # =============================
    # SAVE AS ONE VERSION
    # =============================
    save_new_version(
        df,
        filename,
        action="Applied all AI cleaning suggestions",
        base_dir=app.config["CLEANED_FOLDER"]
    )

    return redirect(url_for("report", filename=filename))

@app.route("/export/analytics", methods=["POST"])
def export_analytics():
    data = request.json

    mem_zip = io.BytesIO()

    with zipfile.ZipFile(mem_zip, "w", zipfile.ZIP_DEFLATED) as z:

        # Save summary
        z.writestr("summary.json", json.dumps({
            "scores": data["scores"],
            "analytics": data["analytics"]
        }, indent=2))

        # Save charts
        for name, img in data["images"].items():
            img_data = base64.b64decode(img.split(",")[1])
            z.writestr(f"charts/{name}.png", img_data)

    mem_zip.seek(0)
    return send_file(
        mem_zip,
        mimetype="application/zip",
        as_attachment=True,
        download_name="analytics_report.zip"
    )

@app.route("/export/analytics-safe/<filename>")
def export_analytics_safe(filename):
    """
    Windows-safe analytics export
    Creates ZIP on disk first, then sends it
    """

    # Decide data source
    csv_path = (
        os.path.join(CLEANED_FOLDER, filename)
        if os.path.exists(os.path.join(CLEANED_FOLDER, filename))
        else os.path.join(RAW_FOLDER, filename)
    )

    df = pd.read_csv(csv_path)
    analytics = analyze_data(df)
    scores = calculate_data_quality_score(df)

    zip_name = filename.replace(".csv", "_analytics.zip")
    zip_path = os.path.join(EXPORT_FOLDER, zip_name)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:

        # 1️⃣ CSV
        z.write(csv_path, arcname=filename)

        # 2️⃣ Analytics JSON
        analytics_path = os.path.join(EXPORT_FOLDER, "analytics.json")
        with open(analytics_path, "w") as f:
            json.dump(analytics, f, indent=2)
        z.write(analytics_path, arcname="analytics/analytics.json")

        # 3️⃣ Scores JSON
        scores_path = os.path.join(EXPORT_FOLDER, "scores.json")
        with open(scores_path, "w") as f:
            json.dump(scores, f, indent=2)
        z.write(scores_path, arcname="analytics/scores.json")

    return send_file(
        zip_path,
        as_attachment=True,
        download_name=zip_name
    )


# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    app.run()

