import streamlit as st
import google.generativeai as genai
import pdfplumber
import edge_tts
import asyncio
import os

# --- 1. ตั้งค่าหน้าตาแอป ---
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
def extract_text_from_file(uploaded_file):
    text = ""
    try:
        if uploaded_file.type == "application/pdf":
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    content = page.extract_text()
                    if content: text += content
        else:
            text = str(uploaded_file.read(), "utf-8")
    except Exception as e:
        st.error(f"อ่านไฟล์ไม่ได้: {e}")
    return text

async def text_to_speech(text, output_filename="podcast_audio.mp3"):
    communicate = edge_tts.Communicate(text, "th-TH-PremwadeeNeural")
    await communicate.save(output_filename)

# --- 3. ส่วนหลักของแอป ---
st.title("Reflective Storyteller 📖")
st.subheader("เปลี่ยนหน้ากระดาษให้เป็นเสียงนำทางใจ")

# ดึง API Key จาก Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

uploaded_file = st.file_uploader("ลากไฟล์หนังสือของคุณมาวางที่นี่ (PDF หรือ TXT)", type=["pdf", "txt"])

if uploaded_file is not None:
    if st.button("เริ่มการตกผลึกความคิด ✨"):
        if not api_key:
            st.error("❌ ไม่พบ API Key ใน Secrets")
        else:
            try:
                # ตั้งค่า Gemini
                genai.configure(api_key=api_key)
                
                with st.status("🚀 กำลังดำเนินการ...", expanded=True) as status:
                    # ขั้นตอนที่ 1: อ่านเนื้อหา
                    raw_text = extract_text_from_file(uploaded_file)
                    if not raw_text.strip():
                        st.error("ไฟล์ว่างเปล่าครับ")
                        st.stop()

                    # ขั้นตอนที่ 2: สรุปด้วย AI
                    st.write("🧠 AI กำลังกลั่นกรองหัวใจสำคัญ...")
                    prompt_text = f"คุณคือ Agent สรุปเนื้อหานี้ให้เป็นพอดแคสต์ที่อบอุ่น: {raw_text[:8000]}"
                    
                    # ลองเรียก Flash ก่อน ถ้าไม่ได้จะสลับไป Pro (แก้ปัญหา 404)
                    try:
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        response = model.generate_content(prompt_text)
                    except:
                        try:
                            model = genai.GenerativeModel('gemini-pro')
                            response = model.generate_content(prompt_text)
                        except Exception as ai_err:
                            st.error(f"AI ทำงานไม่ได้: {ai_err}")
                            st.stop()
                    
                    final_script = response.text
                    
                    # ขั้นตอนที่ 3: ทำเสียง
                    st.write("🔊 กำลังบันทึกเสียงพอดแคสต์...")
                    asyncio.run(text_to_speech(final_script))
                    status.update(label="✨ เสร็จสมบูรณ์!", state="complete")

                # แสดงผล
                st.markdown(f'<div class="notebook-container"><div class="quote-text">{final_script}</div></div>', unsafe_allow_html=True)
                st.audio("podcast_audio.mp3")
                
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดภาพรวม: {e}")

else:
    st.info("กรุณาลากไฟล์มาวางเพื่อเริ่มงานครับ")

st.markdown("---")
st.caption("“Minimalist Insight” - พัฒนาแอปโดยคุณ Jabu")
