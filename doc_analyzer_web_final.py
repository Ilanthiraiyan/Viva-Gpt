# doc_analyzer_web.py

import streamlit as st
from docx import Document
from gtts import gTTS
import os
import tempfile
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
openai_key = st.secrets["OPENAI_API_KEY"]


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
st.title("📄 Multilingual Document Analyzer")
st.markdown("Upload a `.docx` document to analyze and translate its content into your chosen language.")

# Get OpenAI API key from .env
openai_key = st.secrets["OPENAI_API_KEY"]

language_name = st.selectbox("Choose Output Language", list(LANGUAGES.keys()), index=0)
language_code = LANGUAGES[language_name]

uploaded_file = st.file_uploader("Upload .docx file", type=["docx"])

if uploaded_file and openai_key:
    try:
        openai.api_key = openai_key
        doc = Document(uploaded_file)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        total_words = sum(len(p.split()) for p in paragraphs)
        total_chars = sum(len(p) for p in paragraphs)

        summary_text = "\n".join(paragraphs)
        preview = summary_text[:1000] + "..." if len(summary_text) > 1000 else summary_text

        prompt = f"Simplify and explain this document content for a common person:\n{preview}"

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You simplify and explain documents in layman's language."},
                {"role": "user", "content": prompt}
            ]
        )

        simplified = response['choices'][0]['message']['content']
        translated = simplified

        if language_code != 'en':
            translation_prompt = (
                f"Translate the following into {language_name} in natural, polite, and easily understandable {language_name}. "
                f"Use student-friendly words. Keep original structure (like bullet points or numbered items). "
                f"Translate UI terms like 'resume', 'viva', and 'PDF' into commonly used {language_name} equivalents. "
                f"Avoid robotic or literal translation. Write like a human explaining it to students:\n\n{simplified}"
            )
            translation_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You translate simplified English text into Indian regional languages clearly."},
                    {"role": "user", "content": translation_prompt}
                ]
            )
            translated = translation_response['choices'][0]['message']['content']

        st.text_area("📑 Analysis Output", translated, height=400)

        if st.button("🔊 Read Aloud"):
            tts = gTTS(text=translated, lang=language_code)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tts.save(tmp.name)
                audio_path = tmp.name
            st.audio(audio_path, format="audio/mp3")

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
