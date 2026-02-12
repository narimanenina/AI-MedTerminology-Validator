import streamlit as st
import pandas as pd
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
import io
import difflib
from pydub import AudioSegment  # تأكد من تثبيت pydub

# --- دالة معالجة الصوت وتحويله ---
def process_audio(audio_bytes):
    try:
        # تحويل الصوت من الصيغة المسجلة (غالباً webm/ogg) إلى WAV
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
        wav_io = io.BytesIO()
        audio_segment.export(wav_io, format="wav")
        wav_io.seek(0)
        
        r = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            audio_data = r.record(source)
            # استخدام لغة إنجليزية طبية
            text = r.recognize_google(audio_data, language="en-US")
            return text
    except Exception as e:
        return None

# --- واجهة التطبيق المحدثة ---
st.title("🩺 MedSpeak AI: Voice Analysis")

# تحميل البيانات (تأكد من وجود الملف أو البيانات الاحتياطية)
terms = ["Otorhinolaryngology", "Anaphylaxis", "Myocardial Infarction"]
selected_term = st.selectbox("Select Term:", terms)

st.write("Record your pronunciation:")

# التسجيل الصوتي
audio_record = mic_recorder(
    start_prompt="⏺️ Record",
    stop_prompt="⏹️ Stop",
    key='medical_recorder'
)

if audio_record:
    # التحقق من وجود بيانات صوتية لتجنب ValueError
    if audio_record.get('bytes') is not None:
        with st.spinner("Analyzing..."):
            result = process_audio(audio_record['bytes'])
            
            if result:
                st.success(f"I heard: {result}")
                # حساب الدقة
                acc = round(difflib.SequenceMatcher(None, selected_term.lower(), result.lower()).ratio() * 100)
                st.metric("Accuracy", f"{acc}%")
                
                if acc > 85:
                    st.balloons()
                    st.info("Reward: +20 $SURGE added to your vault.")
            else:
                st.error("Could not process audio. Please try again clearly.")
    else:
        st.warning("No audio data captured.")















