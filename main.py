
import streamlit as st
import pandas as pd
import numpy as np
import base64

# ตั้งค่าหน้าเพจให้เป็นแบบกว้าง (Wide Mode) เป็นคำสั่งแรกสุดของสคริปต์
st.set_page_config(page_title="Solar AI Heating Index", page_icon="☀️", layout="wide")

# โค้ดสำหรับเปลี่ยนพื้นหลังทั้งหมดเป็นสีขาว และปรับสีตัวอักษรเป็นสีเข้ม
st.markdown("""
    <style>
    /* เปลี่ยนสีพื้นหลังหน้าหลักเป็นสีขาว */
    .stApp {
        background-color: #FFFFFF !important;
    }
    
    /* เปลี่ยนสีพื้นหลังของ Sidebar เป็นสีขาว (หรือเทาอ่อนมากๆ เพื่อให้ดูมีมิติ) */
    [data-testid="stSidebar"] {
        background-color:  #003366 !important;
    }
    
  /* 3. 🎯 ปรับสีตัวอักษรเฉพาะใน Sidebar ให้เป็นสีเทาเข้ม/ดำ */
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
            
            
    
    /* ยกเว้นสีของปุ่ม Alert (Success, Warning, Error) ให้คงสีเดิมไว้ */
    .stAlert p {
        color: inherit !important;
    }
    </style>
""", unsafe_allow_html=True)

with open("พื้นหลัง1.png", "rb") as f:
    bg_base64 = base64.b64encode(f.read()).decode()



# ใส่ภาพพื้นหลังฝั่งขวา
st.markdown(f"<style>.stApp {{ background-image: url('data:image/png;base64,{bg_base64}'); background-size: cover; background-attachment: fixed; }}</style>", unsafe_allow_html=True)

target_pr = 75.0

##---------------------------------------------------------------------------------------------------------------##

st.title("☀️ Solar AI Heating Index")
st.markdown("ระบบวิเคราะห์และประมวลผลประสิทธิภาพพลังงานแสงอาทิตย์ด้วย AI")
st.markdown("---")

# แนะนำโครงสร้างไฟล์
with st.expander("📝 คลิกเพื่อดูโครงสร้างไฟล์ Excel ที่แนะนำ"):
    st.write("ไฟล์ Excel ของคุณควรมีคอลัมน์หลักๆ ดังนี้ (ชื่อคอลัมน์พิมพ์ให้ตรงหรือใกล้เคียง):")
    st.markdown("- **Date / Time**: วันที่หรือเวลาบันทึกข้อมูล")
    st.markdown("- **Energy**: พลังงานไฟฟ้าที่ผลิตได้จริง (kWh)")
    st.markdown("- **Irradiance**: ค่าความเข้มแสงสะสม (kWh/m² หรือ W/m²)")
    st.markdown("- **Installed Capacity** : กำลังการติดตั้งของระบบ (kWp)")
    st.markdown("- **Temperature** (ถ้ามี): อุณหภูมิแผงเซลล์ (°C)")

##---------------------------------------------------------------------------------------------------------------##
with st.sidebar:
    st.image("Logo-cnes.png", use_container_width=True) ##Logo CNES
    st.markdown("---")
    st.subheader("⚙️ ตั้งค่าพารามิเตอร์ระบบ")
    system_mode = st.selectbox("เลือกโหมดการทำงาน", ["วิเคราะห์ภาพรวม", "คาดการณ์ประสิทธิภาพ", "รายงานความผิดปกติ"])
    
    # 🎨 ปรับปรุง CSS: ให้พื้นหลังเป็นน้ำเงิน ตัวอักษรทั่วไปเป็นสีขาว แต่เจาะจงให้ตัวอักษรในช่อง Selectbox เป็นสีดำ
    st.markdown("""
        <style>
        /* พื้นหลัง Sidebar เป็นสีน้ำเงิน และตัวอักษรทั่วไปเป็นสีขาว */
        [data-testid='stSidebar'] {
            background-color: #003366;
        }
        [data-testid='stSidebar'] * {
            color: white !important;
        }
        
        /* 🎯 เจาะจงเปลี่ยนเฉพาะตัวอักษร "ข้างในช่อง" และ "กล่องตัวเลือก" ของ Selectbox ให้เป็นสีดำ */
        [data-testid='stSidebar'] div[data-baseweb="select"] * {
            color: #000000 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.info(f"โหมดปัจจุบัน: {system_mode}")

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
        
# จับคู่คอลัมน์
        st.subheader("🔍 จับคู่คอลัมน์สำหรับการคำนวณ")
        col_select1, col_select2, col_select3, col_select4 = st.columns(4)
        
        with col_select1:
            date_col = st.selectbox("คอลัมน์ วันที่/เวลา (Date/Time)", df.columns)
        with col_select2:
            energy_col = st.selectbox("คอลัมน์ไฟฟ้าที่ผลิตได้ (kWh)", df.columns)
        with col_select3:
            irr_col = st.selectbox("คอลัมน์ความเข้มแสง (Irradiance)", df.columns)
        with col_select4:
            kwp_col = st.selectbox("คอลัมน์ Capacity (kWp.)", df.columns)

        st.markdown(" ") # เว้นช่องไฟเล็กน้อย
        
        # --- เพิ่มปุ่มสำหรับกดคำนวณ ---
        calculate_button = st.button("🚀 เริ่มประมวลผลและคำนวณผลลัพธ์", type="primary", use_container_width=True)

        if calculate_button:
            # ส่วนประมวลผลคำนวณเมื่อกดปุ่มเท่านั้น
            actual_energy_series = pd.to_numeric(df[energy_col], errors='coerce')
            total_irr_series = pd.to_numeric(df[irr_col], errors='coerce')
            kwp_series = pd.to_numeric(df[kwp_col], errors='coerce')
            
            actual_energy = actual_energy_series.sum()
            total_irradiance = total_irr_series.sum()
            
            if total_irradiance > 0:
                avg_kwp = kwp_series.mean() if kwp_series.mean() > 0 else 1
                specific_yield = actual_energy / avg_kwp
                pr_calculated = (specific_yield / total_irradiance) * 100
                
                st.markdown("---")
                st.subheader("🎯 ผลการวิเคราะห์ประสิทธิภาพ (PR Analysis)")
                
                # บังคับขนาดฟอนต์ Metric ป้องกันหลุดขอบ
                st.html("""
                    <style>
                    div[data-testid="stMetricLabel"] { font-size: 14px !important; white-space: normal !important; }
                    div[data-testid="stMetricValue"] { font-size: 22px !important; }
                    div[data-testid="stMetricDelta"] div { font-size: 12px !important; white-space: normal !important; }
                    </style>
                """)
                
                kpi1, kpi2, kpi3 = st.columns(3)
                with kpi1:
                    st.metric(label="Performance Ratio (PR)", value=f"{pr_calculated:.2f} %", delta=f"{pr_calculated - target_pr:.2f} % เทียบกับเป้าหมาย")
                with kpi2:
                    st.metric(label="พลังงานที่ผลิตได้จริงทั้งหมด", value=f"{actual_energy:,.2f} kWh")
                with kpi3:
                    st.metric(label="ค่าแสงแดดสะสมทั้งหมด (Peak Sun Hours)", value=f"{total_irradiance:,.2f} kWh/m²")
                
                # บทวิเคราะห์ AI
                st.markdown("### 🤖 บทวิเคราะห์จากระบบ")
                if pr_calculated >= target_pr:
                    st.success(f"🟢 **ระบบทำงานได้ดีเยี่ยม:** ค่า PR ปัจจุบันอยู่ที่ {pr_calculated:.2f}% ซึ่งสูงกว่าเป้าหมายที่ตั้งไว้ ({target_pr}%) บ่งบอกว่าไม่มีปัญหาเรื่องเงาบัง หรือความสกปรกบนแผงอย่างรุนแรง")
                elif pr_calculated >= 65:
                    st.warning(f"🟡 **ระบบทำงานอยู่ในเกณฑ์ยอมรับได้ แต่ควรตรวจสอบ:** ค่า PR อยู่ที่ {pr_calculated:.2f}% ต่ำกว่าเป้าหมายเล็กน้อย อาจเกิดจากความร้อนสะสมบนแผงสูง หรือแผงเริ่มมีคราบฝุ่นเกาะ")
                else:
                    st.error(f"🔴 **ระบบทำงานต่ำกว่ามาตรฐาน:** ค่า PR ต่ำกว่า 65% ({pr_calculated:.2f}%) แนะนำให้ส่งช่างเข้าตรวจสอบหน้างาน อาจมีปัญหาจาก Inverter ตัดการทำงาน, แผงสกปรกมาก หรือเกิดเงาบัง (Shading)")
                
                # ส่วนแสดงผลกราฟ
                if len(df) > 1:
                    st.markdown("---")
                    st.subheader("📈 กราฟเปรียบเทียบการผลิตพลังงานไฟฟ้ากับความเข้มแสง")
                    
                    chart_df = df[[date_col, energy_col, irr_col]].copy()
                    chart_df[energy_col] = pd.to_numeric(chart_df[energy_col], errors='coerce')
                    chart_df[irr_col] = pd.to_numeric(chart_df[irr_col], errors='coerce')
                    
                    chart_df[date_col] = chart_df[date_col].astype(str)
                    chart_df = chart_df.set_index(date_col)
                    chart_df.index.name = None
                    chart_df.columns = ["Energy (kWh)", "Irradiance"]
                    
                    st.line_chart(chart_df)
            else:
                st.error("❌ ไม่สามารถคำนวณได้เนื่องจากผลรวมค่าความเข้มแสงในไฟล์เป็น 0 หรือไม่ใช่ตัวเลข")
            
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการอ่านไฟล์: {e}")
else:
    # หน้าแรกตอนยังไม่อัปโหลดไฟล์ ให้โชว์สรุปการศึกษา 9 หัวข้อ
    st.info("💡 กรุณาอัพโหลดไฟล์ Excel ที่แถบด้านบน เพื่อเริ่มการคำนวณ")
    st.markdown("---")
    st.subheader("📊 ขอบเขตและข้อมูลที่ใช้ในการศึกษา (Solar AI Heating Index)")
    
    tab1, tab2, tab3 = st.tabs(["⚡ ข้อมูลไฟฟ้าและอาร์เรย์", "🌱 สภาพแวดล้อมและสมรรถนะ", "🛠️ ระบบบำรุงรักษาและหน้างาน"])
    with tab1:
        st.markdown("""
        * **1. ข้อมูลพลังงานไฟฟ้าที่ผลิตได้:** เช่น พลังงานสะสมรายวัน รายเดือน และรายปี (kWh)
        * **2. ข้อมูลกำลังไฟฟ้าจาก Inverter:** เช่น AC Power, DC Power, Voltage, Current และข้อมูลจาก MPPT Data
        * **5. ข้อมูล Alarm และ Fault:** แจ้งเตือนข้อผิดพลาดโดยตรงจากระบบเชื่อมต่อ Inverter หรือ Monitoring System
        """)
    with tab2:
        st.markdown("""
        * **3. ข้อมูลสภาพแวดล้อม:** เช่น Irradiance (ความเข้มแสงแดด), Ambient Temperature และ Module Temperature
        * **4. ข้อมูลสมรรถนะ (KPIs):** เช่น Performance Ratio (PR), Specific Yield, System Availability และ Capacity Factor
        """)
    with tab3:
        st.markdown("""
        * **6. ข้อมูล Downtime:** ช่วงเวลาที่ระบบหยุดทำงาน
        * **7. ข้อมูลการบำรุงรักษา:** ประวัติการล้างแผงโซลาร์, การตรวจสอบทางวิศวกรรมไฟฟ้า, การซ่อมบำรุง และบันทึกการเปลี่ยนอะไหล่
        * **8. ข้อมูลการออกแบบระบบ (Design):** แบบแปลน Layout, วิธีการจัด String, Inverter Capacity และ SLD
        * **9. ข้อมูลสภาพหน้างานจริง:** บันทึกมุมเงาบัง (Shading), อัตราการสะสมของฝุ่น และข้อจำกัดด้านความปลอดภัย
        """)