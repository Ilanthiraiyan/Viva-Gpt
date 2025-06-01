# doc_analyzer_web.py

import streamlit as st
from docx import Document
from gtts import gTTS
import os
import tempfile
import openai

# Get OpenAI API key securely from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

LANGUAGES = {
    'English': 'en',
    'Hindi (हिन्दी)': 'hi',
    'Tamil (தமிழ்)': 'ta',
    'Telugu (తెలుగు)': 'te',
    'Malayalam (മലയാളം)': 'ml',
    'Kannada (ಕನ್ನಡ)': 'kn',
    'Bengali (বাংলা)': 'bn',
    'Marathi (मराठी)': 'mr',
    'Gujarati (ગુજરાતી)': 'gu',
    'Punjabi (ਪੰਜਾਬੀ)': 'pa',
    'Urdu (اردو)': 'ur',
    'Sanskrit (संस्कृतम्)': 'sa',
    'Spanish (Español)': 'es',
    'French (Français)': 'fr',
    'German (Deutsch)': 'de',
    'Chinese (中文)': 'zh-CN',
    'Japanese (日本語)': 'ja',
    'Korean (한국어)': 'ko'
}

st.set_page_config(page_title="Multilingual Document Analyzer", layout="wide")
st.title("📄 VivaGPT - Document Simplifier + Translator + Voice")
st.markdown("Upload a `.docx` file to simplify and translate it. Output will be explained like a teacher in your language!")

language_name = st.selectbox("Choose Output Language", list(LANGUAGES.keys()), index=0)
language_code = LANGUAGES[language_name]

uploaded_file = st.file_uploader("📁 Upload a .docx file", type=["docx"])

if uploaded_file:
    try:
        doc = Document(uploaded_file)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        summary_text = "\n".join(paragraphs)
        preview = summary_text[:1000] + "..." if len(summary_text) > 1000 else summary_text

        prompt = f"Simplify and explain this document content for a common person:\n{preview}"

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You simplify and explain documents in layman's language."},
                {"role": "user", "content": prompt}
            ]
        )

        simplified = response.choices[0].message.content
        translated = simplified

        if language_code != 'en':
            translation_prompt = f"""
            Translate the following content into **easy-to-understand, spoken {language_name}** suitable for college students.

            Guidelines:
            - Write like a friendly mentor explaining it to students who may not be familiar with technical words.
            - Use simple, clear, and polite language — like you’re talking to someone face-to-face.
            - Keep bullet points, numbering, and formatting intact.
            - Translate or transliterate words like 'resume', 'project', 'PDF', and 'viva' into {language_name} in the most commonly used student-friendly way.
            - Do not use robotic or overly formal tone. Prioritize clarity and usefulness.

            Now translate this:
            \"\"\"
            {simplified}
            \"\"\"
            """

            translation_response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You translate simplified English content for Indian students into their local language."},
                    {"role": "user", "content": translation_prompt}
                ]
            )
            translated = translation_response.choices[0].message.content


        st.text_area("📑 Analysis Output", translated, height=400)

        if st.button("🔊 Read Aloud"):
            tts = gTTS(text=translated, lang=language_code)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tts.save(tmp.name)
                audio_path = tmp.name
            st.audio(audio_path, format="audio/mp3")

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
