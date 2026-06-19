from flask import Blueprint, render_template, request
from werkzeug.utils import secure_filename

from .config import UPLOAD_FOLDER, is_allowed_file
from .services.report_analysis import analyze_report


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return render_template("index.html")


@main_bp.route("/upload", methods=["POST"])
def upload():
    uploaded_file = request.files.get("file")
    if not uploaded_file or uploaded_file.filename == "":
        return render_template("result.html", error="Please choose a medical report image before uploading.")

    if not is_allowed_file(uploaded_file.filename):
        return render_template("result.html", error="Only PNG, JPG, and JPEG images are supported.")

    filename = secure_filename(uploaded_file.filename)
    filepath = UPLOAD_FOLDER / filename
    uploaded_file.save(filepath)

    try:
        result = analyze_report(filepath)
    except Exception as error:
        return render_template("result.html", error=str(error))

    return render_template("result.html", **result)
