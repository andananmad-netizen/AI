import streamlit as st
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
import plotly.express as px
import base64
import os
import io

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Solar AI Heating Index", page_icon="☀️", layout="wide")

# Style สำหรับ Sidebar
st.sidebar.markdown(
    """
    <style>
        [data-testid="stSidebar"] { background-color: #003366; }
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4, [data-testid="stSidebar"] label {
            color: white !important;
        }
        div[data-baseweb="select"] *, ul[role="listbox"] * { color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True
)

# Sidebar
with st.sidebar:
    if os.path.exists("Logo-cnes.png"):
        st.image("Logo-cnes.png", use_container_width=True)
    st.markdown("---")
    st.subheader("⚙️ ตั้งค่าพารามิเตอร์ระบบ")
    system_mode = st.selectbox("เลือกโหมดการทำงาน", ["วิเคราะห์ภาพรวม", "คาดการณ์ประสิทธิภาพ", "รายงานความผิดปกติ"])
    target_pr = 75.0
    st.info(f"โหมดปัจจุบัน: {system_mode}")

# --- ส่วนพื้นหลัง ---
try:
    if os.path.exists("พื้นหลัง1.png"):
        with open("พื้นหลัง1.png", "rb") as f:
            bg_base64 = base64.b64encode(f.read()).decode()
        st.markdown(f"<style>.stApp {{ background-image: url('data:image/png;base64,{bg_base64}'); background-size: cover; background-attachment: fixed; }}</style>", unsafe_allow_html=True)
except Exception:
    pass

# --- ส่วน Logic ของหน้าจอ ---
if system_mode in ["วิเคราะห์ภาพรวม", "คาดการณ์ประสิทธิภาพ"]:
    st.title("☀️ Solar AI Heating Index")
    st.markdown("## ระบบวิเคราะห์และประมวลผลประสิทธิภาพพลังงานแสงอาทิตย์")
    st.markdown("---")
    
    uploaded_file = st.file_uploader("📂 เลือกไฟล์ Excel (.xlsx หรือ .xls)", type=["xlsx", "xls"])

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file, header=1)
            st.success("✅ โหลดไฟล์ข้อมูลสำเร็จ!")
            
            with st.expander("📋 ดูตัวอย่างข้อมูล"):
                st.dataframe(df.head(10), use_container_width=True)
            
            st.subheader("🔍 จับคู่คอลัมน์สำหรับการคำนวณ")
            col1, col2, col3, col4 = st.columns(4)
            with col1: date_col = st.selectbox("คอลัมน์วันที่/เวลา", df.columns)
            with col2: energy_col = st.selectbox("คอลัมน์ไฟฟ้าที่ผลิตได้ (kWh)", df.columns)
            with col3: irr_col = st.selectbox("คอลัมน์ความเข้มแสง (Irradiance)", df.columns)
            with col4: kwp_col = st.selectbox("คอลัมน์กำลังติดตั้ง (kWp)", df.columns)
                
            if st.button("🚀 เริ่มวิเคราะห์และคำนวณค่า PR"):
                # การคำนวณ
                actual_energy = pd.to_numeric(df[energy_col], errors='coerce').fillna(0).sum()
                total_irradiance = pd.to_numeric(df[irr_col], errors='coerce').fillna(0).sum()
                kwp_val = pd.to_numeric(df[kwp_col], errors='coerce').mean()
                kwp_final = kwp_val if kwp_val > 0 else 100.0
    
                if total_irradiance > 0:
                    specific_yield = actual_energy / kwp_final
                    pr_calculated = (specific_yield / total_irradiance) * 100
                    
                    st.markdown("---")
                    st.subheader("🎯 ผลการวิเคราะห์ประสิทธิภาพ (PR Analysis)")
                    k1, k2, k3 = st.columns(3)
                    k1.metric("Performance Ratio (PR)", f"{pr_calculated:.2f} %", f"{pr_calculated - target_pr:.2f} %")
                    k2.metric("ผลิตไฟฟ้าจริง", f"{actual_energy:,.2f} kWh")
                    k3.metric("ค่าแสงสะสม", f"{total_irradiance:,.2f} kWh/m²")
                    
                    # กราฟ
                    if len(df) > 1:
                        st.subheader("📈 กราฟเปรียบเทียบแนวโน้ม")
                        fig = px.line(df, x=date_col, y=[energy_col, irr_col], title="Energy vs Irradiance")
                        fig.update_yaxes(matches=None)
                        st.plotly_chart(fig, use_container_width=True)

                    # ปุ่มดาวน์โหลด (วางไว้หลังคำนวณเสร็จ)
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False, sheet_name='Report')
                    st.download_button(
                        label="📥 ดาวน์โหลดผลการวิเคราะห์เป็น Excel",
                        data=output.getvalue(),
                        file_name="Solar_Analysis_Report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.error("❌ ค่า Irradiance ในคอลัมน์ที่เลือกไม่ถูกต้อง")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการประมวลผลไฟล์: {e}")
    else:
        st.info("💡 กรุณาอัพโหลดไฟล์ Excel ที่แถบด้านบน")





elif system_mode == "รายงานความผิดปกติ":
    st.title("📸 ระบบตรวจจับความผิดปกติแผงโซลาร์เซลล์ด้วย AI")
    # ส่วนของ HTML/JS คงเดิมไว้ได้เลยครับ...
    MODEL_URL = "https://teachablemachine.withgoogle.com/models/T5Nn28B2A/"
    
    html_code = f"""
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #e9ecef; text-align: center;">
        <input type="file" id="image-selector" accept="image/*" style="margin-bottom: 20px;">
        <img id="selected-image" style="max-width: 300px; display: none; margin: 0 auto; border-radius: 8px;">
        <div id="label-container" style="margin-top: 20px; font-weight: bold; font-size: 20px;">กำลังโหลดโมเดล...</div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@latest/dist/tf.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@teachablemachine/image@latest/dist/teachablemachine-image.min.js"></script>
    <script>
        const URL = "{MODEL_URL}";
        let model;
        async function init() {{
            try {{
                model = await tmImage.load(URL + "model.json", URL + "metadata.json");
                document.getElementById("label-container").innerHTML = "✨ โมเดลพร้อมใช้งาน!";
            }} catch(e) {{ document.getElementById("label-container").innerHTML = "❌ โหลดโมเดลไม่สำเร็จ"; }}
        }}
        document.getElementById('image-selector').addEventListener('change', function(e) {{
            const reader = new FileReader();
            reader.onload = function(event) {{
                const img = document.getElementById('selected-image');
                img.src = event.target.result;
                img.style.display = "block";
                img.onload = async () => {{
                    document.getElementById("label-container").innerHTML = "🔍 กำลังวิเคราะห์...";
                    const prediction = await model.predict(img);
                    let top = prediction.reduce((a, b) => a.probability > b.probability ? a : b);
                    document.getElementById("label-container").innerHTML = "ผลสรุป: " + top.className + " (" + (top.probability * 100).toFixed(2) + "%)";
                }};
            }};
            reader.readAsDataURL(e.target.files[0]);
        }});
        init();
    </script>
    """
    components.html(html_code, height=500)