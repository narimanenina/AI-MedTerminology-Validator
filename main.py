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

# --- 1. إعدادات الصفحة والتصميم ---
st.set_page_config(page_title="مقيم نطق الأطفال", layout="centered")

# دالة تنظيف النص العربي من التشكيل
def clean_arabic(text):
    noise = re.compile(r'[\u064B-\u0652]') 
    return re.sub(noise, '', text).strip()

# تحميل بيانات الفونيمات (الرموز الصوتية)
@st.cache_data
def load_phonetics_data():
    file_path = 'arabic_phonetics.csv'
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return None

df_phonetics = load_phonetics_data()

def save_to_database(name, age, target, spoken, accuracy, report_text):
    db_file = 'patient_records.xlsx'
    new_entry = {
        'التاريخ': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'اسم الطفل': name,
        'العمر': age,
        'النص المستهدف': target,
        'نطق الطفل': spoken,
        'نسبة النجاح': f"{accuracy}%",
        'التشخيص': " | ".join(report_text)
    }
    
    df_new = pd.DataFrame([new_entry])
    
    try:
        # إذا كان الملف موجوداً، نحاول قراءته
        if os.path.exists(db_file):
            try:
                df_existing = pd.read_excel(db_file, engine='openpyxl')
                df_final = pd.concat([df_existing, df_new], ignore_index=True)
            except:
                # إذا فشل في القراءة (بسبب خطأ Zip file)، نبدأ ملفاً جديداً تماماً
                df_final = df_new
        else:
            df_final = df_new
        
        # حفظ الملف
        df_final.to_excel(db_file, index=False, engine='openpyxl')
        return True
    except Exception as e:
        st.error(f"فشل الحفظ: {e}")
        return False

# --- 3. محرك التشخيص الفونولوجي ---
def run_diagnosis(target, spoken):
    if df_phonetics is None: 
        return [], "", "", 0
    
    target = clean_arabic(target)
    spoken = clean_arabic(spoken)
    matcher = difflib.SequenceMatcher(None, target, spoken)
    report, t_ipa, s_ipa = [], [], []
    accuracy = round(matcher.ratio() * 100, 1)

    # تحويل النص المستهدف إلى رموز IPA
    for char in target:
        row = df_phonetics[df_phonetics['letter'] == char] if char != " " else None
        t_ipa.append(row.iloc[0]['ipa'] if row is not None and not row.empty else char)

    # تحليل الاختلافات (إبدال، حذف، إضافة)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        t_p, s_p = target[i1:i2], spoken[j1:j2]
        if tag == 'replace':
            for tc, sc in zip(t_p, s_p):
                t_row = df_phonetics[df_phonetics['letter'] == tc]
                s_row = df_phonetics[df_phonetics['letter'] == sc]
                if not t_row.empty and not s_row.empty:
                    tr, sr = t_row.iloc[0], s_row.iloc[0]
                    report.append(f"🔄 **إبدال**: ({sc}) بدلاً من ({tc})")
                    report.append(f"   - مخرج {tr['name']}: {tr['place']} ({tr['manner']})")
                    report.append(f"   - مخرج {sr['name']}: {sr['place']} ({sr['manner']})")
                    s_ipa.append(sr['ipa'])
        elif tag == 'delete':
            for char in t_p: report.append(f"❌ **حذف**: حرف ({char})")
        elif tag == 'insert':
            for char in s_p:
                report.append(f"➕ **إضافة**: حرف ({char})")
                s_row = df_phonetics[df_phonetics['letter'] == char]
                if not s_row.empty: s_ipa.append(s_row.iloc[0]['ipa'])
        elif tag == 'equal':
            for char in s_p:
                s_row = df_phonetics[df_phonetics['letter'] == char]
                s_ipa.append(s_row.iloc[0]['ipa'] if not s_row.empty else char)
                    
    return report, "".join(t_ipa), "".join(s_ipa), accuracy

# --- 4. واجهة المستخدم الرسومية ---
st.title("🔬 محلل اضطرابات النطق الفونولوجي")

if df_phonetics is not None:
    # --- القائمة الجانبية ---
    with st.sidebar:
        st.header("⚙️ الإدارة")
        if st.button("📂 عرض سجل المتابعة"):
            if os.path.exists('patient_records.xlsx'):
                try:
                    df_history = pd.read_excel('patient_records.xlsx', engine='openpyxl')
                    st.session_state['view_db'] = True
                except Exception as e:
                    st.error(f"خطأ في قراءة السجل: {e}")
            else:
                st.warning("⚠️ لا توجد سجلات بعد.")
        
        if st.button("🗑️ إخفاء السجل"):
            st.session_state['view_db'] = False

    # --- مدخلات البيانات ---
    with st.expander("👤 بيانات الطفل الأساسية", expanded=True):
        c1, c2 = st.columns(2)
        child_name = c1.text_input("اسم الطفل:")
        child_age = c2.number_input("العمر:", 2, 15, 5)
        
    target_text = st.text_input("🎯 النص المستهدف (اكتب الكلمة الصحيحة هنا):")
    
    st.divider()
    
    # --- منطقة التسجيل والتحليل ---
    st.subheader("🎤 تسجيل نطق الطفل")
    record = mic_recorder(start_prompt="إبدأ التسجيل", stop_prompt="توقف للتحليل", key='recorder')
    
    final_spoken = ""

    if record:
        st.audio(record['bytes'])
        try:
            with st.spinner("جاري التعرف على الكلام..."):
                audio_segment = AudioSegment.from_file(io.BytesIO(record['bytes']))
                wav_io = io.BytesIO()
                audio_segment.export(wav_io, format="wav", parameters=["-acodec", "pcm_s16le", "-ar", "16000"])
                wav_io.seek(0)
                
                r = sr.Recognizer()
                with sr.AudioFile(wav_io) as source:
                    audio_content = r.record(source)
                    ai_text = r.recognize_google(audio_content, language="ar-SA")
            
            st.info(f"البرنامج سمع: {ai_text}")
            final_spoken = st.text_input("تعديل النص (إذا أخطأ البرنامج في الكتابة):", ai_text)
            
        except Exception:
            st.error("لم يتم التعرف على الصوت بشكل تلقائي. يرجى كتابة ما قاله الطفل يدوياً.")
            final_spoken = st.text_input("اكتب نطق الطفل هنا:")

    # --- عرض النتائج والحفظ ---
    if final_spoken and target_text:
        res, tipa, sipa, acc = run_diagnosis(target_text, final_spoken)
        
        st.subheader("📊 نتيجة التحليل")
        st.metric("دقة النطق", f"{acc}%")
        
        col1, col2 = st.columns(2)
        col1.markdown(f"**IPA المستهدف:**\n`/{tipa}/`")
        col2.markdown(f"**IPA المنطوق:**\n`/{sipa}/`")
        
        if res:
            with st.expander("📋 تفاصيل التشخيص الفونولوجي", expanded=True):
                for line in res:
                    st.write(line)
        else:
            st.balloons()
            st.success("أحسنت! النطق مطابق تماماً للمستهدف.")

        if st.button("💾 حفظ هذه النتيجة في السجل"):
            if not child_name:
                st.warning("يرجى إدخال اسم الطفل قبل الحفظ.")
            else:
                if save_to_database(child_name, child_age, target_text, final_spoken, acc, res):
                    st.success(f"تم حفظ بيانات {child_name} بنجاح!")

    # --- عرض قاعدة البيانات إذا تم تفعيلها ---
    if st.session_state.get('view_db', False):
        st.divider()
        st.subheader("📜 سجل المتابعة المحفوظ")
        df_view = pd.read_excel('patient_records.xlsx', engine='openpyxl')
        st.dataframe(df_view, use_container_width=True)

else:
    st.error("⚠️ ملف 'arabic_phonetics.csv' غير موجود. يرجى رفعه لتفعيل محرك التشخيص.")



















