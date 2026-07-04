import re

from medical_report_app.constants import PII_COLUMN_HINTS


PII_LINE_PATTERNS = [
    re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", re.IGNORECASE),
    re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\d{3}[-.\s]?){2}\d{4}\b"),
    re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"),
    re.compile(r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b"),
]

PII_LABEL_PATTERNS = [
    re.compile(r"(?i)\b(name|patient name|address|email|phone|mobile|hospital id|patient id|report number|aadhaar|aadhar|ssn|barcode)\b\s*[:\-]?\s*.+"),
    re.compile(r"(?i)\b(signature|signed by)\b\s*[:\-]?\s*.+"),
]


def drop_pii_columns(dataframe):
    columns_to_drop = []
    for column in dataframe.columns:
        normalized = re.sub(r"[^a-z0-9]+", "_", str(column).strip().lower())
        if any(hint == normalized or hint in normalized for hint in PII_COLUMN_HINTS):
            columns_to_drop.append(column)
    if columns_to_drop:
        dataframe = dataframe.drop(columns=columns_to_drop, errors="ignore")
    return dataframe, columns_to_drop


def redact_free_text_pii(text):
    redacted = text
    for pattern in PII_LINE_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    redacted_lines = []
    for line in redacted.splitlines():
        updated = line
        for pattern in PII_LABEL_PATTERNS:
            if pattern.search(updated):
                updated = pattern.sub("[REDACTED PII LINE]", updated)
        redacted_lines.append(updated)
    return "\n".join(redacted_lines)
