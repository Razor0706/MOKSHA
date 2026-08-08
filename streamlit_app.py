"""Streamlit entry point for the MOKSHA diagnostic-support prototype."""

import re
import tempfile
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from flask import render_template

from medical_report_app import create_app
from medical_report_app.config import BASE_DIR
from medical_report_app.services.report_analysis import analyze_report


MAX_UPLOAD_BYTES = 5 * 1024 * 1024
RESULT_FRAME_HEIGHT = 1800

DARK_TEMPLATE_CSS = """
:root {
    --page: #0d1720;
    --surface: #14212c;
    --ink: #e7f0f5;
    --muted: #a9bbc7;
    --line: #2c4250;
    --primary: #43b6d9;
    --primary-dark: #2383a4;
    --green: #52c986;
    --orange: #f2a547;
    --red: #f07171;
    --gray: #9caeb9;
    --soft-green: #153a2a;
    --soft-orange: #402b16;
    --soft-red: #421f26;
    --shadow: 0 18px 45px rgba(0, 0, 0, 0.3);
}

body {
    background: radial-gradient(circle at top left, rgba(67, 182, 217, 0.18), transparent 34%),
        linear-gradient(135deg, #101b24 0%, var(--page) 48%, #142b24 100%);
}

.hero-content, .capability-panel, .summary-card, .product-section, .insight-card,
.alert-card, .ocr-debug, .file-drop, .metric-tile, .privacy-strip {
    background: var(--surface) !important;
    border-color: var(--line) !important;
}

.file-drop, .metric-tile { background: #182833 !important; }
.privacy-strip { background: #102a36 !important; border-color: #275168 !important; }
.privacy-strip strong { color: #76d3ee; }
.notice-card { background: #182833 !important; border-color: var(--line) !important; }
.notice-card p, .notice-card strong { color: var(--ink) !important; }
table { background: #14212c !important; }
table thead, table th { background: #1a303d !important; color: #a9bbc7 !important; }
table td { color: #e7f0f5 !important; border-color: var(--line) !important; }
table tbody tr:nth-child(even), .table-row.normal { background: #172630 !important; }
table tbody tr:nth-child(odd), .table-row.moderate { background: #332612 !important; }
.table-row.high { background: #351d25 !important; }
.status-pill.missing, .risk-badge.unknown { background: #273a47 !important; color: #c4d2da !important; }
.disclaimer { border-color: #80414a !important; background: #351d25 !important; color: #ff9d9d !important; }
.ocr-debug pre { background: #0b131a !important; color: #dbe8ee !important; }
"""

STREAMLIT_EMBED_CSS = """
html, body { width: 100%; overflow-x: hidden; }
.landing-shell, .dashboard-shell {
    width: calc(100% - 32px);
    max-width: 1380px;
    padding: 24px 0;
}
"""


st.set_page_config(
    page_title="MOKSHA - AI Diagnostic Support System",
    page_icon="M",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_flask_app():
    """Reuse Flask only for rendering the established report templates."""
    return create_app()


def load_css():
    css_path = BASE_DIR / "static" / "style.css"
    return css_path.read_text(encoding="utf-8") if css_path.exists() else ""


def render_template_html(template_name, dark_mode=False, **context):
    flask_app = get_flask_app()
    with flask_app.test_request_context("/"):
        rendered_html = render_template(template_name, embedded_mode=True, **context)

    # The iframe cannot control Streamlit navigation, so hide template links here.
    theme_css = DARK_TEMPLATE_CSS if dark_mode else ""
    inline_css = f"<style>{load_css()} {STREAMLIT_EMBED_CSS} {theme_css}</style>"
    return rendered_html.replace('<link rel="stylesheet" href="/static/style.css">', inline_css)


def remove_landing_form(html):
    """Keep the existing landing design while replacing its Flask form with Streamlit upload controls."""
    return re.sub(
        r'<form class="upload-form".*?</form>',
        '<div class="privacy-strip"><strong>Upload:</strong> Use the secure uploader above to analyze a report.</div>',
        html,
        count=1,
        flags=re.DOTALL,
    )


def reset_analysis():
    st.session_state.page = "home"
    st.session_state.result = None
    st.session_state.error_message = None
    st.session_state.uploader_version += 1


def initialize_session():
    st.session_state.setdefault("page", "home")
    st.session_state.setdefault("result", None)
    st.session_state.setdefault("error_message", None)
    st.session_state.setdefault("uploader_version", 0)
    st.session_state.setdefault("dark_mode", False)

    # Keep the selected appearance after a browser refresh without storing health data.
    saved_theme = st.query_params.get("theme")
    if saved_theme in {"dark", "light"}:
        st.session_state.dark_mode = saved_theme == "dark"


def save_theme_preference():
    """Persist only the UI preference in the URL, never report data."""
    st.query_params["theme"] = "dark" if st.session_state.dark_mode else "light"


def inject_streamlit_theme(dark_mode):
    """Theme Streamlit controls to match the selected report theme."""
    if not dark_mode:
        return

    st.markdown(
        """
        <style>
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
            background: #0d1720;
            color: #e7f0f5;
        }
        [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {
            background: #0d1720 !important;
        }
        [data-testid="stSidebar"] { background: #14212c; border-right: 1px solid #2c4250; }
        [data-testid="stSidebar"] * { color: #e7f0f5; }
        [data-testid="stFileUploaderDropzone"] { background: #182833; border-color: #3d6274; }
        [data-testid="stFileUploaderDropzone"] * { color: #dbe8ee; }
        [data-testid="stButton"] button,
        [data-testid="stBaseButton-secondary"] {
            background: #182833 !important;
            border-color: #3d6274 !important;
            color: #e7f0f5 !important;
        }
        [data-testid="stButton"] button[kind="primary"],
        [data-testid="stBaseButton-primary"] {
            background: #2383a4 !important;
            border-color: #43b6d9 !important;
            color: #ffffff !important;
        }
        [data-testid="stButton"] button:hover,
        [data-testid="stBaseButton-secondary"]:hover { background: #244352 !important; color: #ffffff !important; }
        [data-testid="stButton"] button[kind="primary"]:hover,
        [data-testid="stBaseButton-primary"]:hover { background: #43b6d9 !important; }
        [data-testid="stImage"] img { border: 1px solid #2c4250; }
        [data-testid="stCaptionContainer"] { color: #a9bbc7; }
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li,
        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3 { color: inherit; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def analyze_uploaded_file(uploaded_file):
    if uploaded_file.size > MAX_UPLOAD_BYTES:
        raise ValueError("Please upload an image smaller than 5 MB.")

    suffix = Path(uploaded_file.name).suffix.lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(uploaded_file.getvalue())
        temp_path = Path(temp_file.name)

    # analyze_report owns deletion of the temporary file, including failure paths.
    return analyze_report(temp_path)


def show_sidebar():
    with st.sidebar:
        st.title("MOKSHA")
        st.caption("AI-assisted medical report screening")
        st.toggle("Dark mode", key="dark_mode", on_change=save_theme_preference)
        st.divider()

        if st.session_state.page == "result":
            st.button("Analyze another report", use_container_width=True, on_click=reset_analysis)
        else:
            st.markdown("### Before you upload")
            st.caption("Use a clear PNG, JPG, or JPEG image smaller than 5 MB.")
            st.caption("Reports are processed temporarily and deleted after analysis.")

        st.divider()
        st.caption("Diagnostic support only. Not a diagnosis or treatment recommendation.")


def show_home():
    st.markdown("## Upload a medical report")
    st.caption("PNG, JPG, or JPEG only. Files are deleted after analysis.")
    uploaded_file = st.file_uploader(
        "Choose a report image",
        type=["png", "jpg", "jpeg"],
        key=f"medical_report_{st.session_state.uploader_version}",
        label_visibility="collapsed",
    )

    if uploaded_file is None:
        landing_html = remove_landing_form(
            render_template_html("index.html", dark_mode=st.session_state.dark_mode)
        )
        components.html(landing_html, height=650, scrolling=True)
        return

    st.image(uploaded_file, caption=f"Selected file: {uploaded_file.name}", width="stretch")
    st.caption(f"File size: {uploaded_file.size / (1024 * 1024):.2f} MB")

    if st.button("Analyze report", type="primary", use_container_width=True):
        with st.spinner("Reading the report and extracting biomarkers..."):
            try:
                st.session_state.result = analyze_uploaded_file(uploaded_file)
                st.session_state.error_message = None
                st.session_state.page = "result"
                st.rerun()
            except ValueError as error:
                st.session_state.error_message = str(error)
            except Exception:
                st.session_state.error_message = (
                    "The report could not be analyzed. Please upload a clearer supported image and try again."
                )

    if st.session_state.error_message:
        st.error(st.session_state.error_message)


def show_result():
    top_left, top_right = st.columns([4, 1])
    with top_left:
        st.markdown("## Diagnostic Support Summary")
        st.caption("Review extracted values against the original laboratory report.")
    with top_right:
        st.button("Back to upload", use_container_width=True, on_click=reset_analysis)

    if st.session_state.result is not None:
        result_html = render_template_html(
            "result.html",
            dark_mode=st.session_state.dark_mode,
            **st.session_state.result,
        )
        components.html(result_html, height=RESULT_FRAME_HEIGHT, scrolling=True)
    else:
        st.error(st.session_state.error_message or "No result is available for this report.")


def main():
    initialize_session()
    inject_streamlit_theme(st.session_state.dark_mode)
    show_sidebar()

    if st.session_state.page == "result":
        show_result()
    else:
        show_home()


if __name__ == "__main__":
    main()
