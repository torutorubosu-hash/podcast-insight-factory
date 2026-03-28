import streamlit as st
from google import genai
from google.cloud import texttospeech
from google.oauth2 import service_account
import pdfplumber
import os

# --- 1. หน้าตาแอป (Adaptive Minimalist) ---
st.set_page_config(page_title="The Quiet Lens Pro", page_icon="🎙️", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Sarabun', sans-serif; }
    
    .notebook-container {
        padding: 30px;
        background-color: var(--secondary-background-color);
        border: 1px solid var(--divider-color);
        border-radius: 15px;
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
        border: 1px solid var(--primary-color);
        background-color: transparent;
        color: var(--text-color);
        width: 100%;
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        background-color: var(--primary-color) !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. ฟังก์ชันหัวใจหลัก ---

def extract_text(uploaded_file):
    """อ่านข้อความจาก PDF หรือ TXT"""
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            return "".join(page.extract_text() for page in pdf.pages if page.extract_text())
    return str(uploaded_file.read(), "utf-8")

def generate_pro_audio(text, voice_name="th-TH-Neural2-A"):
    """สร้างเสียงคุณภาพสูงจาก Google Cloud TTS"""
    try:
        # ดึง Credentials จาก Secrets
        info = dict(st.secrets["gcp_service_account"])
        credentials = service_account.Credentials.from_service_account_info(info)
        
        client = texttospeech.TextToSpeechClient(credentials=credentials)
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # ตั้งค่าเสียง Neural2 (A-หญิงนุ่มนวล, C-ชายสุขุม)
        voice = texttospeech.VoiceSelectionParams(
            language_code="th-TH",
            name=voice_name
        )
        
        # ปรับความเร็วให้ช้าลงเพื่อความละเมียดละไม
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.92, 
            pitch=-1.2
        )
        
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        
        audio_file = "quiet_lens_podcast.mp3"
        with open(audio_file, "wb") as out:
            out.write(response.audio_content)
        return audio_file
    except Exception as e:
        st.error(f"TTS Error: {e}")
        return None

# --- 3. ส่วนควบคุมระบบ (Sidebar & State) ---

if 'script' not in st.session_state:
    st.session_state.script = ""

with st.sidebar:
    st.title("⚙️ Pro Settings")
    gemini_key = st.text_input("Gemini API Key:", type="password")
    voice_option = st.selectbox("เลือกเสียงนักเล่าเรื่อง:", ["Neural2-A (หญิง/นุ่มนวล)", "Neural2-C (ชาย/สุขุม)"])
    selected_voice = "th-TH-Neural2-A" if "A" in voice_option else "th-TH-Neural2-C"
    st.divider()
    st.caption("Status: Google Cloud TTS Connected ✅")

# --- 4. หน้าหลัก (Main Interface) ---

st.title("The Quiet Lens Pro 📖")
st.subheader("เปลี่ยนตัวอักษรให้เป็นเสียงแห่งปัญญา")

file = st.file_uploader("ลากไฟล์ที่ต้องการตกผลึกมาวางที่นี่", type=["pdf", "txt"])

if file and gemini_key:
    # STEP 1: AI สร้างบทสรุป
    if st.button("🧠 1. ตกผลึกเนื้อหาด้วย Gemini"):
        try:
            client = genai.Client(api_key=gemini_key)
            raw_content = extract_text(file)
            
            prompt = f"""
            คุณคือ 'The Quiet Lens' นักจัดพอดแคสต์ที่นุ่มนวลและสุขุม 
            จงสรุปเนื้อหานี้ให้เป็นพอดแคสต์ที่อบอุ่น ลึกซึ้ง และมีพลัง 1-2 นาที
            ใช้ภาษาพูดที่ไพเราะ มีการเว้นจังหวะเหมือนเล่าเรื่องให้เพื่อนฟัง
            เนื้อหา: {raw_content[:10000]}
            """
            
            response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
            st.session_state.script = response.text
            st.success("AI สรุปบทให้เรียบร้อยแล้ว!")
        except Exception as e:
            st.error(f"Gemini Error: {e}")

    # STEP 2: แสดงบทให้แก้ไขได้
    if st.session_state.script:
        st.markdown("### ✍️ เกลาบทพอดแคสต์")
        st.session_state.script = st.text_area(
            "คุณสามารถปรับแต่งคำพูดได้ตรงนี้ก่อนลงเสียงจริง:", 
            value=st.session_state.script, 
            height=300
        )
        
        st.divider()

        # STEP 3: ลงเสียงด้วย Google Cloud
        if st.button("🔊 2. บันทึกเสียงระดับ Studio (Neural2)"):
            with st.spinner("กำลังสังเคราะห์เสียงด้วยเทคโนโลยี Neural2..."):
                audio_path = generate_pro_audio(st.session_state.script, selected_voice)
                if audio_path:
                    st.audio(audio_path)
                    st.success("สร้างพอดแคสต์สำเร็จ!")
                    with open(audio_path, "rb") as f:
                        st.download_button("💾 ดาวน์โหลดไฟล์เสียง", f, file_name="quiet_lens_pro.mp3")

elif not gemini_key:
    st.info("💡 กรุณากรอก API Key และตรวจสอบ Secrets ก่อนเริ่มต้นครับ")

st.divider()
st.caption("The Quiet Lens Pro | Powered by Google Cloud Neural2 & Gemini 2.0")
