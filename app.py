import streamlit as st
import os
import asyncio
import edge_tts
from google import genai  # ใช้ Library ตัวใหม่ตามคำแนะนำของ Google
import pdfplumber
import io

# --- 1. การตั้งค่าหน้าตา (Minimalist Style) ---
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

# --- 2. ฟังก์ชัน Backend ---
def extract_text(uploaded_file):
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            text = "".join(page.extract_text() for page in pdf.pages if page.extract_text())
        return text
    return str(uploaded_file.read(), "utf-8")

async def generate_voice(text, output_file="output.mp3"):
    communicate = edge_tts.Communicate(text, "th-TH-PremwadeeNeural")
    await communicate.save(output_file)

# --- 3. ดึง API Key จาก Secrets ---
# ใน Streamlit Cloud เราจะดึงกุญแจจากระบบความลับของเขาครับ
api_key = st.secrets.get("GEMINI_API_KEY")

# --- 4. Main Stage ---
st.title("Reflective Storyteller 📖")
st.subheader("เปลี่ยนหน้ากระดาษให้เป็นเสียงนำทางใจ")

uploaded_file = st.file_uploader("ลากไฟล์หนังสือของคุณมาวางที่นี่ (PDF หรือ TXT)", type=["pdf", "txt"])

if uploaded_file is not None:
    if st.button("เริ่มการตกผลึกความคิด ✨"):
        if not api_key:
            st.error("ไม่พบ API Key ในระบบ Secrets! กรุณาตั้งค่าที่ Settings -> Secrets")
        else:
            try:
                with st.status("กำลังเปลี่ยนตัวอักษรเป็นความรู้สึก...", expanded=True) as status:
                    # 1. อ่านไฟล์
                    st.write("📖 กำลังอ่านเนื้อหา...")
                    raw_text = extract_text(uploaded_file)
                    
                    # 2. AI สรุป (นิยาม prompt ให้ชัดเจนก่อนเรียกใช้)
                    st.write("🧠 AI กำลังกลั่นกรองหัวใจสำคัญ...")
                    prompt = f"คุณคือ 'Niwgom Agent' จงสรุปเนื้อหานี้ให้เป็นพอดแคสต์ที่อบอุ่น: {raw_text[:8000]}"
                    
                    client = genai.Client(api_key=api_key)
                    response = client.models.generate_content(
                        model='gemini-1.5-flash',
                        contents=prompt
                    )
                    script = response.text
                    
                    # 3. ทำเสียง
                    st.write("🔊 กำลังบันทึกเสียงพอดแคสต์...")
                    asyncio.run(generate_voice(script))
                    status.update(label="เสร็จสมบูรณ์!", state="complete")

                st.markdown(f'<div class="notebook-container"><div class="quote-text">{script}</div></div>', unsafe_allow_html=True)
                st.audio("output.mp3")
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")
