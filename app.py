import streamlit as st
from google import genai
import pdfplumber
import os

# --- 1. หน้าตาแอป (Adaptive Minimalist Notebook) ---
st.set_page_config(page_title="The Quiet Lens", page_icon="📖", layout="centered")

# ใช้ CSS Variables เพื่อรองรับทั้ง Dark และ Light Mode
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Sarabun', sans-serif;
    }

    /* Container สไตล์สมุดโน้ตที่เปลี่ยนสีตาม Theme */
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
        text-align: left;
    }

    /* ปรับแต่งปุ่มให้ดู Minimal */
    .stButton>button {
        border-radius: 20px;
        padding: 10px 25px;
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

# --- 2. ฟังก์ชันดึงข้อความ ---
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

# --- 3. แถบด้านข้าง (Sidebar) ---
with st.sidebar:
    st.title("⚙️ Setting")
    api_key = st.text_input("Gemini API Key:", type="password")
    st.caption("รับกุญแจที่: aistudio.google.com")
    
    st.divider()
    voice_choice = st.selectbox("เลือกเสียงพอดแคสต์:", ["Aoede (นุ่มนวล/หญิง)", "Puck (สุขุม/ชาย)"])
    voice_name = "Aoede" if "Aoede" in voice_choice else "Puck"

# --- 4. หน้าหลัก (The Quiet Lens) ---
st.title("The Quiet Lens 📖")
st.subheader("เลนส์ที่เงียบสงบ ที่จะช่วยให้คุณมองโลกอย่างลึกซึ้ง")

file = st.file_uploader("ลากไฟล์ PDF หรือ TXT มาวางตรงนี้", type=["pdf", "txt"])

if file and api_key:
    if st.button("เริ่มการตกผลึกความคิด ✨"):
        try:
            client = genai.Client(api_key=api_key)
            
            with st.status("🚀 กำลังกลั่นกรองเสียงแห่งปัญญา...", expanded=True) as status:
                # 1. อ่านไฟล์
                raw_text = extract_text(file)
                
                # 2. ส่งให้ AI สรุปและสร้างเสียง (Native Audio)
                st.write("🧠 The Quiet Lens กำลังวิเคราะห์เนื้อหา...")
                prompt = f"""
                คุณคือ 'The Quiet Lens' นักจัดพอดแคสต์ที่นุ่มนวลและสุขุม
                สรุปเนื้อหานี้ให้เป็นบทพอดแคสต์ที่อบอุ่นและลึกซึ้ง มีรายละเอียดและการยกตัวอย่างให้เข้ากับชีวิตจริงของคนยุคปัจจุบัน
                เน้นการเล่าเรื่องที่ทำให้คนฟังรู้สึกสงบและได้แง่คิดในการใช้ชีวิต
                เนื้อหา: {raw_text[:12000]}
                (สรุปเป็นภาษาไทยที่ไพเราะ และเว้นจังหวะการเล่าให้ดูใจเย็น)
                """
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash-native-audio-latest',
                    contents=prompt,
                    config={
                        "speech_config": voice_name  # ใช้ชื่อเสียงตรงๆ ตาม SDK ล่าสุด
                    }
                )
                
                # 3. บันทึกเสียง
                st.write("🔊 กำลังบันทึกพอดแคสต์...")
                with open("podcast.mp3", "wb") as f:
                    f.write(response.audio_bytes)
                
                status.update(label="ตกผลึกเรียบร้อย!", state="complete")

            # --- แสดงผลลัพธ์ ---
            st.markdown(f"""
            <div class="notebook-container">
                <div class="quote-text">{response.text}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.audio("podcast.mp3")
            st.download_button("💾 ดาวน์โหลดพอดแคสต์ (MP3)", open("podcast.mp3", "rb"), file_name="quiet_lens_podcast.mp3")

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
            if "404" in str(e):
                st.info("แนะนำ: ลองตรวจสอบชื่อโมเดลใน Sidebar หรือสร้าง API Key ใหม่ครับ")

elif not api_key:
    st.info("💡 กรุณากรอก API Key ที่แถบด้านข้างเพื่อเริ่มต้นครับ")
else:
    st.markdown("""
    <div style='text-align: center; padding: 50px; opacity: 0.5;'>
        <p>รอรับฟังเสียงแห่งการตกผลึกจากไฟล์ของคุณ...</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()
st.caption("The Quiet Lens Project | Powered by Gemini 2.5 Native Audio")
