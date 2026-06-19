from medical_report_app.constants import TEST_DEFINITIONS


def format_value(value):
    if value is None:
        return "Not detected"
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.1f}"


def build_value_rows(values):
    rows = []
    for key, definition in TEST_DEFINITIONS.items():
        rows.append(
            {
                "name": definition["label"],
                "value": format_value(values.get(key)),
                "unit": definition["unit"] if values.get(key) is not None else "-",
                "range": f"{definition['range'][0]}-{definition['range'][1]}",
                "detected": values.get(key) is not None,
            }
        )
    return rows
