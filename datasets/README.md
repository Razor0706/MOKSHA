# Datasets

This project is configured to train against the UCI Heart Disease dataset and cache sanitized copies locally.

- Source: UCI Machine Learning Repository, Heart Disease
- URL: https://archive.ics.uci.edu/dataset/45/heart+disease
- DOI: 10.24432/C52P4X
- License: CC BY 4.0

The `train_model.py` script downloads the dataset through `ucimlrepo`, removes any PII-like columns automatically, and writes cached copies into `datasets/raw/` and `datasets/processed/`.

This folder intentionally stores dataset metadata and caches rather than personal report uploads.
