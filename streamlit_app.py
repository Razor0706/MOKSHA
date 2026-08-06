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
    sidebar_upload = st.file_uploader(
        "Choose an image file",
        type=["png", "jpg", "jpeg"],
        help="Supports PNG, JPG, JPEG report images",
        key="sidebar_uploader",
    )

# Main Content Header & Upload Area
uploaded_file = sidebar_upload

if uploaded_file is None:
    st.markdown(
        """
        <div style="background-color: #1e293b; padding: 1.5rem; border-radius: 12px; border: 1px solid #334155; margin-bottom: 1.5rem;">
            <h2 style="color: #f8fafc; margin-top: 0;">🏥 MOKSHA — AI Diagnostic Support System</h2>
            <p style="color: #94a3b8; font-size: 1.05rem;">
                Upload a medical report image (PNG, JPG, or JPEG) below to get structured biomarker extraction,
                cardiometabolic risk scoring, condition detection, and specialist recommendations.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    main_upload = st.file_uploader(
        "📁 Click or Drag & Drop Medical Report Image Here",
        type=["png", "jpg", "jpeg"],
        key="main_uploader",
    )
    if main_upload is not None:
        uploaded_file = main_upload

# Main Content Display
if uploaded_file is None:
    # Render landing page hero details below upload box
    try:
        html_out = get_clean_html("index.html")
        # Remove original static HTML form from landing page view to prevent 405 POST error
        if '<form class="upload-form"' in html_out:
            start_idx = html_out.find('<form class="upload-form"')
            end_idx = html_out.find('</form>', start_idx) + len('</form>')
            html_out = html_out[:start_idx] + '<div class="privacy-strip"><strong>Notice:</strong> Please use the file uploader above to analyze your report.</div>' + html_out[end_idx:]
        components.html(html_out, height=650, scrolling=True)
    except Exception:
        pass

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
