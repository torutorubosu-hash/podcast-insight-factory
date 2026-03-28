import streamlit as st
import os
import asyncio
import edge_tts
import google.generativeai as genai
import pdfplumber
import io

# --- 1. การตั้งค่าหน้าตา (Minimalist Notebook Style) ---
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
    /* ปรับแต่งช่อง Upload */
    .stFileUploader section { background-color: white; border: 1px dashed #4A4A4A; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 2. ฟังก์ชัน Backend ---

def extract_text(uploaded_file):
    """ดึงข้อความจากไฟล์ PDF หรือ TXT"""
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            text = "".join(page.extract_text() for page in pdf.pages if page.extract_text())
        return text
    else:
        return str(uploaded_file.read(), "utf-8")

async def generate_voice(text, output_file="output.mp3"):
    """สร้างเสียงพอดแคสต์ที่นุ่มนวล (Edge-TTS)"""
    communicate = edge_tts.Communicate(text, "th-TH-PremwadeeNeural")
    await communicate.save(output_file)

# --- 3. Sidebar: Settings ---

with st.sidebar:
    st.markdown("### ⚙️ ตั้งค่าระบบ")
    api_key = st.text_input("Gemini API Key", type="password", help="รับได้ที่ Google AI Studio")
    if api_key:
        genai.configure(api_key=api_key)
    st.divider()
    st.caption("แนะนำให้ใช้ไฟล์ PDF หรือ TXT ที่มีเนื้อหาไม่เกิน 50 หน้าเพื่อให้ AI ทำงานได้ดีที่สุดครับ")

# --- 4. Main Stage (หน้าหลัก) ---

st.title("Reflective Storyteller 📖")
st.subheader("เปลี่ยนหน้ากระดาษให้เป็นเสียงนำทางใจ")

# ช่องลากวางไฟล์
uploaded_file = st.file_uploader("ลากไฟล์หนังสือของคุณมาวางที่นี่ (PDF หรือ TXT)", type=["pdf", "txt"])

if uploaded_file is not None:
    st.success(f"เตรียมไฟล์ '{uploaded_file.name}' เรียบร้อยแล้ว")

    if st.button("เริ่มการตกผลึกความคิด ✨"):
        if not api_key:
            st.error("กรุณาใส่ Gemini API Key ที่แถบด้านข้างก่อนนะครับ")
        else:
            with st.status("กำลังเปลี่ยนตัวอักษรเป็นความรู้สึก...", expanded=True) as status:
                # 1. อ่านไฟล์
                st.write("📖 กำลังอ่านเนื้อหา...")
                raw_text = extract_text(uploaded_file)

                # 2. AI สรุป (สไตล์นิ้วกลม)
                st.write("🧠 AI กำลังกลั่นกรองหัวใจสำคัญ...")
                from google import genai

                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=prompt
                )
                script = response.text

                # 3. ทำเสียง
                st.write("🔊 กำลังบันทึกเสียงพอดแคสต์...")
                asyncio.run(generate_voice(script))

                status.update(label="ตกผลึกเสร็จสิ้น!", state="complete")

            # แสดงผลในรูปแบบสมุดบันทึก
            st.markdown(f"""
            <div class="notebook-container">
                <div class="quote-text">{script}</div>
            </div>
            """, unsafe_allow_html=True)

            st.audio("output.mp3")
            st.download_button(
                label="💾 ดาวน์โหลดพอดแคสต์ไว้ฟังทีหลัง",
                data=open("output.mp3", "rb"),
                file_name=f"Podcast_{uploaded_file.name.split('.')[0]}.mp3",
                mime="audio/mp3"
            )
else:
    # หน้าว่างๆ เมื่อยังไม่มีไฟล์
    st.markdown("""
    <div style='text-align: center; padding: 100px 20px; color: #BBB; border: 1px dashed #DDD; border-radius: 20px;'>
        <p style='font-size: 18px;'>เริ่มต้นความละเมียดละไม</p>
        <p style='font-size: 14px;'>โดยการลากไฟล์ที่ต้องการสรุปมาวางด้านบนครับ</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("“Minimalist Insight” - เพราะทุกบรรทัดมีความหมาย")