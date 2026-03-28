# --- ภายในส่วนที่ st.button("เริ่มการตกผลึกความคิด") ---
try:
    client = genai.Client(api_key=api_key)
    
    with st.status("🚀 The Quiet Lens กำลังบันทึกเสียงแห่งปัญญา...", expanded=True) as status:
        st.write("📖 อ่านเนื้อหา...")
        raw_text = extract_text(uploaded_file)
        
        st.write("🧠 กำลังกลั่นกรองความคิด...")
        prompt = f"""
        คุณคือ 'The Quiet Lens' นักจัดพอดแคสต์ที่นุ่มนวลและสุขุม
        จงสรุปเนื้อหาที่ได้รับ ให้เป็นบทพอดแคสต์ที่อบอุ่น มีรายละเอียด และยกตัวอย่างให้เข้ากับชีวิตจริงในยุคปัจจุบัน
        เน้นการเล่าเรื่องที่ทำให้คนฟังรู้สึกสงบและได้แง่คิดลึกซึ้ง
        ข้อความ: {raw_text[:12000]}
        """
        
        # --- แก้ไข Config ให้สั้นลงตามที่ SDK ต้องการ ---
        response = client.models.generate_content(
            model='gemini-2.5-flash-native-audio-latest',
            contents=prompt,
            config={
                # ในปี 2026 เราใส่ชื่อเสียงตรงนี้ได้เลยครับ! 
                # ลอง 'Puck' (ชาย) หรือ 'Aoede' (หญิง) ตามใจชอบ
                "speech_config": "Aoede" 
            }
        )
        
        final_script = response.text
        
        st.write("🔊 กำลังรวมไฟล์เสียงพอดแคสต์...")
        with open("quiet_lens.mp3", "wb") as f:
            f.write(response.audio_bytes)
            
        status.update(label="เสร็จสมบูรณ์!", state="complete")

    # แสดงผล
    st.markdown(f'<div class="notebook-container"><div class="quote-text">{final_script}</div></div>', unsafe_allow_html=True)
    st.audio("quiet_lens.mp3")
    
except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")
