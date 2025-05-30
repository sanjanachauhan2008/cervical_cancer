import streamlit as st
import joblib
import numpy as np
from fpdf import FPDF
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

# Load model
MODEL_PATH = "cervicalcancer.pkl"
model = joblib.load(MODEL_PATH)

# Supported languages
languages = {
    "English": "en",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr"
}

# Translation dictionary (partial for demonstration)
translations = {
    "Patient Details": {
        "hi": "रोगी का विवरण",
        "es": "Detalles del paciente",
        "fr": "Détails du patient"
    },
    "Name": {"hi": "नाम", "es": "Nombre", "fr": "Nom"},
    "Location": {"hi": "स्थान", "es": "Ubicación", "fr": "Emplacement"},
    "Country": {"hi": "देश", "es": "País", "fr": "Pays"},
    "Submit": {"hi": "जमा करें", "es": "Enviar", "fr": "Soumettre"},
    "Download PDF Report": {
        "hi": "पीडीएफ रिपोर्ट डाउनलोड करें",
        "es": "Descargar informe PDF",
        "fr": "Télécharger le rapport PDF"
    }
}

def t(text, lang):
    return translations.get(text, {}).get(lang, text)

def create_pdf(patient_name, prediction_result, details):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 50, "Cervical Cancer Risk Assessment Report")

    c.setFont("Helvetica", 10)
    c.drawString(40, height - 80, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(40, height - 100, f"Patient Name: {patient_name}")
    c.drawString(40, height - 120, f"Prediction Result: {'At Risk' if prediction_result == 1 else 'No Risk'}")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, height - 150, "Entered Details:")

    y = height - 170
    c.setFont("Helvetica", 10)
    for key, value in details.items():
        if y < 50:
            c.showPage()
            y = height - 50
        c.drawString(60, y, f"{key}: {value}")
        y -= 15

    c.save()
    buffer.seek(0)
    return buffer

# App config
st.set_page_config(page_title="Cervical Cancer Predictor", page_icon="🏥", layout="wide")

# Language selection
selected_lang = st.sidebar.selectbox("🌐 Select Language", list(languages.keys()))
lang_code = languages[selected_lang]

# Title
st.markdown(
    f"<h1 style='text-align: center; color: navy;'>🧬 {'Cervical Cancer Diagnosis Application'}</h1>",
    unsafe_allow_html=True
)

# Sidebar
with st.sidebar:
    st.header(f"👩‍⚕️ {t('Patient Details', lang_code)}")
    user_name = st.text_input(f"📝 {t('Name', lang_code)}")
    user_location = st.text_input(f"📍 {t('Location', lang_code)}")
    user_country = st.text_input(f"🌍 {t('Country', lang_code)}")

# Tabs
tab1, tab2 = st.tabs(["🧾 Input Form", "📊 Prediction Result"])

with tab1:
    with st.form("cervical_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            gender = st.radio("Gender", ["Female", "Male"])
            Age = st.slider("Age", 1, 110, 30)
            PoR = st.radio("Place of Residence", ["Rural", "Urban"])
            ES = st.radio("Educational Status", ["Illiterate", "Literate"])
            SES = st.radio("Socio-economic Status", ["Lower", "Middle", "Upper"])

        with col2:
            Parity = st.radio("Parity", ["None", "≤2", "more_than_2"])
            AgefirstP = st.radio("Age at First Full-Term Pregnancy", ["≤20", "more_than_20"])
            MC = st.radio("Menstrual Cycle", ["Regular", "Irregular"])
            MH = st.radio("Menstrual Hygiene", ["Napkin", "Cloths"])
            Contraception = st.radio("Use of Contraception", ["Oral contraceptive pills", "Others"])

        with col3:
            Smoking = st.radio("Smoking", ["Passive", "Active"])
            HRHPV = st.radio("High-risk HPV", ["Negative", "Positive"])
            IL6 = st.radio("IL6", ['GG', 'AA', 'AG'])
            IL1beta = st.radio("IL1beta", ['TT', 'CT', 'CC'])
            TNFalpha = st.radio("TNFalpha", ['GG', 'AA', 'GA'])
            IL1RN = st.selectbox("IL1RN", ['I I', 'II II', 'I II', 'I IV', 'II III', 'I III', 'II IV'])

        submitted = st.form_submit_button(t("Submit", lang_code))

        if submitted:
            st.success("✅ Prediction submitted! Go to the next tab to view the result.")

with tab2:
    if submitted:
        gender_val = 1 if gender == "Male" else 0
        PoR_val = 2 if PoR == "Urban" else 0
        ES_val = 2 if ES == "Literate" else 1
        SES_val = {"Lower": 3, "Middle": 2, "Upper": 1}[SES]
        Parity_val = {"None": 1, "≤2": 2, "more_than_2": 3}[Parity]
        AgefirstP_val = 1 if AgefirstP == "≤20" else 2
        MC_val = 1 if MC == "Regular" else 2
        MH_val = 1 if MH == "Napkin" else 2
        Contraception_val = 1 if Contraception == "Others" else 2
        Smoking_val = 1 if Smoking == "Active" else 2
        HRHPV_val = 2 if HRHPV == "Positive" else 1
        IL6_val = {"AG": 2, "AA": 1, "GG": 3}[IL6]
        IL1beta_val = {"TT": 1, "CT": 2, "CC": 3}[IL1beta]
        TNFalpha_val = {"GG": 1, "AA": 2, "GA": 3}[TNFalpha]
        IL1RN_val = {
            'I I': 1, 'II II': 2, 'I II': 3, 'I IV': 4, 'II III': 5, 'I III': 6, 'II IV': 7
        }.get(IL1RN, 0)

        input_data = np.array([[Age, PoR_val, ES_val, SES_val, Parity_val, AgefirstP_val,
                                MC_val, MH_val, Contraception_val, Smoking_val, HRHPV_val,
                                IL6_val, IL1beta_val, TNFalpha_val, IL1RN_val]])

        result = model.predict(input_data)
        patient_display = user_name.strip() if user_name else "Patient"

        st.markdown("### 🧪 Prediction Result")
        if gender_val == 1:
            st.warning("⚠️ This prediction tool is intended for biological females. Your result may be invalid.")
        elif result[0] == 1:
            st.error(f"🔬 {patient_display}, you may have a risk of Cervical Cancer.")
        else:
            st.success(f"✅ {patient_display}, no indication of Cervical Cancer risk was found.")
            st.balloons()

        # Generate and download PDF
        patient_details = {
            "Name": user_name,
            "Location": user_location,
            "Country": user_country,
            "Age": Age,
            "Gender": gender,
            "PoR": PoR,
            "Education": ES,
            "SES": SES,
            "Parity": Parity,
            "First Pregnancy Age": AgefirstP,
            "Menstrual Cycle": MC,
            "Menstrual Hygiene": MH,
            "Contraception": Contraception,
            "Smoking": Smoking,
            "HPV": HRHPV,
            "IL6": IL6,
            "IL1beta": IL1beta,
            "TNFalpha": TNFalpha,
            "IL1RN": IL1RN
        }
        pdf_data = create_pdf(patient_display, result[0], patient_details)
        st.download_button(
            label=t("Download PDF Report", lang_code),
            data=pdf_data,
            file_name="cervical_cancer_report.pdf",
            mime="application/pdf"
        )

        # Helpful resources section
        st.markdown("### 🌐 Find Help or More Information")

        st.markdown(
            """
            - 🔍 [Search Nearby Gynecologists on Google Maps](https://www.google.com/maps/search/gynecologist+near+me)
            - 🏥 [Search Hospitals Near You](https://www.google.com/maps/search/hospitals+near+me)
            - 📚 [WHO Cervical Cancer Info](https://www.who.int/health-topics/cervical-cancer)
            - 📖 [CDC Cervical Cancer Resources](https://www.cdc.gov/cancer/cervical/)
            - 💡 [National Cancer Institute – Cervical Cancer](https://www.cancer.gov/types/cervical)
            """
        )

        if user_location:
            search_query = user_location.replace(" ", "+")
            map_url = f"https://www.google.com/maps/search/gynecologist+in+{search_query}"
            st.markdown(f"🔍 [Find gynecologists near {user_location}]({map_url})")
