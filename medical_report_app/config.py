import os
from pathlib import Path

import pytesseract


BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
DATASETS_DIR = BASE_DIR / "datasets"
MODELS_DIR = BASE_DIR / "models"
TRAINED_MODEL_PATH = MODELS_DIR / "cardiometabolic_risk_bundle.joblib"
TRAINING_REPORT_PATH = MODELS_DIR / "training_report.json"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
DEFAULT_TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def configure_ocr_engine():
    configured_path = os.getenv("TESSERACT_CMD", DEFAULT_TESSERACT_PATH)
    if os.path.exists(configured_path):
        pytesseract.pytesseract.tesseract_cmd = configured_path


def configure_upload_folder(app):
    app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)


def is_allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
