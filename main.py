import streamlit as st
import pandas as pd
import speech_recognition as sr
import io
import difflib
import os
from pydub import AudioSegment
from streamlit_mic_recorder import mic_recorder
from datetime import datetime

# --- 1. إعدادات المنصة ---
st.set_page_config(page_title="MedSpeak AI | Web3 Agent", layout="wide")

# تصميم واجهة مستخدم احترافية
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .definition-box { padding: 20px; border-radius: 10px; background-color: #e9ecef; border-left: 5px solid #007bff; margin-bottom: 20px; }
    .reward-banner { padding: 15px; border-radius: 10px; background: linear-gradient(90deg, #28a745, #218838); color: white; text-align: center; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. تحميل البيانات ---
@st.cache_data
def load_data():
    file_path = 'medical_master_db.csv'
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        st.error("Missing medical_master_db.csv file!")
        return pd.DataFrame()

df_med = load_data()

# --- 3. محاكاة منطق الـ Web3 والمكافآت ---
if 'wallet' not in st.session_state:
    st.session_state['wallet'] = {"address": "0x71C...392a", "balance": 0.0, "connected": False}

def connect_wallet():
    st.session_state['wallet']['connected'] = True
    st.session_state['wallet']['balance'] = 150.0 # رصيد ابتدائي افتراضي

def save_onchain_log(term, accuracy, reward):
    log_file = 'web3_learning_logs.xlsx'
    new_entry = {
        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'Student_Wallet': st.session_state['wallet']['address'],
        'Term': term,
        'Accuracy': f"{accuracy}%",
        'Reward_Claimed': f"{reward} $SURGE"
    }
    df_new = pd.DataFrame([new_entry])
    if os.path.exists(log_file):
        df_old = pd.read_excel(log_file)
        pd.concat([df_old, df_new], ignore_index=True).to_excel(log_file, index=False)
    else:
        df_new.to_excel(log_file, index=False)

# --- 4. واجهة المستخدم الجانبية (Sidebar) ---
with st.sidebar:
    st.title("🌐 Web3 Identity")
    if not st.session_state['wallet']['connected']:
        if st.button("🔌 Connect Wallet (Surge)"):
            connect_wallet()
            st.rerun()
    else:
        st.success(f"Connected: {st.session_state['wallet']['address']}")
        st.metric("Balance", f"{st.session_state['wallet']['balance']} $SURGE")
        st.info("Identity verified on Moltbook Protocol.")

# --- 5. منطقة التعلم الرئيسية ---
st.title("🩺 MedSpeak: AI Pronunciation Agent")
st.write("Master medical terminology, own your learning data, and earn rewards.")

if not df_med.empty:
    # اختيار المصطلح (عرض باللغتين لسهولة البحث)
    selected_term_idx = st.selectbox(
        "Select Medical Term / اختر المصطلح الطبي:",
        range(len(df_med)),
        format_func=lambda x: f"{df_med.iloc[x]['term_en']} | {df_med.iloc[x]['term_ar']}"
    )
    
    term_info = df_med.iloc[selected_term_idx]

    # عرض التعريفات بـ 3 لغات
    with st.expander("📖 View Definitions / عرض التعاريف", expanded=True):
        col_en, col_fr, col_ar = st.columns(3)
        with col_en:
            st.markdown(f"**English**\n\n{term_info['def_en']}")
        with col_fr:
            st.markdown(f"**Français**\n\n{term_info['def_fr']}")
        with col_ar:
            st.markdown(f"**العربية**\n\n{term_info['def_ar']}")

    st.divider()

    # قسم التسجيل والتحليل
    col_practice, col_result = st.columns([1, 1])

    with col_practice:
        st.subheader("🎤 Practice Session")
        st.write(f"Target Pronunciation (IPA): `/{term_info['ipa']}/`")
        st.write(f"Difficulty: **{term_info['difficulty']}** | Reward: **{term_info['reward_surge']} $SURGE**")
        
        audio_record = mic_recorder(
            start_prompt="⏺️ Click to Speak",
            stop_prompt="⏹️ Analyze My Voice",
            key='medical_agent'
        )

    with col_result:
        if audio_record:
            try:
                with st.spinner("AI Agent is analyzing phonemes..."):
                    # معالجة الصوت وتحويله لـ WAV
                    audio_segment = AudioSegment.from_file(io.BytesIO(audio_record['bytes']))
                    wav_io = io.BytesIO()
                    audio_segment.export(wav_io, format="wav")
                    wav_io.seek(0)
                    
                    r = sr.Recognizer()
                    with sr.AudioFile(wav_io) as source:
                        audio_data = r.record(source)
                        # التعرف على الكلام بالإنجليزية الطبية
                        heard_text = r.recognize_google(audio_data, language="en-US")
                    
                    # حساب دقة النطق
                    accuracy = round(difflib.SequenceMatcher(None, term_info['term_en'].lower(), heard_text.lower()).ratio() * 100)
                    
                    st.subheader("📊 Analysis Result")
                    st.write(f"AI Heard: **'{heard_text}'**")
                    st.metric("Accuracy Score", f"{accuracy}%")
                    
                    if accuracy >= 80:
                        st.balloons()
                        st.markdown(f"""
                            <div class="reward-banner">
                                🏆 Success! +{term_info['reward_surge']} $SURGE tokens minted to your wallet.
                            </div>
                        """, unsafe_allow_html=True)
                        if st.session_state['wallet']['connected']:
                            st.session_state['wallet']['balance'] += term_info['reward_surge']
                            save_onchain_log(term_info['term_en'], accuracy, term_info['reward_surge'])
                    else:
                        st.warning("Accuracy is low. Pay attention to the IPA guide and try again.")
            except Exception:
                st.error("Could not recognize audio. Please try to speak more clearly or check your mic.")

# --- 6. شفافية البيانات (Data Ownership) ---
st.divider()
if st.checkbox("🔍 View My Decentralized Learning History"):
    if os.path.exists('web3_learning_logs.xlsx'):
        history = pd.read_excel('web3_learning_logs.xlsx')
        st.dataframe(history, use_container_width=True)
    else:
        st.info("No learning records found on-chain yet.")











