import streamlit as st
from google import genai
import pdfplumber
import os

# --- 1. หน้าตาแอป (Adaptive Minimalist) ---
st.set_page_config(page_title="The Quiet Lens", page_icon="📖", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Sarabun', sans-serif; }
    .notebook-container {
        padding: 25px;
        background-color: var(--secondary-background-color);
        border: 1px solid var(--divider-color);
        border-radius: 15px;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. ฟังก์ชันเสริม ---
def extract_text(uploaded_file):
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            return "".join(page.extract_text() for page in pdf.pages if page.extract_text())
    return str(uploaded_file.read(), "utf-8")

# --- 3. Session State เก็บสคริปต์ ---
if 'native_script' not in st.session_state:
    st.session_state.native_script = ""

# --- 4. Sidebar ---
with st.sidebar:
    st.title("⚙️ Native Audio Config")
    api_key = st.text_input("Gemini API Key:", type="password")
    voice_name = st.selectbox("เลือกโทนเสียง AI:", ["Aoede", "Puck", "Charon", "Kore", "Fenrir"])
    st.caption("Native Audio จะให้เสียงที่เหมือนมนุษย์ มีจังหวะหายใจและอารมณ์")

# --- 5. หน้าหลัก ---
st.title("The Quiet Lens 📖")
st.subheader("สัมผัสเสียงแห่งปัญญาผ่าน Native AI")

file = st.file_uploader("ลากไฟล์ที่ต้องการสรุปมาวางที่นี่", type=["pdf", "txt"])

if file and api_key:
    client = genai.Client(api_key=api_key)

    # ขั้นตอนที่ 1: สร้างสคริปต์ (Text Only ก่อน)
    if st.button("🧠 1. วิเคราะห์และร่างบทพอดแคสต์"):
        try:
            raw_content = extract_text(file)
            prompt_gen = f"""
            คุณคือ 'The Quiet Lens' สรุปเนื้อหานี้ให้เป็นบทพอดแคสต์ที่อบอุ่นและลึกซึ้ง 
            เขียนให้เป็นภาษาพูดที่นุ่มนวล มีจังหวะจะโคน เพื่อเตรียมนำไปบันทึกเสียง
            เนื้อหา: {raw_content[:12000]}
            """
            # ใช้ 2.5-flash ปกติเพื่อร่างบทก่อน
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_gen)
            st.session_state.native_script = response.text
        except Exception as e:
            st.error(f"ร่างบทไม่สำเร็จ: {e}")

    # ขั้นตอนที่ 2: แก้ไขสคริปต์
    if st.session_state.native_script:
        st.markdown("### ✍️ ปรับแต่งบทก่อนลงเสียง")
        edited_text = st.text_area("เกลาบทพอดแคสต์ของคุณ:", value=st.session_state.native_script, height=300)
        st.session_state.native_script = edited_text

        st.divider()

        # ขั้นตอนที่ 3: สร้าง Native Audio
        if st.button("🎙️ 2. สร้างพอดแคสต์ด้วย Native Audio (AI พูดเอง)"):
            try:
                with st.status("🚀 Gemini กำลังสังเคราะห์เสียงพอดแคสต์...", expanded=True) as status:
                    st.write("🧠 กำลังส่งบทให้โมเดล Native Audio...")
                    
                    # หัวใจสำคัญ: เรียกใช้ Native Audio Model
                    audio_response = client.models.generate_content(
                        model='gemini-2.5-flash-native-audio-latest',
                        contents=f"จงอ่านบทพูดนี้ด้วยน้ำเสียงนุ่มนวลและสุขุมในฐานะ The Quiet Lens: {edited_text}",
                        config={
                            "speech_config": voice_name
                        }
                    )
                    
                    st.write("🔊 กำลังประมวลผลไฟล์เสียง...")
                    with open("native_podcast.mp3", "wb") as f:
                        f.write(audio_response.audio_bytes)
                    
                    status.update(label="เสร็จสมบูรณ์!", state="complete")

                st.audio("native_podcast.mp3")
                st.download_button("💾 ดาวน์โหลดไฟล์เสียง (Native)", open("native_podcast.mp3", "rb"), file_name="quiet_lens_native.mp3")
                
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดกับ Native Audio: {e}")
                st.info("💡 หากขึ้น 404: อาจเป็นเพราะโมเดล Native Audio ยังไม่รองรับในบางเงื่อนไข ให้ลองเปลี่ยน Voice หรือใช้ Prompt ภาษาอังกฤษกำกับในขั้นตอน Generate Audio ครับ")

elif not api_key:
    st.info("💡 กรุณากรอก API Key เพื่อสัมผัสพลังของ Native Audio ครับ")
