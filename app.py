import streamlit as st
import google.generativeai as genai
import pdfplumber
import edge_tts
import asyncio
import os

# --- 1. ตั้งค่าหน้าตาแอป (Minimalist Notebook Style) ---
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

# --- 2. ฟังก์ชันเสริม (Helpers) ---

def extract_text_from_file(uploaded_file):
    """ดึงข้อความจากไฟล์ PDF หรือ TXT"""
    text = ""
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                content = page.extract_text()
                if content:
                    text += content
    else:
        text = str(uploaded_file.read(), "utf-8")
    return text

async def text_to_speech(text, output_filename="podcast_audio.mp3"):
    """แปลงข้อความเป็นเสียงพอดแคสต์"""
    communicate = edge_tts.Communicate(text, "th-TH-PremwadeeNeural")
    await communicate.save(output_filename)

# --- 3. ส่วนหลักของแอป ---

st.title("Reflective Storyteller 📖")
st.subheader("เปลี่ยนหน้ากระดาษให้เป็นเสียงนำทางใจ")

# ดึง API Key จาก Streamlit Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

# ช่องอัปโหลดไฟล์
uploaded_file = st.file_uploader("ลากไฟล์หนังสือของคุณมาวางที่นี่ (PDF หรือ TXT)", type=["pdf", "txt"])

if uploaded_file is not None:
    st.info(f"📁 รับไฟล์: {uploaded_file.name} เรียบร้อยแล้ว")
    
    if st.button("เริ่มการตกผลึกความคิด ✨"):
        if not api_key:
            st.error("❌ ไม่พบ API Key! กรุณาไปที่ Settings > Secrets แล้วใส่ GEMINI_API_KEY ก่อนครับ")
        else:
            try:
                # ตั้งค่า Gemini
                genai.configure(api_key=api_key)
                
                with st.status("🚀 กำลังสร้างพอดแคสต์...", expanded=True) as status:
                    # ขั้นตอนที่ 1: อ่านเนื้อหา
                    st.write("📖 กำลังอ่านเนื้อหาจากไฟล์...")
                    raw_text = extract_text_from_file(uploaded_file)
                    
                    if not raw_text.strip():
                        st.error("ไม่สามารถอ่านข้อความจากไฟล์ได้ กรุณาลองไฟล์อื่นครับ")
                        st.stop()

                    # ขั้นตอนที่ 2: สรุปด้วย AI (นิยาม prompt ไว้ตรงนี้เลย)
                    st.write("🧠 AI กำลังกลั่นกรองหัวใจสำคัญ...")
                    prompt_text = f"""
                    คุณคือนักเล่าเรื่องที่อบอุ่นและช่างสังเกต
                    จงสรุปเนื้อหาที่ได้รับ ให้เป็นบทพอดแคสต์ที่มีรายละเอียดและการยกตัวอย่างให้เชื่อมโยงกับชีวิตจริง
                    โทน: นุ่มนวล, ให้กำลังใจ, มีความหวัง, เชื่อมโยงเรื่องราวเข้ากับชีวิตจริง
                    เนื้อหา: {raw_text[:10000]}
                    (สรุปเป็นภาษาไทยที่ไพเราะ เริ่มต้นด้วยการทักทายที่ทำให้คนฟังรู้สึกสบายใจ)
                    """
                    
                
try:
    # 1. นิยาม prompt
    prompt_text = f"คุณคือAgentสรุปเนื้อหานี้ให้เป็นพอดแคสต์ที่อบอุ่น: {raw_text[:8000]}"
    
    # 2. เรียกใช้โมเดล (ลองใส่ 'models/' นำหน้าชื่อ)
    # เราจะลองเรียก Flash ก่อน ถ้าไม่ได้ค่อยถอยไป Pro
    try:
        model = genai.GenerativeModel(model_name='models/gemini-1.5-flash') # <--- ใส่ models/ นำหน้า
        response = model.generate_content(prompt_text)
    except:
        model = genai.GenerativeModel(model_name='models/gemini-pro') # <--- ใส่ models/ นำหน้า
        response = model.generate_content(prompt_text)
        
    final_script = response.text
                    
                    # ขั้นตอนที่ 3: ทำเสียง
                    st.write("🔊 กำลังบันทึกเสียงพอดแคสต์...")
                    asyncio.run(text_to_speech(final_script))
                    
                    status.update(label="✨ ตกผลึกเสร็จสิ้น!", state="complete")

                # --- การแสดงผลผลลัพธ์ ---
                st.markdown(f"""
                <div class="notebook-container">
                    <div class="quote-text">{final_script}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.audio("podcast_audio.mp3")
                st.download_button(
                    label="💾 ดาวน์โหลดเสียงพอดแคสต์",
                    data=open("podcast_audio.mp3", "rb"),
                    file_name=f"Insight_{uploaded_file.name.split('.')[0]}.mp3",
                    mime="audio/mp3"
                )

            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")

else:
    st.markdown("""
    <div style='text-align: center; padding: 100px 20px; color: #BBB; border: 1px dashed #DDD; border-radius: 20px;'>
        <p style='font-size: 18px;'>เริ่มต้นความละเมียดละไม</p>
        <p style='font-size: 14px;'>โดยการลากไฟล์ที่ต้องการสรุปมาวางด้านบนครับ</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("“Minimalist Insight” - พัฒนาแอปโดยคุณ Jabu")
