
import streamlit as st
from docx import Document
from gtts import gTTS
import openai
import tempfile

# Setup page
st.set_page_config(page_title="VivaGPT - AI Document Simplifier", layout="centered")
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Language support
LANGUAGES = {
    'English': 'en',
    'Tamil (தமிழ்)': 'ta',
    'Hindi (हिन्दी)': 'hi',
    'Telugu (తెలుగు)': 'te',
    'Malayalam (മലയാളം)': 'ml',
    'Kannada (ಕನ್ನಡ)': 'kn',
    'Bengali (বাংলা)': 'bn',
    'Marathi (मराठी)': 'mr',
    'Gujarati (ગુજરાતી)': 'gu',
    'Punjabi (ਪੰਜਾਬੀ)': 'pa',
    'Urdu (اردو)': 'ur'
}

# Header
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>📘 VivaGPT</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Understand any document in your language</h4>", unsafe_allow_html=True)
st.markdown("---")

# Language selection
language_name = st.selectbox("🌐 Choose Output Language", list(LANGUAGES.keys()), index=0)
language_code = LANGUAGES[language_name]

# 🔒 Payment session state setup
if "usage_count" not in st.session_state:
    st.session_state["usage_count"] = 0

if "paid_user" not in st.session_state:
    st.session_state["paid_user"] = False

# ✨ NEW: Ask for Gmail & check
user_email = st.text_input("Enter your Gmail ID to check premium access:")
PAID_USERS = ["user1@gmail.com", "ithiraiyan86@gmail.com"]
if user_email and user_email.strip().lower() in [email.lower() for email in PAID_USERS]:
    st.session_state.paid_user = True
    st.success("✅ Premium access activated.")


if st.session_state.usage_count >= 1 and not st.session_state.paid_user:
    st.warning("🔴 Free usage limit reached (1 file/day).")
    st.markdown("To unlock unlimited access for 7 days, please pay ₹49 using the details below:")
    st.markdown("💳 **Send ₹49 to `ithiraiya-2@okhdfcbank` on GPay or any UPI app**")
    st.markdown("📧 After payment, email your **Gmail ID** and **screenshot** to: `ithiraiyan@gmail.com` to activate your access.")
    st.stop()


# File upload
uploaded_file = st.file_uploader("📂 Upload a .docx file to analyze", type=["docx"])

if uploaded_file:
    try:
        # Read document
        doc = Document(uploaded_file)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        summary_text = "\n".join(paragraphs)
        preview = summary_text[:1000] + "..." if len(summary_text) > 1000 else summary_text

        # Step 1: Simplify
        with st.spinner("✍️ Simplifying..."):
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You simplify and explain documents in layman's language."},
                    {"role": "user", "content": f"Simplify and explain this document content for a college student:\n{preview}"}
                ]
            )
            simplified = response.choices[0].message.content
            translated = simplified

        # Step 2: Translate
        if language_code != 'en':
            with st.spinner(f"🌐 Translating to {language_name}..."):
                translation_prompt = f"""
                Translate this into easy-to-understand, spoken {language_name} for Indian families.

                - Use a natural, conversational tone.
                - Avoid robotic or overly formal language.
                - Translate or explain terms like 'resume', 'viva', 'PDF'.

                Content:
                """
                {simplified}
                """
                """
                translation_response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You translate simplified English into Indian languages for general users."},
                        {"role": "user", "content": translation_prompt}
                    ]
                )
                translated = translation_response.choices[0].message.content

        # Output
        st.success("✅ Done! See below.")
        st.text_area("📑 Result:", translated, height=400)

        # Voice
        if st.button("🔊 Read Aloud"):
            tts = gTTS(text=translated, lang=language_code)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tts.save(tmp.name)
                st.audio(tmp.name, format="audio/mp3")

        # Track usage
        st.session_state.usage_count += 1

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
