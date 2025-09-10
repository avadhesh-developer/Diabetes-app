import streamlit as st
import requests
import pandas as pd

API_BASE = "http://localhost:8000"

#  Custom CSS 
st.markdown(
    """
    <style>
        /* Global background */
        .stApp {
            background: #f8f9fa;
            font-family: "Segoe UI", sans-serif;
        }

        /* Header style */
        h1, h2, h3 {
            color: #2c3e50;
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #f0f2f6;
            border-right: 2px solid #ddd;
        }

        /* Buttons */
        div.stButton > button:first-child {
            background-color: #2e86de;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 0.6em 1.2em;
            font-weight: 600;
            transition: 0.3s;
        }
        div.stButton > button:first-child:hover {
            background-color: #1b4f72;
            color: #f0f0f0;
        }

        /* Success / error messages */
        .stSuccess {
            background-color: #d4efdf;
            border: 1px solid #27ae60;
            border-radius: 8px;
            padding: 10px;
        }
        .stError {
            background-color: #fadbd8;
            border: 1px solid #c0392b;
            border-radius: 8px;
            padding: 10px;
        }
        .stInfo {
            background-color: #d6eaf8;
            border: 1px solid #2980b9;
            border-radius: 8px;
            padding: 10px;
        }

        /* Tabs */
        .stTabs [role="tab"] {
            background-color: #ecf0f1;
            padding: 10px 20px;
            border-radius: 8px 8px 0 0;
            font-weight: 600;
            margin-right: 5px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #2e86de !important;
            color: white !important;
        }

        /* Dataframe table */
        .stDataFrame, .stTable {
            border-radius: 10px;
            border: 1px solid #ccc;
            overflow: hidden;
            box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
        }

        /* Inputs */
        input, textarea {
            border-radius: 6px !important;
            border: 1px solid #bbb !important;
            padding: 0.5em !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

#  App Config 
st.set_page_config(
    page_title="Healthcare - Diabetes Prediction & Research Chatbot",
    layout="wide",
    page_icon="🩸"
)

#  Main Header 
st.title("🩸 Diabetes Prediction App")
st.markdown("Predict diabetes risk, manage patient records, and explore research insights.")

#  Sidebar Input 
with st.sidebar:
    st.header("📋 Input Parameters")
    with st.form("prediction_form"):
        pregnancies = st.number_input("Pregnancies", min_value=0, max_value=20, value=1)
        glucose = st.number_input("Glucose", min_value=0.0, max_value=200.0, value=120.0)
        blood_pressure = st.number_input("Blood Pressure", min_value=0.0, max_value=150.0, value=70.0)
        skin_thickness = st.number_input("Skin Thickness", min_value=0.0, max_value=100.0, value=20.0)
        insulin = st.number_input("Insulin", min_value=0.0, max_value=900.0, value=80.0)
        bmi = st.number_input("BMI", min_value=0.0, max_value=70.0, value=25.0)
        dpf = st.number_input("Diabetes Pedigree Function", min_value=0.0, max_value=2.5, value=0.5)
        age = st.number_input("Age", min_value=1, max_value=120, value=30)
        submit = st.form_submit_button("⚡ Predict")

if submit:
    data = {
        "pregnancies": pregnancies,
        "glucose": glucose,
        "blood_pressure": blood_pressure,
        "skin_thickness": skin_thickness,
        "insulin": insulin,
        "bmi": bmi,
        "diabetes_pedigree_function": dpf,
        "age": age
    }
    try:
        response = requests.post(f"{API_BASE}/predict", json=data)
        if response.status_code == 200:
            result = response.json()
            st.success(f" Diabetes Risk: {'Positive' if result['diabetes_risk'] else 'Negative'}")
            st.info(f" Record ID: {result.get('record_id')} (stored in database)")
        else:
            st.error("❌ Prediction failed. Backend error.")
    except Exception as e:
        st.error(f"⚠️ Error: {e}")

#  Tabs Section 
st.header("📁 Advanced Data Processing")
st.markdown("Upload patient datasets, analyze medical PDFs, or view stored records.")

tab1, tab2, tab3 = st.tabs(["📊 CSV Batch Processing", "📄 PDF Document Analysis", "📋 Patient Records"])

with tab1:
    st.subheader("📊 Batch Predictions from CSV")
    csv_file = st.file_uploader("Upload CSV file", type=["csv"])
    if csv_file is not None and st.button(" Process CSV batch"):
        with st.spinner("Processing..."):
            try:
                files = {"file": (csv_file.name, csv_file.getvalue(), "text/csv")}
                resp = requests.post(f"{API_BASE}/predict/csv", files=files, timeout=30)
                if resp.ok:
                    data = resp.json()
                    st.success(f"✅ Processed {data['count']} patient records")
                    preds_df = pd.DataFrame({"Prediction": data["predictions"]})
                    st.dataframe(preds_df, use_container_width=True)
                else:
                    st.error(f"❌ CSV processing failed: {resp.status_code} {resp.text}")
            except Exception as e:
                st.error(f"⚠️ Error: {e}")

with tab2:
    st.subheader("📄 AI-Powered PDF Analysis")
    pdf_file = st.file_uploader("Upload PDF file", type=["pdf"])
    if pdf_file is not None and st.button(" Analyze PDF"):
        with st.spinner("processing..."):
            try:
                files = {"file": (pdf_file.name, pdf_file.getvalue(), "application/pdf")}
                resp = requests.post(f"{API_BASE}/predict/pdf", files=files, timeout=30)
                if resp.ok:
                    data = resp.json()
                    st.info(f" {data.get('message', 'Analysis complete')}")
                    if "features" in data:
                        df = pd.DataFrame(list(data["features"].items()), columns=["Feature", "Value"])
                        st.table(df)
                    if "prediction" in data:
                        st.metric("Diabetes Risk", data["prediction"])
                else:
                    st.error(f"❌ PDF analysis failed: {resp.status_code}")
            except Exception as e:
                st.error(f"⚠️ Error: {e}")

with tab3:
    st.subheader("📋 Patient Records Database")
    if st.button(" Refresh Records"):
        st.session_state["records_refresh"] = True

    if st.session_state.get("records_refresh"):
        with st.spinner("Fetching patient records..."):
            try:
                resp = requests.get(f"{API_BASE}/records", timeout=15)
                if resp.ok:
                    records = resp.json()
                    if records:
                        st.success(f" Found {len(records)} patient records")
                        df = pd.DataFrame(records)[[
                            "id", "glucose", "blood_pressure", "bmi", 
                            "age", "diabetes_pedigree_function","predicted", "created_at",
                        ]]
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("📝 No records yet")
                else:
                    st.error(f"❌ Fetch failed: {resp.status_code} {resp.text}")
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
        st.session_state["records_refresh"] = False

# ---- Research Chatbot ----
st.header("🤖 Research Chatbot")
question = st.text_input("Ask about diabetes research or prevention")
if st.button("💬 Ask"):
    with st.spinner("Thinking..."):
        try:
            resp = requests.post(f"{API_BASE}/chat", json={"question": question}, timeout=30)
            if resp.ok:
                st.info(f"💡 {resp.json().get('answer', 'No answer')}")
            else:
                st.error(f"❌ Chat failed: {resp.status_code}")
        except Exception as e:
            st.error(f"⚠️ Error: {e}")
