# MOKSHA

MOKSHA is a Flask-based AI-assisted healthcare screening prototype for medical report interpretation. It combines OCR, biomarker extraction, rule-based clinical screening, and optional machine-learning support to produce explainable risk summaries while preserving medical ethics and privacy-by-design principles.

MOKSHA is a diagnostic support tool only. It does not diagnose disease, replace a clinician, or override laboratory interpretation.

## Core capabilities

- **Multi-Domain Report Parsing**: OCR-driven extraction supporting 35+ biomarkers across 9 major clinical domains (Glycemic, Lipid, Kidney/Renal, Liver/LFT, CBC/Hematology, Thyroid, Vitamins & Minerals, Inflammation, Vitals).
- **Smart Row Filtering**: Dynamically hides non-detected parameters to render clean, context-specific laboratory result tables.
- **Minimum Detection Threshold**: Enforces validation (`MIN_BIOMARKER_THRESHOLD`) to ensure adequate data before running risk analysis.
- **Multi-Dataset ML Infrastructure**: Automated fetching, PII sanitization, and model training across multiple UCI datasets (Heart Disease, Diabetes, Indian Liver Patient Dataset).
- **Rule Engine & Multi-Specialist Referrals**: Expanded clinical rules mapping findings to relevant condition warnings and chaining specialist recommendations (Endocrinologist, Nephrologist, Hepatologist, Hematologist, Cardiologist, etc.).
- **Dual Web Architecture**: Native Flask web application alongside a Streamlit cloud wrapper (`streamlit_app.py`) for 1-click free deployment.
- **Privacy-by-Design**: Ephemeral upload handling with immediate temporary file deletion and automatic PII redaction.

## Architecture

The project keeps a modular Flask and Streamlit architecture extended with clinical interpretation services and multi-dataset training pipelines.

```text
MOKSHA/
|-- app.py
|-- streamlit_app.py
|-- train_model.py
|-- packages.txt
|-- Dockerfile
|-- datasets/
|   |-- raw/
|   |   |-- heart_disease_raw.csv
|   |   |-- diabetes_raw.csv
|   |   `-- liver_raw.csv
|   |-- processed/
|   |   |-- heart_disease_training.csv
|   |   |-- diabetes_training.csv
|   |   `-- liver_training.csv
|   |-- README.md
|   `-- source_catalog.json
|-- models/
|   |-- cardiometabolic_risk_bundle.joblib
|   `-- training_report.json
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
|   |   |-- risk.py
|   |   `-- text_processing.py
|   `-- utils/
|       |-- files.py
|       `-- privacy.py
|-- templates/
`-- static/
```

## Datasets

MOKSHA leverages public, peer-reviewed healthcare datasets from the UCI Machine Learning Repository for training and evaluating clinical risk support models:

1. **UCI Heart Disease Dataset (ID: 45)**
   - URL: https://archive.ics.uci.edu/dataset/45/heart+disease
   - DOI: 10.24432/C52P4X | License: CC BY 4.0
   - Primary dataset for cardiovascular and cardiometabolic risk classification.

2. **UCI Diabetes Dataset (ID: 89)**
   - URL: https://archive.ics.uci.edu/dataset/89/diabetes
   - License: CC BY 4.0
   - Multi-feature dataset for diabetes screening and glycemic risk estimation.

3. **UCI Indian Liver Patient Dataset / ILPD (ID: 225)**
   - URL: https://archive.ics.uci.edu/dataset/225/ilpd+indian+liver+patient+dataset
   - License: CC BY 4.0
   - Used for hepatic risk screening, transaminase (ALT/AST), ALP, and bilirubin analysis.

### Dataset Handling Workflow

1. `train_model.py` fetches raw datasets via `ucimlrepo`.
2. Any column matching PII (patient ID, identifiers) is automatically dropped via `drop_pii_columns` prior to feature curation.
3. Raw and processed datasets are cached locally under `datasets/raw/` and `datasets/processed/`.
4. Model artifacts and multi-model evaluation reports are compiled under `models/`.

## Privacy Policy

MOKSHA is designed with privacy-first defaults:

- **Zero Permanent File Storage**: Uploaded report images are deleted immediately after OCR and analysis complete, even when an error occurs.
- **OCR PII Redaction**: Debug OCR text displayed during local testing is stripped of patient identifiers before browser rendering.
- **Automated Pipeline PII Removal**: Training pipelines automatically strip personal identifiers before dataset caching and preprocessing.

Identifiers explicitly excluded:
- Name, Address, Phone number, Email
- Patient ID, Hospital ID, Report number
- Aadhaar / SSN / Barcodes / Signatures

## Training Process

Run the multi-dataset training pipeline with:

```bash
python train_model.py
```

The training pipeline:
- Fetches and caches UCI Heart Disease, Diabetes, and Liver datasets
- Strips PII automatically across all data streams
- Curates features, handles missing values via imputation, and normalizes numeric inputs
- Encodes categorical variables and splits training/testing partitions
- Trains candidate classifiers: Logistic Regression, Random Forest, Gradient Boosting, and XGBoost (if installed)
- Evaluates metrics: Accuracy, Precision, Recall, F1 Score, ROC AUC
- Automatically selects the optimal model bundle and exports `models/cardiometabolic_risk_bundle.joblib` and `models/training_report.json`

Candidate models:
- Logistic Regression
- Random Forest
- Gradient Boosting
- XGBoost (when package is present)

Saved artifacts:
- `models/cardiometabolic_risk_bundle.joblib`
- `models/training_report.json`

## Supported Biomarkers & Clinical Panels

MOKSHA parses and interprets 35+ parameters across 9 distinct medical domains:

1. **Glycemic Profile**: Fasting Glucose, HbA1c
2. **Lipid Profile**: Total Cholesterol, LDL, HDL, Triglycerides
3. **Vitals**: Blood Pressure (Systolic & Diastolic)
4. **Kidney / Renal Function (RFT)**: Serum Creatinine, Urea, Uric Acid, eGFR, Sodium (Na+), Potassium (K+)
5. **Liver Function Test (LFT)**: ALT (SGPT), AST (SGOT), Alkaline Phosphatase (ALP), Total Bilirubin, Direct Bilirubin, Albumin, Total Protein
6. **Complete Blood Count (CBC) / Hematology**: Hemoglobin, Total Leukocyte Count (WBC), Platelet Count, RBC Count, Hematocrit (PCV), ESR
7. **Thyroid Profile**: TSH, Free T3, Free T4
8. **Vitamins & Minerals**: Vitamin D (25-OH), Vitamin B12, Serum Calcium, Serum Iron, Serum Ferritin
9. **Inflammatory Profile**: High-Sensitivity C-Reactive Protein (hs-CRP)

## OCR and Extraction Pipeline

OCR preprocessing includes:
- Resize & Grayscale conversion
- CLAHE contrast enhancement
- Noise removal & Adaptive thresholding
- Deskew & Tesseract OCR engine extraction

Value extraction features:
- Regex pattern matching combined with fuzzy text matching and domain context scoring (`_has_relevant_context`)
- **Minimum Detection Threshold**: Requires at least 1 valid detected biomarker (`MIN_BIOMARKER_THRESHOLD`) to prevent invalid or speculative analysis
- **Smart Filtering**: Non-detected biomarkers are omitted from UI result tables to display clean, concise lab summaries

## Clinical Engine & Explainability

- **Multi-domain condition detection**: Diabetes Risk, Cardiovascular Risk, Kidney Function Concern, Hepatic Stress / Enzyme Elevation, Possible Anemia, Leukocytosis, Thrombocyte Imbalance, Thyroid Dysfunction, Vitamin / Deficiency Caution, Systemic Inflammation Warning.
- **Referral Chaining**: Recommends specialized medical follow-ups (Endocrinologist, Nephrologist, Gastroenterologist / Hepatologist, Hematologist, Cardiologist, General Physician).
- **Explainable Risk Scoring**: Combines ML risk classification (SHAP / heuristic feature ranking) with evidence-based clinical screening rules.

## Result Dashboard

The result UI includes:
- Risk Severity Badge & Confidence Level
- Identified Clinical Condition Summaries
- Recommended Specialist Referral(s)
- Clean Biomarker Table (showing only detected values with reference ranges & status flags)
- Explainable Risk Factor Breakdown & Next Steps
- Privacy & Ephemeral Data Notice

## Installation

### Prerequisites

- Python 3.12 or 3.13
- `pip`
- Tesseract OCR installed separately on your system
- Internet access on first run to fetch UCI datasets via `ucimlrepo`

### Tesseract OCR Setup

Windows setup:
1. Install Tesseract OCR using the Windows installer: [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
2. Default path: `C:\Program Files\Tesseract-OCR\tesseract.exe`
3. Verify installation:
   ```powershell
   tesseract --version
   ```

macOS setup:
```bash
brew install tesseract
```

Linux setup:
```bash
sudo apt install tesseract-ocr
```

### Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-optional.txt
```

## Running the App

### Recommended Local Flask Setup

```bash
pip install -r requirements.txt
pip install -r requirements-optional.txt
python train_model.py
python app.py
```

Open the local Flask URL printed in your console.

### Running with Streamlit

To run MOKSHA using the Streamlit interface:

```bash
streamlit run streamlit_app.py
```

## Deployment

### Streamlit Community Cloud (Recommended - 100% Free Forever)

1. Push your repository to GitHub.
2. Log in to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Click **New app** -> Select your GitHub repository.
4. Set Main file path to: `streamlit_app.py`.
5. Click **Deploy!**

*(Note: `packages.txt` automatically installs `tesseract-ocr` system dependencies on Streamlit Cloud).*

### Render Docker Setup

1. Push the deployment branch to GitHub and create a Render **Web Service**.
2. Select **Docker** runtime.
3. Set `TESSERACT_CMD` to `/usr/bin/tesseract`.
4. Set `SECRET_KEY` in environment variables.
5. Set health-check path as `/health`.

## Model Evaluation

Training writes evaluation output to `models/training_report.json`, including accuracy, precision, recall, F1 score, and ROC AUC metrics across all trained model candidates.

## Security & Privacy Notes

- Temporary report files are deleted immediately after analysis.
- PII redaction is automatically applied to OCR text.
- PII columns are automatically excluded during dataset training.

## License

Licensed under the Apache License 2.0. See `LICENSE` for details.

## Medical Ethics Statement

MOKSHA is intentionally designed as a diagnostic support system, not a diagnosis engine. It must not be used as a substitute for professional medical evaluation, emergency care, or individualized treatment decisions.
