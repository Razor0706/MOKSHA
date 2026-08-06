import os
import tempfile
from pathlib import Path
import streamlit as st

from medical_report_app.config import configure_ocr_engine
from medical_report_app.services.report_analysis import analyze_report

# Configure OCR engine path if set in environment
configure_ocr_engine()

st.set_page_config(
    page_title="MOKSHA - Diagnostic Support Prototype",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for modern UI aesthetics
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .metric-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .risk-high {
        color: #dc2626;
        font-weight: bold;
    }
    .risk-moderate {
        color: #d97706;
        font-weight: bold;
    }
    .risk-low {
        color: #16a34a;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-header">🏥 MOKSHA</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">AI-Assisted Medical Report Screening & Explainable Risk Summary</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("About MOKSHA")
    st.info(
        "**MOKSHA** by Nexora Technologies is an AI-assisted diagnostic support prototype for medical report interpretation. "
        "It combines OCR, biomarker extraction, clinical rules, and machine learning to produce explainable risk summaries."
    )
    st.warning(
        "⚠️ **Diagnostic Support Only**: MOKSHA does not diagnose diseases, replace clinicians, "
        "or override laboratory interpretations."
    )
    st.markdown("---")
    st.markdown("**Supported Report Formats:** PNG, JPG, JPEG")

uploaded_file = st.file_uploader(
    "Upload a clear lab report image to analyze",
    type=["png", "jpg", "jpeg"],
    help="Upload an image of a medical laboratory report.",
)

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Medical Report Image", use_container_width=True)
    
    if st.button("🚀 Analyze Report", type="primary"):
        with st.spinner("Processing image, running OCR, and executing clinical screening..."):
            # Save uploaded file to temporary path
            file_suffix = Path(uploaded_file.name).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as temp_file:
                temp_file.write(uploaded_file.getvalue())
                temp_path = Path(temp_file.name)

            try:
                result = analyze_report(temp_path)
                
                st.success("Analysis Complete!")
                st.markdown("---")

                # Key Diagnostics Overview
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Report Type", result.get("report_type", "Standard Report"))
                
                risk = result.get("risk", {})
                risk_level = risk.get("level", "N/A").capitalize()
                confidence = risk.get("confidence")
                conf_str = f" ({confidence}% confidence)" if confidence else ""
                
                with col2:
                    st.metric("Risk Level", f"{risk_level}{conf_str}")

                with col3:
                    st.metric("Condition Detected", result.get("condition", "N/A"))

                with col4:
                    st.metric("Recommended Specialist", result.get("specialist", "General Physician"))

                st.markdown("---")

                # AI Explainability & Clinical Reasoning
                col_left, col_right = st.columns(2)
                
                with col_left:
                    st.subheader("📊 AI Support Details")
                    st.write(f"**Top Contributing Factors:** {', '.join(risk.get('top_factors', [])) if risk.get('top_factors') else 'Clinical review required'}")
                    st.write(f"**Model Support:** {risk.get('model_name', 'Rule Engine')}")
                    st.write(f"**Clinical Rationale:** {risk.get('explanation', '')}")

                with col_right:
                    st.subheader("🛡️ Privacy & Compliance Notice")
                    st.write(result.get("privacy_notice", ""))

                st.markdown("---")

                # Extracted Biomarker Summary Table
                st.subheader("🧪 Extracted Biomarker Summary")
                value_rows = result.get("value_rows", [])
                
                if value_rows:
                    table_data = []
                    for row in value_rows:
                        val_str = f"{row['value']}" if row['value'] is not None else "Not Detected"
                        table_data.append({
                            "Biomarker": row["label"],
                            "Extracted Value": val_str,
                            "Unit": row["unit"],
                            "Normal Reference Range": row["normal_range"],
                            "Status": row["status"],
                            "Interpretation": row["interpretation"],
                        })
                    st.table(table_data)
                else:
                    st.warning("No structured biomarkers could be extracted from this image.")

                # OCR Debug Output (Redacted)
                with st.expander("🔍 View Redacted OCR Raw Text"):
                    st.text(result.get("ocr_text", ""))

            except Exception as e:
                st.error(f"Analysis Error: {str(e)}")
