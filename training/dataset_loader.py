from pathlib import Path
import pandas as pd

from medical_report_app.config import DATASETS_DIR
from medical_report_app.constants import CARDIO_MODEL_FEATURES
from medical_report_app.utils.privacy import drop_pii_columns


RAW_HEART_PATH = DATASETS_DIR / "raw" / "heart_disease_raw.csv"
PROCESSED_HEART_PATH = DATASETS_DIR / "processed" / "heart_disease_training.csv"

RAW_DIABETES_PATH = DATASETS_DIR / "raw" / "diabetes_raw.csv"
PROCESSED_DIABETES_PATH = DATASETS_DIR / "processed" / "diabetes_training.csv"

RAW_LIVER_PATH = DATASETS_DIR / "raw" / "liver_raw.csv"
PROCESSED_LIVER_PATH = DATASETS_DIR / "processed" / "liver_training.csv"


def _import_ucirepo():
    try:
        from ucimlrepo import fetch_ucirepo
    except ImportError as error:
        raise RuntimeError(
            "ucimlrepo is required to fetch UCI datasets. Install it with `pip install ucimlrepo`."
        ) from error
    return fetch_ucirepo


# --- 1. Heart Disease Dataset (ID: 45) ---

def load_uci_heart_disease_dataset(force_refresh=False):
    if PROCESSED_HEART_PATH.exists() and not force_refresh:
        return pd.read_csv(PROCESSED_HEART_PATH)

    fetch_ucirepo = _import_ucirepo()
    dataset = fetch_ucirepo(id=45)
    features = dataset.data.features.copy()
    target = dataset.data.targets.copy()

    features, _ = drop_pii_columns(features)
    target_series = pd.to_numeric(target.iloc[:, 0], errors="coerce")
    training_frame = features.copy()
    training_frame["target"] = (target_series > 0).astype(int)
    training_frame = training_frame.dropna(subset=["target"])

    available_features = [column for column in CARDIO_MODEL_FEATURES if column in training_frame.columns]
    curated_frame = training_frame[available_features + ["target"]].copy()

    DATASETS_DIR.mkdir(parents=True, exist_ok=True)
    (DATASETS_DIR / "raw").mkdir(parents=True, exist_ok=True)
    (DATASETS_DIR / "processed").mkdir(parents=True, exist_ok=True)

    curated_frame.to_csv(PROCESSED_HEART_PATH, index=False)
    features["target"] = training_frame["target"]
    features.to_csv(RAW_HEART_PATH, index=False)

    return curated_frame


# --- 2. Diabetes Dataset (ID: 89) ---

def load_uci_diabetes_dataset(force_refresh=False):
    if PROCESSED_DIABETES_PATH.exists() and not force_refresh:
        return pd.read_csv(PROCESSED_DIABETES_PATH)

    fetch_ucirepo = _import_ucirepo()
    dataset = fetch_ucirepo(id=89)
    features = dataset.data.features.copy()
    target = dataset.data.targets.copy()

    features, _ = drop_pii_columns(features)
    target_series = pd.to_numeric(target.iloc[:, 0], errors="coerce")
    training_frame = features.copy()
    training_frame["target"] = (target_series > 0).astype(int)
    training_frame = training_frame.dropna(subset=["target"])

    training_frame.to_csv(PROCESSED_DIABETES_PATH, index=False)
    features["target"] = training_frame["target"]
    features.to_csv(RAW_DIABETES_PATH, index=False)

    return training_frame


# --- 3. Indian Liver Patient Dataset (ID: 225) ---

def load_uci_liver_dataset(force_refresh=False):
    if PROCESSED_LIVER_PATH.exists() and not force_refresh:
        return pd.read_csv(PROCESSED_LIVER_PATH)

    fetch_ucirepo = _import_ucirepo()
    dataset = fetch_ucirepo(id=225)
    features = dataset.data.features.copy()
    target = dataset.data.targets.copy()

    features, _ = drop_pii_columns(features)
    target_series = pd.to_numeric(target.iloc[:, 0], errors="coerce")
    training_frame = features.copy()
    # ILPD targets: 1 = liver patient, 2 = non-patient
    training_frame["target"] = (target_series == 1).astype(int)
    training_frame = training_frame.dropna(subset=["target"])

    training_frame.to_csv(PROCESSED_LIVER_PATH, index=False)
    features["target"] = training_frame["target"]
    features.to_csv(RAW_LIVER_PATH, index=False)

    return training_frame


def dataset_metadata():
    return {
        "primary_dataset": "UCI Heart Disease",
        "primary_url": "https://archive.ics.uci.edu/dataset/45/heart+disease",
        "primary_doi": "10.24432/C52P4X",
        "additional_datasets": [
            {
                "name": "UCI Diabetes Dataset (ID: 89)",
                "url": "https://archive.ics.uci.edu/dataset/89/diabetes",
            },
            {
                "name": "UCI Indian Liver Patient Dataset (ID: 225)",
                "url": "https://archive.ics.uci.edu/dataset/225/ilpd+indian+liver+patient+dataset",
            },
        ],
        "license": "CC BY 4.0",
        "task": "Multi-domain clinical screening & cardiometabolic risk support",
        "note": "PII fields are dropped automatically before preprocessing across all datasets.",
    }
