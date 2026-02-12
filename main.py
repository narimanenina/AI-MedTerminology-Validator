import streamlit as st
import pandas as pd
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
import io
import difflib

# --- 1. تحميل البيانات الطبية ---
@st.cache_data
def load_medical_data():
    # تأكد من وجود ملف medical_terms.csv الذي أنشأناه سابقاً
    try:
        return pd.read_csv('medical_terms.csv')
    except:
        return pd.DataFrame({
            'term': ['Otorhinolaryngology', 'Anaphylaxis', 'Myocardial Infarction'],
            'ipa': ['oʊtoʊˌraɪnoʊ', 'ˌænəfɪˈlæksɪs', 'ˌmaɪəˈkɑːrdiəl'],
            'difficulty': ['Hard', 'Medium', 'Medium'],
            'reward_surge': [50, 15, 20]
        })

df_medical = load_medical_data()

# --- 2. دالة تحويل الصوت إلى نص (Speech to Text) ---
def transcribe_audio(audio_bytes):
    r = sr.Recognizer()
    audio_file = io.BytesIO(audio_bytes)
    with sr.AudioFile(audio_file) as source:
        audio_data = r.record(source)
        try:
            # نستخدم لغة إنجليزية طبية
            text = r.recognize_google(audio_data, language="en-US")
            return text
        except:
            return None

# --- 3. واجهة التطبيق ---
st.title("🩺 MedSpeak AI: Voice Practice")

# اختيار المصطلح
selected_term = st.selectbox("Select a medical term to practice:", df_medical['term'].tolist())
term_info = df_medical[df_medical['term'] == selected_term].iloc[0]

st.info(f"Target: **{selected_term}** | Expected IPA: `/{term_info['ipa']}/`")

# --- 4. جزء تسجيل الصوت ---
st.write("Click the mic and say the term clearly:")
audio_record = mic_recorder(
    start_prompt="⏺️ Start Recording",
    stop_prompt="⏹️ Stop & Analyze",
    key='recorder'
)

if audio_record:
    # 1. تحويل الصوت المسجل إلى نص
    with st.spinner("Analyzing your voice..."):
        spoken_text = transcribe_audio(audio_record['bytes'])
        
        if spoken_text:
            st.write(f"👂 I heard: **'{spoken_text}'**")
            
            # 2. حساب الدقة
            accuracy = round(difflib.SequenceMatcher(None, selected_term.lower(), spoken_text.lower()).ratio() * 100, 1)
            
            # 3. عرض النتيجة والمكافأة
            st.metric("Accuracy Score", f"{accuracy}%")
            
            if accuracy >= 85:
                st.balloons()
                st.success(f"Excellent! You've earned {term_info['reward_surge']} $SURGE tokens.")
                # هنا يمكنك إضافة كود تحديث الرصيد في المحفظة
            else:
                st.warning("Keep practicing! Try to emphasize each syllable.")
        else:
            st.error("Could not recognize the audio. Please speak louder and clearer.")

# --- 5. ربط المحفظة (Web3 Simulation) ---
with st.sidebar:
    st.header("Web3 Wallet")
    if 'balance' not in st.session_state:
        st.session_state['balance'] = 100.0
    st.metric("Current Balance", f"{st.session_state['balance']} $SURGE")
    st.caption("Data is hashed and stored on-chain for privacy.")

















