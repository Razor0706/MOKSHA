import re
from difflib import SequenceMatcher


VALUE_TOKEN_PATTERN = re.compile(r"(?<![A-Za-z0-9])[\dOoIiLl]{1,3}(?:[.,][\dOoIiLl]{1,2})?(?![A-Za-z0-9])")
BP_PATTERN = re.compile(r"(?<!\d)([0-2]?[\dOoIiLl]{2})\s*[/|\\-]\s*([0-1]?[\dOoIiLl]{2})(?!\d)")


def normalize_ocr_text(text):
    replacements = {
        "|": "l",
        "\u20b9": "",
        ",": ".",
        ";": ":",
        "\u2014": "-",
        "\u2013": "-",
    }
    for wrong, right in replacements.items():
        text = text.replace(wrong, right)
    return text


def noisy_text_variant(text):
    text = normalize_ocr_text(text).lower()
    translation = str.maketrans({"o": "0", "i": "1", "l": "1"})
    return text.translate(translation)


def normalize_numeric_token(token):
    token = token.strip()
    token = token.replace("O", "0").replace("o", "0")
    token = token.replace("I", "1").replace("i", "1").replace("l", "1")
    token = re.sub(r"[^0-9.]", "", token)
    if token.count(".") > 1:
        first_dot = token.find(".")
        token = token[: first_dot + 1] + token[first_dot + 1 :].replace(".", "")
    return token


def clean_label_text(text):
    text = normalize_ocr_text(text).lower()
    text = text.replace("0", "o").replace("1", "l")
    text = re.sub(r"[^a-z0-9\s/%-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def safe_float(token):
    normalized = normalize_numeric_token(token)
    if not normalized:
        return None
    try:
        return float(normalized)
    except ValueError:
        return None


def find_numbers(line):
    numbers = []
    for match in VALUE_TOKEN_PATTERN.finditer(line):
        token = match.group(0)
        prefix = line[max(0, match.start() - 3) : match.start()]
        if "<" in prefix or ">" in prefix:
            continue

        value = safe_float(token)
        if value is None:
            continue

        if 0.3 <= value <= 600 and int(value) not in range(1900, 2101):
            numbers.append(value)
    return numbers


def find_blood_pressure(line):
    match = BP_PATTERN.search(line)
    if not match:
        return None

    systolic = safe_float(match.group(1))
    diastolic = safe_float(match.group(2))
    if systolic is None or diastolic is None:
        return None
    if 80 <= systolic <= 240 and 40 <= diastolic <= 140:
        return int(round(systolic)), int(round(diastolic))
    return None


def similarity(left, right):
    return SequenceMatcher(None, left, right).ratio()


def keyword_score(text, keywords):
    clean_text = clean_label_text(text)
    tokens = clean_text.split()
    best = 0.0

    for keyword in keywords:
        keyword = clean_label_text(keyword)
        if keyword in clean_text:
            best = max(best, 1.0)

        keyword_parts = keyword.split()
        if len(keyword_parts) > 1:
            window_size = len(keyword_parts)
            for index in range(0, max(1, len(tokens) - window_size + 1)):
                window = " ".join(tokens[index : index + window_size])
                best = max(best, similarity(window, keyword))
        else:
            for token in tokens:
                best = max(best, similarity(token, keyword))

    return best


def range_score(value, expected_range, ideal_range):
    expected_low, expected_high = expected_range
    ideal_low, ideal_high = ideal_range

    if ideal_low <= value <= ideal_high:
        return 1.0
    if expected_low <= value <= expected_high:
        return 0.85

    nearest = expected_low if value < expected_low else expected_high
    distance = abs(value - nearest)
    return max(0.0, 0.6 - (distance / 220))
