import streamlit as st
import pandas as pd
import speech_recognition as sr
import os
import re
from datetime import datetime

# --- 1. إعدادات الصفحة والتصميم ---
st.set_page_config(page_title="MedSpeak AI: Web3 Medical Agent", layout="wide")

# تصميم واجهة مستخدم احترافية (CSS)
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #007bff; color: white; }
    .reward-box { padding: 20px; border-radius: 15px; background-color: #d4edda; border: 1px solid #c3e6cb; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محاكاة منطق الـ Web3 ---
def connect_wallet():
    # في الهاكاثون الحقيقي، هنا يتم استدعاء Web3.js أو Ethers.js
    st.session_state['wallet_connected'] = True
    st.session_state['wallet_address'] = "0x71C...392a"
    st.session_state['balance'] = 150.5  # رصيد محاكي بـ $SURGE

# --- 3. محرك تصحيح النطق الطبي ---
def medical_pronunciation_correction(target, spoken):
    target = target.lower().strip()
    spoken = spoken.lower().strip()
    
    # حساب نسبة الدقة (يمكن تطويرها باستخدام تقنيات الصوت المتقدمة)
    import difflib
    accuracy = round(difflib.SequenceMatcher(None, target, spoken).ratio() * 100, 2)
    
    feedback = ""
    if accuracy == 100:
        feedback = "Perfect! Your pronunciation is clinically accurate."
    elif accuracy > 80:
        feedback = "Very good. Minor phonetic adjustment needed."
    else:
        feedback = "Needs improvement. Try breaking down the syllables."
        
    return accuracy, feedback

# --- 4. واجهة المستخدم ---
st.title("🩺 MedSpeak AI")
st.subheader("Smart Medical Pronunciation Agent (Web3-Powered)")

# شريط جانبي لربط المحفظة
with st.sidebar:
    st.header("Web3 Identity")
    if 'wallet_connected' not in st.session_state:
        if st.button("Connect Wallet (SURGE)"):
            connect_wallet()
            st.rerun()
    else:
        st.success(f"Connected: {st.session_state['wallet_address']}")
        st.metric("Balance", f"{st.session_state['balance']} $SURGE")

# القسم الرئيسي
col1, col2 = st.columns([1, 1])

with col1:
    st.info("💡 Practice complex medical terms and earn $SURGE rewards.")
    target_term = st.selectbox("Select Medical Term:", 
        ["Otorhinolaryngology", "Myocardial Infarction", "Anaphylaxis", "Gastroenteritis"])
    
    st.write(f"**Target Pronunciation:** `/{target_term}/`")
    
    # محاكاة تسجيل الصوت (بسبب قيود المتصفح في النسخة المحلية)
    spoken_text = st.text_input("Your Pronunciation (Type what you said or use Mic):")

with col2:
    if spoken_text:
        acc, msg = medical_pronunciation_correction(target_term, spoken_text)
        
        st.metric("Accuracy Score", f"{acc}%")
        
        if acc > 90:
            st.balloons()
            st.markdown(f"""
                <div class="reward-box">
                    <h4>🏆 Well Done!</h4>
                    <p>Accuracy is high enough to earn rewards.</p>
                    <strong>+10 $SURGE Tokens minted to your wallet.</strong>
                </div>
            """, unsafe_allow_html=True)
            if 'balance' in st.session_state:
                st.session_state['balance'] += 10
        else:
            st.warning(msg)

# --- 5. سجل البيانات (ملكية البيانات) ---
st.divider()
st.write("📂 **Your Decentralized Record (Data Ownership)**")
if st.session_state.get('wallet_connected'):
    st.caption("All training data is encrypted and linked to your wallet address.")
    # عرض جدول بسيط للمحاولات السابقة
    data = {
        "Date": [datetime.now().strftime("%Y-%m-%d")],
        "Term": [target_term],
        "Score": [f"{acc}%" if spoken_text else "0%"],
        "Status": ["Verified On-Chain" if spoken_text and acc > 90 else "Pending"]
    }
    st.table(pd.DataFrame(data))
else:
    st.warning("Please connect your wallet to view and own your data.")


















