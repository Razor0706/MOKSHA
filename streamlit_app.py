import tempfile
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
from flask import render_template

from medical_report_app import create_app
from medical_report_app.config import BASE_DIR
from medical_report_app.services.report_analysis import analyze_report

# Initialize Flask App for template rendering
flask_app = create_app()

st.set_page_config(
    page_title="MOKSHA - AI Diagnostic Support System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load original static CSS file
css_path = BASE_DIR / "static" / "style.css"
css_content = css_path.read_text(encoding="utf-8") if css_path.exists() else ""

# Helper to inject inline CSS into Flask rendered HTML
def get_clean_html(template_name, **context):
    with flask_app.test_request_context("/"):
        rendered_html = render_template(template_name, **context)
        # Replace external CSS link tag with actual inline CSS rules
        clean_html = rendered_html.replace(
            '<link rel="stylesheet" href="/static/style.css">',
            f"<style>{css_content}</style>",
        )
        return clean_html

# Sidebar Navigation & Upload
with st.sidebar:
    st.title("🏥 MOKSHA")
    st.markdown("### Upload Medical Report")
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=["png", "jpg", "jpeg"],
        help="Supports PNG, JPG, JPEG report images",
    )

# Main Content Display
if uploaded_file is None:
    # Render original landing page with full CSS styling
    try:
        html_out = get_clean_html("index.html")
        components.html(html_out, height=850, scrolling=True)
    except Exception:
        st.info("👈 Please upload a medical report image from the sidebar to begin analysis.")
else:
    # Process uploaded report image
    file_suffix = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as temp_file:
        temp_file.write(uploaded_file.getvalue())
        temp_path = Path(temp_file.name)

    with st.spinner("Analyzing report..."):
        try:
            result = analyze_report(temp_path)
            html_out = get_clean_html("result.html", **result)
            components.html(html_out, height=1800, scrolling=True)
        except Exception as err:
            html_out = get_clean_html("result.html", error=str(err))
            components.html(html_out, height=600, scrolling=True)
