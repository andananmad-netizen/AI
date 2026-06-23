import streamlit as st
import pandas as pd
import numpy as np

target_pr = 75.0

##---------------------------------------------------------------------------------------------------------------##

# แนะนำโครงสร้างไฟล์
with st.expander("📝 คลิกเพื่อดูโครงสร้างไฟล์ Excel ที่แนะนำ"):
    st.write("ไฟล์ Excel ของคุณควรมีคอลัมน์หลักๆ ดังนี้ (ชื่อคอลัมน์พิมพ์ให้ตรงหรือใกล้เคียง):")
    st.markdown("- **Date / Time**: วันที่หรือเวลาบันทึกข้อมูล")
    st.markdown("- **Energy**: พลังงานไฟฟ้าที่ผลิตได้จริง (kWh)")
    st.markdown("- **Irradiance**: ค่าความเข้มแสงสะสม (kWh/m² หรือ W/m²)")
    st.markdown("- **Installed Capacity** : กำลังการติดตั้งของระบบ (kWp)")
    st.markdown("- **Temperature** (ถ้ามี): อุณหภูมิแผงเซลล์ (°C)")

##---------------------------------------------------------------------------------------------------------------##

st.sidebar.image("Logo-cnes.png", use_container_width=True) ##Logo CNES
st.sidebar.markdown("<style>[data-testid='stSidebar'] {background-color: #003366;} [data-testid='stSidebar'] * {color: white !important;}</style>", unsafe_allow_html=True) ##สีพื้นหลังของ Sidebar
st.sidebar.header("⚙️ ตั้งค่าพารามิเตอร์ระบบ")

##---------------------------------------------------------------------------------------------------------------##

# ส่วนอัพโหลดไฟล์
uploaded_file = st.file_uploader("📂 เลือกไฟล์ Excel (.xlsx หรือ .xls)", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # อ่านไฟล์ Excel
        df = pd.read_excel(uploaded_file)
        
        st.success("✅ โหลดไฟล์ข้อมูลสำเร็จ!")
        
        # แสดงตัวอย่างข้อมูล
        st.subheader("📋 ตัวอย่างข้อมูลจากไฟล์ของคุณ")
        st.dataframe(df.head(34), use_container_width=True)
        
        # ให้ผู้ใช้จับคู่คอลัมน์ (กรณีชื่อคอลัมน์ไม่ตรง)
        st.subheader("🔍 จับคู่คอลัมน์สำหรับการคำนวณ")
        col_select1, col_select2, col_select3, col_select4 = st.columns(4)
        
        with col_select1:
            # 🟢 แก้จุดที่ 1: เปลี่ยนป้ายกำกับให้ตรงเป็น วันที่/เวลา (Date/Time) เพื่อนำไปทำ Index ของกราฟ
            date_col = st.selectbox("คอลัมน์ วันที่/เวลา (Date/Time)", df.columns)
        with col_select2:
            energy_col = st.selectbox("คอลัมน์ไฟฟ้าที่ผลิตได้ (kWh)", df.columns)
        with col_select3:
            irr_col = st.selectbox("คอลัมน์ความเข้มแสง (Irradiance)", df.columns)
        with col_select4:
            kwp_col = st.selectbox("คอลัมน์ Capacity (kWp.)", df.columns)

##---------------------------------------------------------------------------------------------------------------##
            
        # ปุ่มเริ่มคำนวณ
        if st.button("🚀 เริ่มวิเคราะห์และคำนวณค่า PR"):

##---------------------------------------------------------------------------------------------------------------##

            # สูตรและการกำหนดตัวแปรในการคำนวณ PR%
            # แปลงข้อมูลแต่ละคอลัมน์ให้เป็นตัวเลขรายแถว (Series)
            actual_energy_series = pd.to_numeric(df[energy_col], errors='coerce')
            total_irr_series = pd.to_numeric(df[irr_col], errors='coerce')
            kwp_series = pd.to_numeric(df[kwp_col], errors='coerce')
            
            # คำนวณหาผลรวมเพื่อใช้โชว์ใน KPI และเงื่อนไข
            actual_energy = actual_energy_series.sum()
            total_irradiance = total_irr_series.sum()
            
            if total_irradiance > 0:
                # คำนวณ PR โดยรวมจากสูตรภาพรวมระบบ (Total Energy / (Total Irr * Average kWp))
                # หรือหาค่าเฉลี่ยจากข้อมูลทั้งหมด
                avg_kwp = kwp_series.mean() if kwp_series.mean() > 0 else 1
                specific_yield = actual_energy / avg_kwp
                pr_calculated = (specific_yield / total_irradiance) * 100
                
                st.markdown("---")
                st.subheader("🎯 ผลการวิเคราะห์ประสิทธิภาพ (PR Analysis)")
                
                # 🟢 แก้จุดที่ 2: ปรับปรุง CSS ให้ขยาย/ย่อตัวอักษร Metric อัตโนมัติ ป้องกันตัวอักษร ... หลุดหาย
                st.html("""
                    <style>
                    div[data-testid="stMetricLabel"] { font-size: 14px !important; white-space: normal !important; }
                    div[data-testid="stMetricValue"] { font-size: 22px !important; }
                    div[data-testid="stMetricDelta"] div { font-size: 12px !important; white-space: normal !important; }
                    </style>
                """)
                
                kpi1, kpi2, kpi3 = st.columns(3)
                with kpi1:
                    st.metric(
                        label="Performance Ratio (PR)", 
                        value=f"{pr_calculated:.2f} %", 
                        delta=f"{pr_calculated - target_pr:.2f} % เทียบกับเป้าหมาย"
                    )
                with kpi2:
                    st.metric(label="พลังงานที่ผลิตได้จริงทั้งหมด", value=f"{actual_energy:,.2f} kWh")
                with kpi3:
                    # ปรับหน่วยเล็กน้อยให้กระชับขึ้น
                    st.metric(label="ค่าแสงแดดสะสมทั้งหมด (Peak Sun Hours)", value=f"{total_irradiance:,.2f} kWh/m²")
                
                # การประเมินผลโดย AI เบื้องต้น
                st.markdown("### 🤖 บทวิเคราะห์จากระบบ")
                if pr_calculated >= target_pr:
                    st.success(f"🟢 **ระบบทำงานได้ดีเยี่ยม:** ค่า PR ปัจจุบันอยู่ที่ {pr_calculated:.2f}% ซึ่งสูงกว่าเป้าหมายที่ตั้งไว้ ({target_pr}%) บ่งบอกว่าไม่มีปัญหาเรื่องเงาบัง หรือความสกปรกบนแผงอย่างรุนแรง")
                elif pr_calculated >= 65:
                    st.warning(f"🟡 **ระบบทำงานอยู่ในเกณฑ์ยอมรับได้ แต่ควรตรวจสอบ:** ค่า PR อยู่ที่ {pr_calculated:.2f}% ต่ำกว่าเป้าหมายเล็กน้อย อาจเกิดจากความร้อนสะสมบนแผงสูง หรือแผงเริ่มมีคราบฝุ่นเกาะ")
                else:
                    st.error(f"🔴 **ระบบทำงานต่ำกว่ามาตรฐาน:** ค่า PR ต่ำกว่า 65% ({pr_calculated:.2f}%) แนะนำให้ส่งช่างเข้าตรวจสอบหน้างาน อาจมีปัญหาจาก Inverter ตัดการทำงาน, แผงสกปรกมาก หรือเกิดเงาบัง (Shading)")
                
                # ทำกราฟแนวโน้มรายวัน/รายชั่วโมง (ถ้ามีข้อมูลมากพอ)
                if len(df) > 1:
                    st.markdown("---")
                    st.subheader("📈 กราฟเปรียบเทียบการผลิตพลังงานไฟฟ้ากับความเข้มแสง")
                    
                    # 🟢 แก้จุดที่ 3: จัดการชื่อคอลัมน์และแปลงประเภทข้อมูลก่อนนำไปพลอตลงกราฟเพื่อไม่ให้เกิด Error 
                    chart_df = df[[date_col, energy_col, irr_col]].copy()
                    chart_df.columns = chart_df.columns.astype(str)
                    
                    chart_df[str(energy_col)] = pd.to_numeric(chart_df[str(energy_col)], errors='coerce')
                    chart_df[str(irr_col)] = pd.to_numeric(chart_df[str(irr_col)], errors='coerce')
                    
                    chart_df = chart_df.set_index(str(date_col))
                    st.line_chart(chart_df)
                    
            else:
                st.error("❌ ไม่สามารถคำนวณได้เนื่องจากผลรวมค่าความเข้มแสงในไฟล์เป็น 0 หรือไม่ใช่ตัวเลข")
                
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการอ่านไฟล์: {e}")
else:
    st.info("💡 กรุณาอัพโหลดไฟล์ Excel ที่แถบด้านบน เพื่อเริ่มการคำนวณ")