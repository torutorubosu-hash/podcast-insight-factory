import streamlit as st
from google import genai
import pdfplumber
import os

# --- 1. หน้าตาแอป (Minimalist Notebook) ---
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

# --- 3. Sidebar (API Key & Debug) ---
with st.sidebar:
    st.markdown("### 🔑 ตั้งค่าระบบ")
    # ช่องกรอก Key
    api_key = st.text_input("กรอก Gemini API Key:", type="password")
    
    # ดึงรายชื่อโมเดลมาโชว์เพื่อความมั่นใจ
    if st.button("🔍 ตรวจสอบโมเดล"):
        if api_key:
            try:
                client = genai.Client(api_key=api_key)
                models = [m.name for m in client.models.list()]
                st.success("เชื่อมต่อสำเร็จ!")
                st.write("โมเดลที่คุณใช้ได้:")
                # แสดงแค่โมเดลที่เราจะใช้เพื่อความง่าย
                st.write([m for m in models if "native-audio" in m or "gemini-2.5-flash" == m.replace("models/","")])
            except Exception as e:
                st.error(f"กุญแจมีปัญหา: {e}")
        else:
            st.warning("กรุณากรอก API Key ก่อนครับ")

# --- 4. หน้าหลัก (Main Stage) ---
st.title("The Quiet Lens 📖")
st.subheader("เลนส์ที่เงียบสงบ ที่จะช่วยให้คุณมองโลกอย่างลึกซึ้ง")

uploaded_file = st.file_uploader("ลากไฟล์ PDF/TXT ที่ต้องการสรุปมาวางที่นี่", type=["pdf", "txt"])

if uploaded_file and api_key:
    if st.button("เริ่มการตกผลึกความคิด ✨"):
        try:
            client = genai.Client(api_key=api_key)
            
            with st.status("🚀 กำลังทำงาน...", expanded=True) as status:
                st.write("📖 อ่านเนื้อหา...")
                raw_text = extract_text(uploaded_file)
                
                st.write("🧠 AI สรุปและสร้างเสียงพอดแคสต์...")
                # นิยาม Persona และคำสั่งใหม่ให้เข้ากับชื่อแอป
                prompt = f"""
                คุณคือ 'The Quiet Lens' นักจัดพอดแคสต์ที่นุ่มนวลและช่างสังเกต
                จงสรุปเนื้อหาที่ได้รับ ให้เป็นบทพอดแคสต์ที่มีรายละเอียด อาจยกตัวอย่างให้เข้ากับชีวิตจริงของคนในยุคปัจจุบัน
                โทน: เงียบสงบ, นุ่มนวล, ให้กำลังใจ, เชื่อมโยงเรื่องราวเข้ากับชีวิตจริงอย่างลึกซึ้ง
                เนื้อหา: {raw_text[:12000]}
                (สรุปเป็นภาษาไทยที่ไพเราะ เริ่มต้นด้วยการทักทายที่ทำให้คนฟังรู้สึกสบายใจ)
                """
                
                # เรียกโมเดล Gemini Native Audio (โมเดลจะสังเคราะห์เสียงออกมาเองโดยตรง)
                response = client.models.generate_content(
                    model='gemini-2.5-flash-native-audio-latest', # ใช้ตัวที่อยู่ในลิสต์ของคุณ
                    contents=prompt,
                    config={
                        "speech_config": {
                            # ลองชื่อเสียง Aoede (ผู้หญิง) หรือ Puck (ผู้ชาย) ดูนะครับ
                            "voice_config": {"predefined_voice": "Puck"}
                        }
                    }
                )
                
                final_script = response.text
                
                st.write("🔊 กำลังบันทึกไฟล์เสียง...")
                # บันทึกเสียงที่ได้จาก AI โดยตรงเป็นไฟล์ mp3
                with open("quiet_lens_podcast.mp3", "wb") as f:
                    f.write(response.audio_bytes)
                    
                status.update(label="ตกผลึกเสร็จสมบูรณ์!", state="complete")

            # --- การแสดงผลผลลัพธ์ ---
            st.markdown(f'<div class="notebook-container"><div class="quote-text">{final_script}</div></div>', unsafe_allow_html=True)
            
            # เล่นเสียงที่ AI สร้างออกมาเองโดยตรง (จะมีความธรรมชาติสูงมาก)
            st.audio("quiet_lens_podcast.mp3")
            
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
            if "404" in str(e):
                st.warning("ดูเหมือน API Key ของคุณยังไม่ได้รับสิทธิ์ให้ใช้โมเดล Native Audio ในโปรเจกต์นี้ครับ ลองสร้าง API Key ใหม่ในโปรเจกต์ใหม่ดูนะครับ")

elif not api_key:
    st.info("เริ่มต้นโดยการกรอก API Key ที่แถบด้านข้างเพื่อเปิดใช้งานระบบครับ")
