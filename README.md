# MOKSHA

MOKSHA by Nexora Technologies is a Flask-based AI-assisted healthcare screening prototype for medical report interpretation. It combines OCR, biomarker extraction, rule-based clinical screening, and optional machine-learning support to produce explainable risk summaries while preserving medical ethics and privacy-by-design principles.

MOKSHA is a diagnostic support tool only. It does not diagnose disease, replace a clinician, or override laboratory interpretation.

## Core capabilities

- OCR-driven extraction from uploaded report images
- Expanded biomarker support for fasting glucose, HbA1c, total cholesterol, LDL, HDL, triglycerides, blood pressure, creatinine, and hemoglobin
- Rule engine informed by common CDC, WHO, and cardiometabolic screening ranges
- Production-style training pipeline for a UCI-backed cardiometabolic screening model
- Explainable risk summaries with confidence, top factors, and next-step guidance
- Ephemeral upload handling with immediate file deletion after analysis

## Architecture

The project keeps the existing Flask app structure and extends it with modular services and training assets.

```text
MOKSHA/
|-- app.py
|-- train_model.py
|-- datasets/
|   |-- raw/
|   |-- processed/
|   |-- README.md
|   `-- source_catalog.json
|-- models/
|-- training/
|   |-- dataset_loader.py
|   |-- preprocessing.py
|   `-- model_training.py
|-- medical_report_app/
|   |-- config.py
|   |-- constants.py
|   |-- routes.py
|   |-- services/
|   |   |-- clinical_rules.py
|   |   |-- ml.py
|   |   |-- ocr.py
|   |   |-- presentation.py
|   |   |-- report_analysis.py
|   |   |-- report_parser.py
|   |   `-- risk.py
|   `-- utils/
|       |-- files.py
|       `-- privacy.py
|-- templates/
`-- static/
```

## Dataset

Primary training dataset:

- UCI Machine Learning Repository, Heart Disease
- URL: https://archive.ics.uci.edu/dataset/45/heart+disease
- DOI: 10.24432/C52P4X
- License: CC BY 4.0

Why this dataset was selected:

- It is a legitimate public healthcare dataset from the preferred source hierarchy.
- It supports a classification task aligned with cardiovascular screening support.
- It includes medically relevant attributes such as age, sex, resting blood pressure, cholesterol, and fasting blood sugar flags.
- It includes historical identifier-like columns in the broader schema, which makes it useful for demonstrating privacy removal logic.

Dataset handling workflow:

1. `train_model.py` fetches the dataset through `ucimlrepo`.
2. Any column that looks like PII is dropped automatically before preprocessing.
3. Sanitized caches are written to `datasets/raw/` and `datasets/processed/`.
4. The final model bundle and training report are saved under `models/`.

## Privacy policy

MOKSHA is designed with privacy-first defaults:

- Uploaded report images are never kept permanently for inference.
- The uploaded file is deleted immediately after OCR and analysis complete, even when an error occurs.
- OCR debug output is redacted before rendering to the browser.
- Training pipelines remove PII-like columns automatically before preprocessing.
- The application is designed to retain only medically useful extracted markers when persistence is needed in the future.

Examples of identifiers explicitly excluded from training and persistence:

- Name
- Address
- Phone number
- Email
- Hospital ID
- Patient ID
- Aadhaar or Aadhar
- Social Security Number
- Report number
- Barcode
- Signature

## Training process

Run the model training pipeline with:

```bash
python train_model.py
```

The training pipeline:

- Loads the UCI Heart Disease dataset
- Removes PII-like columns automatically
- Curates medically relevant features
- Cleans missing values with imputation
- Normalizes numerical features
- Encodes categorical features
- Splits train and test sets
- Trains multiple candidate models
- Evaluates accuracy, precision, recall, F1, and ROC AUC
- Selects the best-performing model automatically
- Saves the final bundle with `joblib`

Candidate models:

- Logistic Regression
- Random Forest
- Gradient Boosting
- XGBoost, only when the package is installed

Saved artifacts:

- `models/cardiometabolic_risk_bundle.joblib`
- `models/training_report.json`

## Explainability

At inference time, MOKSHA returns:

- Risk level
- Confidence score
- Top contributing factors
- Clinical rationale
- Follow-up suggestions

Explainability strategy:

- If a trained model bundle is available, the app uses it for cardiometabolic support.
- If SHAP is installed and compatible with the saved model, SHAP-based factor ranking is attempted.
- If SHAP is unavailable, the app falls back to clinically grounded factor explanations.
- If no trained model bundle is present, the app falls back to heuristic clinical scoring rather than failing.

## OCR and extraction pipeline

OCR preprocessing includes:

- Resize
- Grayscale conversion
- CLAHE contrast enhancement
- Noise removal
- Adaptive thresholding
- Deskew
- Tesseract OCR

Value extraction includes fuzzy matching and report-context scoring for:

- Fasting glucose
- HbA1c
- Total cholesterol
- LDL
- HDL
- Triglycerides
- Blood pressure
- Creatinine
- Hemoglobin

## Clinical engine

The existing rule-based engine has been preserved and expanded. It complements the ML layer rather than replacing it.

Examples of supported interpretation logic:

- Fasting glucose and HbA1c screening ranges
- Cholesterol and lipid profile interpretation
- Blood pressure stratification
- Creatinine reference-range cautioning
- Hemoglobin and possible anemia screening

Important note:

- Clinical thresholds in MOKSHA are for screening support and should always be interpreted alongside the original laboratory reference interval and clinician judgment.

## Result dashboard

The result page now includes:

- Risk badge
- Confidence percentage
- Detected condition summary
- Recommended specialist
- Parameter interpretation
- Normal ranges
- Abnormal highlighting
- Explainable factors
- Clinical explanation
- Next steps
- Privacy notice

## Installation

## Prerequisites

Before running MOKSHA locally, make sure you have:

- Python 3.12 or 3.13
- `pip`
- Tesseract OCR installed separately on your system
- Internet access the first time you run `train_model.py`, because the UCI dataset is fetched through `ucimlrepo`

Important:

- `requirements.txt` installs the Python wrapper `pytesseract`, but it does not install the Tesseract OCR engine itself.
- Without Tesseract installed, the report-upload OCR workflow will not function.

## Tesseract OCR setup

Official Tesseract documentation:

- Tesseract installation guide: [tessdoc Installation](https://tesseract-ocr.github.io/tessdoc/Installation.html)
- Main Tesseract repository: [tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract)

Windows setup:

1. Install Tesseract OCR using the Windows installer referenced by the official Tesseract docs:
   [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install it to the default path if possible:
   `C:\Program Files\Tesseract-OCR\tesseract.exe`
3. Optionally add `C:\Program Files\Tesseract-OCR` to your system `PATH`.
4. Verify the installation from a new terminal:

```powershell
tesseract --version
```

If Tesseract is installed in a different location, set the environment variable before running the app:

```powershell
$env:TESSERACT_CMD="C:\Path\To\Tesseract-OCR\tesseract.exe"
```

Then start the app in the same terminal.

macOS setup:

- Install with Homebrew:

```bash
brew install tesseract
```

Linux setup:

- On Ubuntu or Debian:

```bash
sudo apt install tesseract-ocr
```

Language data note:

- The app primarily expects English-language lab reports.
- If you need additional OCR languages, install the corresponding Tesseract language data supported by your platform.

Base dependencies:

```bash
pip install -r requirements.txt
```

Optional enhancements:

- Install optional ML and explainability packages separately with:

```bash
pip install -r requirements-optional.txt
```

- `xgboost` for additional model comparison
- `shap` for model explainability

## Requirements

Current required packages:

- Flask
- pytesseract
- opencv-python
- numpy
- scikit-learn
- Werkzeug
- pandas
- joblib
- ucimlrepo

Optional packages:

- xgboost
- shap

Optional dependency file:

- `requirements-optional.txt` for advanced model training and explainability extras

## Running the app

Recommended local setup order:

```bash
pip install -r requirements.txt
pip install -r requirements-optional.txt
python train_model.py
python app.py
```

If you do not want optional packages, you can skip the second command.

Windows users who installed Tesseract in a non-default location should set:

```powershell
$env:TESSERACT_CMD="C:\Path\To\Tesseract-OCR\tesseract.exe"
```

before running `python app.py`.

```bash
python app.py
```

Then open the Flask URL shown in the console and upload a supported image report.

## Troubleshooting

Common local setup issues:

- `ModuleNotFoundError: No module named 'pandas'`
  Install core dependencies with `pip install -r requirements.txt`

- `tesseract is not recognized` or OCR does not work
  Install Tesseract separately and verify with `tesseract --version`

- Tesseract is installed but the app still cannot find it
  Set `TESSERACT_CMD` to the full `tesseract.exe` path before starting the app

- `train_model.py` fails on first run
  Check internet access because the dataset download happens at training time

## Model evaluation

Training writes structured evaluation output to `models/training_report.json`.

The evaluation report includes:

- Selected model
- Accuracy
- Precision
- Recall
- F1 score
- ROC AUC
- Comparison across all trained candidate models

This separation keeps model governance auditable and makes future retraining easier.

## Security notes

- Reports are handled as transient files only.
- Uploaded filenames are replaced with generated identifiers before temporary storage.
- PII redaction is applied to OCR text shown in debug mode.
- The training pipeline is privacy-aware by default.

## Future scope

The codebase is organized so it can expand into:

- PDF report ingestion
- Hospital or LIS integration
- FHIR-compatible payload generation
- Longitudinal patient history support
- Multi-model condition packs
- Imaging workflows such as X-ray assistance
- Structured clinician review dashboards
- Audit logging and model registry support

## Production-readiness notes

This repository is a strong prototype foundation, not a regulated medical device.

Before real-world deployment, add:

- Human validation workflows
- Dataset version pinning and reproducible model registries
- Access control and encryption at rest
- Full audit logging
- Bias and subgroup performance checks
- Clinical safety review
- Monitoring for OCR drift and model drift
- Input validation for PDFs and larger file types
- Containerization and CI/CD with security scanning

## Medical ethics statement

MOKSHA is intentionally designed as a support system, not a diagnosis engine.

Its purpose is to:

- Highlight potentially important findings
- Improve report readability
- Support faster triage conversations
- Encourage timely follow-up with licensed clinicians

It must not be used as a substitute for professional medical evaluation, emergency care, or individualized treatment decisions.
