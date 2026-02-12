import streamlit as st
import pandas as pd
import speech_recognition as sr
import io
import difflib
import os
import re
from pydub import AudioSegment
from streamlit_mic_recorder import mic_recorder
from datetime import datetime

# --- 1. إعدادات الصفحة والتصميم (بروح طبية وتقنية) ---
st.set_page_config(page_title="MedSpeak AI | Web3 Medical Agent", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .reward-card { 
        padding: 20px; 
        border-radius: 15px; 
        background: linear-gradient(135deg, #007bff, #6610f2); 
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة البيانات الطبية والمكافآت ---
@st.cache_data
def load_medical_db():
    # محاكاة لملف المصطلحات الطبية
    data = {
        'term': ['Otorhinolaryngology', 'Myocardial Infarction', 'Anaphylaxis', 'Gastroenteritis', 'Hypercholesterolemia'],
        'ipa': ['oʊtoʊˌraɪnoʊ', 'ˌmaɪəˈkɑːrdiəl', 'ˌænəfɪˈlæksɪs', 'ˌɡæstroʊˌɛntəˈraɪtɪs', 'ˌhaɪpərhəˌlɛstərə'],
        'difficulty': ['Hard', 'Medium', 'Medium', 'Medium', 'Hard'],
        'reward': [50, 20, 15, 15, 45]
    }
    return pd.DataFrame(data)

def save_medical_record(address, term, accuracy, reward):
    # حفظ السجل على أنه "Transaction" محاكية في الـ Web3
    db_file = 'medical_onchain_records.xlsx'
    new_tx = {
        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'Wallet_Address': address,
        'Medical_Term': term,
        'Accuracy': f"{accuracy}%",
        'Status': 'Verified & Rewarded',
        'Reward_Amount': f"{reward} $SURGE"
    }
    df_new = pd.DataFrame([new_tx])
    if os.path.exists(db_file):
        df_existing = pd.read_excel(db_file)
        df_final = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_final = df_new
    df_final.to_excel(db_file, index=False)

# --- 3. محاكاة ربط المحفظة (Web3 Integration) ---
def connect_wallet():
    st.session_state['connected'] = True
    st.session_state['address'] = "0x71C941...392a"
    st.session_state['balance'] = 1250.0

# --- 4. واجهة المستخدم الرئيسية ---
st.title("🩺 MedSpeak AI")
st.subheader("Smart Medical Pronunciation & Web3 Rewards")

# القائمة الجانبية للهوية الرقمية
with st.sidebar:
    st.header("🌐 Web3 Identity")
    if 'connected' not in st.session_state:
        if st.button("Connect Wallet (Surge)"):
            connect_wallet()
            st.rerun()
    else:
        st.markdown(f"""
        <div class='reward-card'>
            <small>Connected Wallet</small><br>
            <strong>{st.session_state['address']}</strong><br><br>
            <small>Current Balance</small><br>
            <h3>{st.session_state['balance']} $SURGE</h3>
        </div>
        """, unsafe_allow_html=True)

# منطقة ممارسة المصطلحات
df_med = load_medical_db()
col_a, col_b = st.columns([1, 1])

with col_a:
    st.info("💡 اختر مصطلحاً طبياً للتدريب عليه وكسب المكافآت.")
    target_term = st.selectbox("Select Medical Term:", df_med['term'].tolist())
    term_data = df_med[df_med['term'] == target_term].iloc[0]
    
    st.markdown(f"""
    **Phonetic Guide:** `/{term_data['ipa']}/`  
    **Difficulty:** `{term_data['difficulty']}`  
    **Potential Reward:** `{term_data['reward']} $SURGE`
    """)

with col_b:
    st.subheader("🎤 Voice Recording")
    record = mic_recorder(start_prompt="Start Recording", stop_prompt="Stop to Verify", key='med_recorder')
    
    if record:
        st.audio(record['bytes'])
        try:
            with st.spinner("Analyzing Medical Phonemes..."):
                # تحويل الصوت
                audio_segment = AudioSegment.from_file(io.BytesIO(record['bytes']))
                wav_io = io.BytesIO()
                audio_segment.export(wav_io, format="wav")
                wav_io.seek(0)
                
                r = sr.Recognizer()
                with sr.AudioFile(wav_io) as source:
                    audio_content = r.record(source)
                    # استخدام اللغة الإنجليزية للمصطلحات الطبية
                    ai_text = r.recognize_google(audio_content, language="en-US")
                
                # حساب الدقة
                accuracy = round(difflib.SequenceMatcher(None, target_term.lower(), ai_text.lower()).ratio() * 100, 1)
                
                st.metric("Pronunciation Accuracy", f"{accuracy}%")
                
                if accuracy >= 85:
                    st.balloons()
                    st.success(f"Verified! You earned {term_data['reward']} $SURGE")
                    if 'connected' in st.session_state:
                        save_medical_record(st.session_state['address'], target_term, accuracy, term_data['reward'])
                        st.session_state['balance'] += term_data['reward']
                else:
                    st.warning(f"Heard: '{ai_text}'. Accuracy too low for reward. Try again!")
                    
        except Exception as e:
            st.error("AI could not process the audio. Please speak clearly.")

# --- عرض سجل المعاملات (شفافية البيانات) ---
st.divider()
if st.checkbox("🔍 View On-Chain Learning Logs"):
    if os.path.exists('medical_onchain_records.xlsx'):
        logs = pd.read_excel('medical_onchain_records.xlsx')
        st.dataframe(logs, use_container_width=True)
    else:
        st.write("No transactions recorded yet.")













