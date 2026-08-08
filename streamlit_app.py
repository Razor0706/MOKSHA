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


def render_template_html(template_name, **context):
    flask_app = get_flask_app()
    with flask_app.test_request_context("/"):
        rendered_html = render_template(template_name, **context)

    # The iframe cannot control Streamlit navigation, so hide template links here.
    inline_css = f"<style>{load_css()} .back-link {{ display: none !important; }}</style>"
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
        landing_html = remove_landing_form(render_template_html("index.html"))
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
        result_html = render_template_html("result.html", **st.session_state.result)
        components.html(result_html, height=RESULT_FRAME_HEIGHT, scrolling=True)
    else:
        st.error(st.session_state.error_message or "No result is available for this report.")


def main():
    initialize_session()
    show_sidebar()

    if st.session_state.page == "result":
        show_result()
    else:
        show_home()


if __name__ == "__main__":
    main()
