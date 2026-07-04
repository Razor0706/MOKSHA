from .clinical_rules import assess_parameters


def format_value(value):
    if value is None:
        return "Not detected"
    if isinstance(value, str):
        return value
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.1f}"


def build_value_rows(values):
    _, ordered_rows = assess_parameters(values)
    formatted_rows = []
    for row in ordered_rows:
        formatted_rows.append(
            {
                "name": row["label"],
                "value": format_value(row["value"]),
                "unit": row["unit"] if row["value"] is not None else "-",
                "range": row["normal_range"],
                "detected": row["value"] is not None,
                "status": row["status"],
                "flag_class": row["flag_class"],
                "interpretation": row["interpretation"],
            }
        )
    return formatted_rows
