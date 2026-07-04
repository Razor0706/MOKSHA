from pathlib import Path

import pandas as pd

from medical_report_app.config import DATASETS_DIR
from medical_report_app.constants import CARDIO_MODEL_FEATURES
from medical_report_app.utils.privacy import drop_pii_columns


RAW_CACHE_PATH = DATASETS_DIR / "raw" / "heart_disease_raw.csv"
PROCESSED_CACHE_PATH = DATASETS_DIR / "processed" / "heart_disease_training.csv"


def _import_ucirepo():
    try:
        from ucimlrepo import fetch_ucirepo
    except ImportError as error:  # pragma: no cover - depends on runtime environment
        raise RuntimeError(
            "ucimlrepo is required to fetch the UCI Heart Disease dataset. Install it with `pip install ucimlrepo`."
        ) from error
    return fetch_ucirepo


def load_uci_heart_disease_dataset(force_refresh=False):
    if PROCESSED_CACHE_PATH.exists() and not force_refresh:
        return pd.read_csv(PROCESSED_CACHE_PATH)

    fetch_ucirepo = _import_ucirepo()
    dataset = fetch_ucirepo(id=45)
    features = dataset.data.features.copy()
    target = dataset.data.targets.copy()

    features, removed_columns = drop_pii_columns(features)
    target_series = pd.to_numeric(target.iloc[:, 0], errors="coerce")
    training_frame = features.copy()
    training_frame["target"] = (target_series > 0).astype(int)
    training_frame = training_frame.dropna(subset=["target"])

    available_features = [column for column in CARDIO_MODEL_FEATURES if column in training_frame.columns]
    missing_features = [column for column in CARDIO_MODEL_FEATURES if column not in training_frame.columns]
    if missing_features:
        raise RuntimeError(f"Dataset is missing expected training features: {', '.join(missing_features)}")

    curated_frame = training_frame[available_features + ["target"]].copy()
    curated_frame.to_csv(PROCESSED_CACHE_PATH, index=False)

    raw_export = features.copy()
    raw_export["target"] = training_frame["target"]
    raw_export.to_csv(RAW_CACHE_PATH, index=False)

    return curated_frame


def dataset_metadata():
    return {
        "name": "UCI Heart Disease",
        "source_url": "https://archive.ics.uci.edu/dataset/45/heart+disease",
        "doi": "10.24432/C52P4X",
        "license": "CC BY 4.0",
        "task": "Binary cardiometabolic risk screening support",
        "note": "PII fields are dropped automatically before preprocessing even if present in future raw copies.",
    }
