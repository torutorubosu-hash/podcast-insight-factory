import streamlit as st
from google import genai
from google.genai import types # <--- เพิ่มการ import ตัวนี้เข้ามาครับ
import pdfplumber
import os

# --- 1. หน้าตาแอป (The Quiet Lens Style) ---
st.set_page_config(page_title="The Quiet Lens", page_icon="📖", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Sarabun', sans-serif; color: #4A4A4A; background-color: #FAFAFA; }
    .stApp { background: #FAFAFA; }
    .notebook-container { padding: 40px; background: white; border: 1px solid #E0E0E0; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-top: 20px; }
    .quote-text { font-size: 18px; font-weight: 300; line-height: 1.8; color: #333; white-space: pre-wrap; text-align: left; }
    .stButton>button { background-color: transparent; color: #4A4A4A; border: 1px solid #4A4A4A; border-radius: 20px; padding: 8px 24px; transition: all 0.3s; width: 100%; }
    .stButton>button:hover { background-color: #4A4A4A !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. ฟังก์ชันเสริม ---
def extract_text(uploaded_file):
    text = ""
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                content = page.extract_text()
                if content: text += content
    else:
        text = str(uploaded_file.read(), "utf-8")
    return text

# --- 3. Sidebar ---
with st.sidebar:
    st.markdown("### 🔑 ตั้งค่าระบบ")
    api_key = st.text_input("กรอก Gemini API Key:", type="password")
    
# --- 4. หน้าหลัก ---
st.title("The Quiet Lens 📖")
st.subheader("เลนส์ที่เงียบสงบ ที่จะช่วยให้คุณมองโลกอย่างลึกซึ้ง")

uploaded_file = st.file_uploader("ลากไฟล์ PDF/TXT มาวางที่นี่", type=["pdf", "txt"])

if uploaded_file and api_key:
    if st.button("เริ่มการตกผลึกความคิด ✨"):
        try:
            client = genai.Client(api_key=api_key)
            
            with st.status("🚀 กำลังกลั่นกรองเสียงแห่งปัญญา...", expanded=True) as status:
                st.write("📖 อ่านเนื้อหา...")
                raw_text = extract_text(uploaded_file)
                
                st.write("🧠 The Quiet Lens กำลังวิเคราะห์...")
                prompt = f"""
                คุณคือ 'The Quiet Lens' นักเล่าเรื่องที่นุ่มนวล
                สรุปเนื้อหานี้ให้เป็นบทพอดแคสต์ที่อบอุ่นและลึกซึ้ง 1-2 นาที
                เน้นการตั้งคำถามให้คนฟังได้คิดตาม และใช้ภาษาไทยที่สวยงาม
                เนื้อหา: {raw_text[:12000]}
                """
                
                # --- แก้ไขโครงสร้าง Config ตรงนี้ครับ ---
                response = client.models.generate_content(
                    model='gemini-2.5-flash-native-audio-latest',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        speech_config=types.SpeechConfig(
                            voice_config=types.VoiceConfig(
                                predefined_voice=types.PredefinedVoiceConfig(
                                    voice_name='Puck' # หรือ 'Aoede' สำหรับเสียงผู้หญิงที่นุ่มนวล
                                )
                            )
                        )
                    )
                )
                
                final_script = response.text
                
                st.write("🔊 กำลังบันทึกพอดแคสต์...")
                with open("quiet_lens.mp3", "wb") as f:
                    f.write(response.audio_bytes)
                    
                status.update(label="ตกผลึกเรียบร้อย!", state="complete")

            # แสดงผล
            st.markdown(f'<div class="notebook-container"><div class="quote-text">{final_script}</div></div>', unsafe_allow_html=True)
            st.audio("quiet_lens.mp3")
            
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")

elif not api_key:
    st.info("กรุณากรอก API Key เพื่อเริ่มต้นการเดินทางครับ")
