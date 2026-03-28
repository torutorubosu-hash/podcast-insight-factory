import streamlit as st
from google import genai
import pdfplumber
import edge_tts
import asyncio
import os

# --- 1. ตั้งค่าหน้าตาแอป (Adaptive Minimalist) ---
st.set_page_config(page_title="The Quiet Lens", page_icon="📖", layout="centered")

# CSS ที่ดึงค่าจาก Theme ของเครื่องผู้ใช้ (รองรับ Dark/Light Mode)
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
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    .quote-text {
        font-size: 18px;
        font-weight: 300;
        line-height: 1.8;
        color: var(--text-color);
        white-space: pre-wrap;
    }
    .stButton>button {
        border-radius: 25px;
        padding: 10px 20px;
        border: 1px solid var(--primary-color);
        background-color: transparent;
        color: var(--text-color);
        width: 100%;
        transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stButton>button:hover {
        background-color: var(--primary-color) !important;
        color: white !important;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. ฟังก์ชันเสริม ---
def extract_text(uploaded_file):
    text = ""
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            text = "".join(page.extract_text() for page in pdf.pages if page.extract_text())
    else:
        text = str(uploaded_file.read(), "utf-8")
    return text

async def text_to_speech(text):
    # ใช้เสียง Niwat ที่นุ่มนวลและเป็นธรรมชาติที่สุดสำหรับภาษาไทย
    communicate = edge_tts.Communicate(text, "th-TH-NiwatNeural")
    await communicate.save("podcast.mp3")

# --- 3. ระบบ Smart Model Selector ---
def get_best_model(client):
    """ฟังก์ชันเลือกโมเดลที่ดีที่สุดจากสิทธิ์ที่ API Key มี"""
    # ลำดับความเก่งที่เราอยากได้ (จากมากไปน้อย)
    priority_list = [
        'models/gemini-2.5-flash',
        'models/gemini-2.0-flash',
        'models/gemini-1.5-flash',
        'models/gemini-pro'
    ]
    try:
        available_models = [m.name for m in client.models.list()]
        # เลือกตัวแรกที่เจอใน priority_list และมีอยู่ในเครื่องจริง
        for model_name in priority_list:
            if model_name in available_models:
                return model_name
    except:
        pass
    return 'models/gemini-2.0-flash' # ค่าเริ่มต้นกรณีเช็คไม่ได้

# --- 4. Sidebar & หน้าหลัก ---
with st.sidebar:
    st.title("⚙️ System Configuration")
    api_key = st.text_input("กรอก Gemini API Key:", type="password")
    st.divider()
    st.caption("แอปจะเลือกโมเดลที่ดีที่สุดให้คุณอัตโนมัติ")

st.title("The Quiet Lens 📖")
st.subheader("เลนส์ที่เงียบสงบ ที่จะช่วยให้คุณมองโลกอย่างลึกซึ้ง")

file = st.file_uploader("ลากไฟล์ PDF หรือ TXT ของคุณมาวางที่นี่", type=["pdf", "txt"])

if file and api_key:
    if st.button("เริ่มการตกผลึกความคิด ✨"):
        try:
            client = genai.Client(api_key=api_key)
            
            with st.status("🚀 กำลังคัดสรรเทคโนโลยีที่ดีที่สุด...", expanded=True) as status:
                # 1. เลือกโมเดลที่ใช้งานได้จริง
                best_model = get_best_model(client)
                st.write(f"✅ เลือกใช้โมเดล: `{best_model}`")
                
                # 2. อ่านไฟล์
                raw_text = extract_text(file)
                
                # 3. สั่ง AI สรุปเนื้อหา
                st.write("🧠 The Quiet Lens กำลังตกผลึกเนื้อหา...")
                prompt = f"""
                คุณคือ 'The Quiet Lens' นักจัดพอดแคสต์ที่นุ่มนวลและสุขุม
                จงสรุปเนื้อหาที่ได้รับ ให้เป็นบทพอดแคสต์ที่อบอุ่นและลึกซึ้ง 1-2 นาที
                เน้นการเล่าเรื่องที่ทำให้คนฟังรู้สึกสงบและได้แง่คิดลึกซึ้ง
                เนื้อหา: {raw_text[:12000]}
                (สรุปเป็นภาษาไทยที่ไพเราะ เริ่มต้นด้วยการทักทายที่อบอุ่น)
                """
                
                response = client.models.generate_content(
                    model=best_model.replace("models/", ""), # ตัด models/ ออกถ้าใช้ SDK ใหม่
                    contents=prompt
                )
                final_script = response.text
                
                # 4. สร้างเสียงพอดแคสต์
                st.write("🔊 กำลังบันทึกเสียงแห่งความเงียบสงบ...")
                asyncio.run(text_to_speech(final_script))
                
                status.update(label="การตกผลึกเสร็จสมบูรณ์!", state="complete")

            # --- ผลลัพธ์ ---
            st.markdown(f'<div class="notebook-container"><div class="quote-text">{final_script}</div></div>', unsafe_allow_html=True)
            st.audio("podcast.mp3")
            st.download_button("💾 เก็บพอดแคสต์นี้ไว้ฟัง", open("podcast.mp3", "rb"), file_name="the_quiet_lens.mp3")

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")

elif not api_key:
    st.info("💡 กรุณากรอก API Key ที่แถบด้านข้างเพื่อเปิดใช้งานเลนส์แห่งปัญญาครับ")

st.divider()
st.caption("The Quiet Lens | Adaptive & Smart Podcast Generator")
