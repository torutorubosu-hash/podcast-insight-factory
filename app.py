import google.generativeai as genai

# --- ตั้งค่า API Key (นอกฟังก์ชัน) ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("กรุณาตั้งค่า GEMINI_API_KEY ในหน้า Secrets ก่อนครับ")

# --- ภายในส่วน st.button ("เริ่มการตกผลึกความคิด") ---
try:
    # 1. นิยาม prompt
    prompt = f"สรุปเนื้อหานี้เป็นพอดแคสต์สไตล์นิ้วกลม: {raw_text[:8000]}"
    
    # 2. เรียกใช้โมเดล (ใช้ชื่อเต็มเพื่อความชัวร์)
    model = genai.GenerativeModel(model_name='gemini-1.5-flash') 
    
    # 3. สั่ง Gen
    response = model.generate_content(prompt)
    script = response.text
    
    # ... ทำขั้นตอนเสียงต่อ ...
except Exception as e:
    # ถ้ายัง 404 อีก ให้ลองถอยไปใช้ gemini-pro (เพื่อเช็คว่า API Key ปกติไหม)
    st.warning("กำลังลองใช้โมเดลสำรอง...")
    model = genai.GenerativeModel(model_name='gemini-pro')
    response = model.generate_content(prompt)
    script = response.text
