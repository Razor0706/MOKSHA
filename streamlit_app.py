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
    initial_sidebar_state="collapsed",
)

# Load original static CSS file
css_path = BASE_DIR / "static" / "style.css"
css_content = css_path.read_text(encoding="utf-8") if css_path.exists() else ""

# Inject global CSS into Streamlit
st.markdown(
    f"""
    <style>
    {css_content}
    .stApp {{
        background-color: #0b0f19;
    }}
    .block-container {{
        padding: 1rem 1rem !important;
        max-width: 100% !important;
    }}
    iframe {{
        border: none !important;
        width: 100% !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar File Uploader
with st.sidebar:
    st.title("🏥 MOKSHA")
    st.markdown("### Upload Medical Report")
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=["png", "jpg", "jpeg"],
        help="Supports PNG, JPG, JPEG report images",
    )

# Main Content Area
if uploaded_file is None:
    # Render the exact original landing page (templates/index.html)
    with flask_app.test_request_context("/"):
        try:
            rendered_html = render_template("index.html")
            full_html = f"<!DOCTYPE html><html><head><style>{css_content}</style></head><body>{rendered_html}</body></html>"
            components.html(full_html, height=850, scrolling=True)
        except Exception as e:
            st.info("👈 Please upload a medical report image from the sidebar to begin analysis.")

else:
    # Save file temporarily and run analysis
    file_suffix = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as temp_file:
        temp_file.write(uploaded_file.getvalue())
        temp_path = Path(temp_file.name)

    with st.spinner("Analyzing report..."):
        try:
            result = analyze_report(temp_path)
            with flask_app.test_request_context("/"):
                rendered_html = render_template("result.html", **result)
                full_html = f"<!DOCTYPE html><html><head><style>{css_content}</style></head><body>{rendered_html}</body></html>"
                components.html(full_html, height=1500, scrolling=True)
        except Exception as err:
            with flask_app.test_request_context("/"):
                rendered_html = render_template("result.html", error=str(err))
                full_html = f"<!DOCTYPE html><html><head><style>{css_content}</style></head><body>{rendered_html}</body></html>"
                components.html(full_html, height=600, scrolling=True)
