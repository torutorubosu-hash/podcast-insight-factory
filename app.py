import streamlit as st
import google.generativeai as genai
import pdfplumber
import edge_tts
import asyncio
import os

# --- 1. หน้าตาแอป (Adaptive Minimalist) ---
st.set_page_config(page_title="The Quiet Lens", page_icon="📖", layout="centered")

# CSS ที่รองรับทั้ง Dark และ Light Theme อัตโนมัติ
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Sarabun', sans-serif; }
    
    .notebook-container {
        padding: 30px;
        background-color: var(--secondary-background-color);
        border: 1px solid var(--divider-color);
        border-radius: 12px;
        margin-top: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .quote-text {
        font-size: 18px;
        font-weight: 300;
        line-height: 1.8;
        color: var(--text-color);
        white-space: pre-wrap;
    }
    .stButton>button {
        border-radius: 20px;
        border: 1px solid var(--primary-color);
        background-color: transparent;
        color: var(--text-color);
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: var(--primary-color) !important;
        color: white !important;
    }
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

async def text_to_speech(text):
    # ใช้เสียงคุณ Niwat ซึ่งนุ่มนวลและเป็นธรรมชาติมากสำหรับพอดแคสต์ไทย
    communicate = edge_tts.Communicate(text, "th-TH-NiwatNeural")
    await communicate.save("podcast.mp3")

# --- 3. ส่วนตั้งค่าด้านข้าง (Sidebar) ---
with st.sidebar:
    st.title("⚙️ การตั้งค่า")
    api_key = st.text_input("กรอก Gemini API Key:", type="password")
    st.info("💡 ใช้โมเดล: gemini-2.0-flash (เสถียรที่สุด)")

# --- 4. หน้าหลัก ---
st.title("The Quiet Lens 📖")
st.subheader("เลนส์ที่เงียบสงบ ที่จะช่วยให้คุณมองโลกอย่างลึกซึ้ง")

file = st.file_uploader("ลากไฟล์ PDF หรือ TXT มาวางที่นี่", type=["pdf", "txt"])

if file and api_key:
    if st.button("เริ่มการตกผลึกความคิด ✨"):
        try:
            # ตั้งค่า API
            genai.configure(api_key=api_key)
            
            with st.status("🚀 กำลังเดินทางเข้าสู่โลกแห่งปัญญา...", expanded=True) as status:
                # 1. อ่านไฟล์
                st.write("📖 อ่านเนื้อหาจากหน้ากระดาษ...")
                raw_text = extract_text(file)
                
                # 2. สรุปด้วย AI (ใช้รุ่น 2.0-flash ที่อยู่ในลิสต์ของคุณและเสถียรกว่า)
                st.write("🧠 The Quiet Lens กำลังตกผลึกความคิด...")
                prompt = f"""
                คุณคือ 'The Quiet Lens' นักจัดพอดแคสต์ที่นุ่มนวลและช่างสังเกต
                จงสรุปเนื้อหาที่ได้รับ ให้เป็นบทพอดแคสต์ที่อบอุ่นและลึกซึ้ง มีรายละเอียดและการยกตัวอย่างให้เข้ากับชีวิตยุคใหม่
                เน้นการเล่าเรื่องที่ทำให้คนฟังรู้สึกสงบและได้แง่คิดในการใช้ชีวิต
                เนื้อหา: {raw_text[:10000]}
                (สรุปเป็นภาษาไทยที่ไพเราะ เริ่มต้นด้วยการทักทายที่อบอุ่น)
                """
                
                model = genai.GenerativeModel('gemini-2.0-flash')
                response = model.generate_content(prompt)
                final_script = response.text
                
                # 3. สร้างเสียง (ใช้ edge-tts ที่เสถียรกว่าในตอนนี้)
                st.write("🔊 กำลังบันทึกเสียงพอดแคสต์...")
                asyncio.run(text_to_speech(final_script))
                
                status.update(label="การตกผลึกเสร็จสิ้น!", state="complete")

            # --- แสดงผลลัพธ์ ---
            st.markdown(f'<div class="notebook-container"><div class="quote-text">{final_script}</div></div>', unsafe_allow_html=True)
            st.audio("podcast.mp3")
            st.download_button("💾 ดาวน์โหลดพอดแคสต์", open("podcast.mp3", "rb"), file_name="quiet_lens.mp3")

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")

elif not api_key:
    st.warning("⚠️ กรุณากรอก API Key ที่แถบด้านข้างก่อนเริ่มต้นครับ")

st.divider()
st.caption("The Quiet Lens | พัฒนาโดยคุณ Jabu")
