import streamlit as st
from google import genai  # ใช้ SDK ตัวใหม่ล่าสุด
import pdfplumber
import edge_tts
import asyncio
import os

# --- 1. หน้าตาแอป (Minimalist) ---
st.set_page_config(page_title="Minimalist Insight", page_icon="📖", layout="centered")

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

async def make_audio(text):
    communicate = edge_tts.Communicate(text, "th-TH-PremwadeeNeural")
    await communicate.save("podcast.mp3")

# --- 3. Sidebar (API Key & Debug) ---
with st.sidebar:
    st.markdown("### 🔑 ตั้งค่าระบบ")
    api_key = st.text_input("กรอก Gemini API Key:", type="password")
    
    if st.button("🔍 ตรวจสอบการเชื่อมต่อ"):
        if api_key:
            try:
                client = genai.Client(api_key=api_key)
                # ลองดึงชื่อโมเดลที่กุญแจนี้เห็น
                models = [m.name for m in client.models.list()]
                st.success("เชื่อมต่อสำเร็จ!")
                st.write("โมเดลที่กุญแจคุณใช้ได้:")
                st.write(models)
            except Exception as e:
                st.error(f"กุญแจมีปัญหา: {e}")
        else:
            st.warning("กรุณากรอก API Key ก่อนครับ")

# --- 4. หน้าหลัก ---
st.title("Reflective Storyteller 📖")
st.subheader("เปลี่ยนหน้ากระดาษให้เป็นเสียงนำทางใจ")

file = st.file_uploader("ลากไฟล์ PDF/TXT มาวางที่นี่", type=["pdf", "txt"])

if file and api_key:
    if st.button("เริ่มการตกผลึกความคิด ✨"):
        try:
            client = genai.Client(api_key=api_key)
            
            with st.status("🚀 กำลังดำเนินการ...", expanded=True) as status:
                st.write("📖 อ่านไฟล์...")
                raw_content = extract_text(file)
                
                st.write("🧠 AI สรุปเนื้อหา...")
                prompt = f"คุณคือ 'Niwgom Agent' สรุปเนื้อหานี้ให้เป็นพอดแคสต์ที่อบอุ่น: {raw_content[:10000]}"
                
                # เรียกใช้โมเดลผ่าน SDK ใหม่ (ระบุชื่อสั้นๆ ได้เลย)
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=prompt
                )
                script = response.text
                
                st.write("🔊 บันทึกเสียง...")
                asyncio.run(make_audio(script))
                status.update(label="เสร็จแล้ว!", state="complete")

            st.markdown(f'<div class="notebook-container"><div class="quote-text">{script}</div></div>', unsafe_allow_html=True)
            st.audio("podcast.mp3")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
elif not api_key:
    st.info("กรุณากรอก API Key ที่แถบด้านข้างเพื่อเริ่มต้นครับ")
