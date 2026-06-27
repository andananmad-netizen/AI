import streamlit as st
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
import os
import io
from datetime import datetime
import uuid

# ---------------- ชื่อเว็บไซต์ + Icon ----------------
st.set_page_config(page_title="Solar AI Heating Index", page_icon="☀️", layout="wide")

# ================= SIDEBAR SOLAR THEME (NEW - SAFE ADD) =================
st.markdown("""
<style>
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a, #1e3a8a, #0ea5e9);
}

[data-testid="stSidebar"] * {
    color: white !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #fbbf24 !important;
}
</style>
""", unsafe_allow_html=True)

# -----------------ภาพพื้นหลัง-----------------------
def bg(image):
    if os.path.exists(image):
        with open(image, "rb") as f:
            img = base64.b64encode(f.read()).decode()

        st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{img}");
            background-size: cover;
            background-position: center;
        }}
        </style>
        """, unsafe_allow_html=True)

bg("พื้นหลัง1.png")

# -----------------ตัวแปรเป้าหมาย-----------------------
target_pr = 75.0

# -----------------ตัวแปรดาวน์โหลด Excel-----------------------
history_file = "download_history.csv"

# ---------------- SAFE LOAD HISTORY ----------------
def load_history():
    try:
        if os.path.exists(history_file) and os.path.getsize(history_file) > 0:
            df = pd.read_csv(history_file)
            if df.empty:
                return []
            return df.to_dict("records")
        return []
    except:
        return []

# ---------------- SAFE SAVE HISTORY ----------------
def save_history(file_name, project_name):

    new_record = {
        "id": str(uuid.uuid4()),
        "file": file_name,
        "project": project_name,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    st.session_state.download_history.insert(0, new_record)
    st.session_state.download_history = st.session_state.download_history[:10]

    try:
        df = pd.DataFrame(st.session_state.download_history)
        if not df.empty:
            df.to_csv(history_file, index=False)
        else:
            if os.path.exists(history_file):
                os.remove(history_file)
    except:
        pass

# ---------------- SESSION STATE ----------------
if "download_history" not in st.session_state:
    st.session_state.download_history = load_history()

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "result_data" not in st.session_state:
    st.session_state.result_data = {}

# ---------------- SIDEBAR ----------------
with st.sidebar:
    if os.path.exists("Logo-cnes.png"):
        st.image("Logo-cnes.png", use_container_width=True)

    st.markdown("---")
    st.subheader("⚙️ ตั้งค่าพารามิเตอร์ระบบ")

    # ✅ FIX CSS เฉพาะ sidebar (แยก label / input / dropdown)
    st.markdown("""
    <style>
    /* พื้นหลัง sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a, #1e3a8a, #0ea5e9);
    }

    /* ข้อความทั่วไป sidebar */
    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    /* ✅ label ของ selectbox (ให้เป็นสีขาว) */
    section[data-testid="stSidebar"] label {
        color: white !important;
        font-weight: 600;
    }

    /* ✅ ตัว dropdown (ให้เป็นสีดำ) */
    section[data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: black !important;
    }

    /* ช่อง input ใน dropdown */
    section[data-testid="stSidebar"] input {
        color: black !important;
    }

    /* dropdown กล่อง */
    section[data-testid="stSidebar"] div[data-baseweb="select"] {
        background-color: white;
        border-radius: 6px;
    }
    </style>
    """, unsafe_allow_html=True)

    system_mode = st.selectbox(
        "เลือกโหมดการทำงาน",
        ["วิเคราะห์ภาพรวม", "คาดการณ์ประสิทธิภาพ", "รายงานความผิดปกติ"]
    )

    st.info(f"โหมดปัจจุบัน: {system_mode}")

# ---------------- MAIN ----------------
if system_mode in ["วิเคราะห์ภาพรวม", "คาดการณ์ประสิทธิภาพ"]:

    st.title("☀️ Solar AI Heating Index")
    st.markdown("## ระบบวิเคราะห์ประสิทธิภาพพลังงานแสงอาทิตย์")
    st.markdown("---")

    uploaded_file = st.file_uploader("📂 เลือกไฟล์ Excel", type=["xlsx", "xls"])

    if uploaded_file is not None:

        project_name = os.path.splitext(uploaded_file.name)[0]
        st.title(f"🏢 โครงการ: {project_name}")

        try:
            df = pd.read_excel(uploaded_file, header=1)
            st.success("✅ โหลดไฟล์สำเร็จ")

            col1, col2, col3, col4 = st.columns(4)
            date_col = col1.selectbox("วันที่", df.columns)
            energy_col = col2.selectbox("Energy", df.columns)
            irr_col = col3.selectbox("Irradiance", df.columns)
            kwp_col = col4.selectbox("kWp", df.columns)

            if st.button("🚀 วิเคราะห์"):

                actual_energy = pd.to_numeric(df[energy_col], errors="coerce").fillna(0).sum()
                total_irradiance = pd.to_numeric(df[irr_col], errors="coerce").fillna(0).sum()
                kwp_val = pd.to_numeric(df[kwp_col], errors="coerce").mean()
                kwp_final = kwp_val if kwp_val > 0 else 100.0

                if total_irradiance > 0:

                    pr = (actual_energy / kwp_final / total_irradiance) * 100

                    st.session_state.analysis_done = True
                    st.session_state.result_data = {
                        "pr": pr,
                        "energy": actual_energy,
                        "irr": total_irradiance,
                        "df": df,
                        "date": date_col,
                        "energy_col": energy_col,
                        "irr_col": irr_col
                    }

            if st.session_state.analysis_done:

                data = st.session_state.result_data

                st.markdown("---")
                st.subheader("🎯 PR Analysis")

                k1, k2, k3 = st.columns(3)
                k1.metric("PR", f"{data['pr']:.2f} %", f"{data['pr'] - target_pr:.2f} %")
                k2.metric("Energy", f"{data['energy']:,.2f} kWh")
                k3.metric("Irradiance", f"{data['irr']:,.2f}")

                if len(data["df"]) > 1:
                    fig = make_subplots(specs=[[{"secondary_y": True}]])

                    fig.add_trace(go.Bar(
                        x=data["df"][data["date"]],
                        y=data["df"][data["energy_col"]],
                        name="Energy"
                    ), secondary_y=False)

                    fig.add_trace(go.Scatter(
                        x=data["df"][data["date"]],
                        y=data["df"][data["irr_col"]],
                        name="Irradiance"
                    ), secondary_y=True)

                    st.plotly_chart(fig, use_container_width=True)

                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    data["df"].to_excel(writer, index=False)

                file_name = f"{project_name}_Analysis.xlsx"

                st.download_button(
                    "📥 ดาวน์โหลด Excel",
                    data=output.getvalue(),
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"dl_{uuid.uuid4()}",
                    on_click=save_history,
                    args=(file_name, project_name)
                )

        except Exception as e:
            st.error(f"❌ Error: {e}")

    # ---------------- HISTORY ----------------
    st.markdown("---")
    st.subheader("📜 ประวัติการดาวน์โหลด")

    if st.session_state.download_history:

        df_hist = pd.DataFrame(st.session_state.download_history)

        selected = st.multiselect(
            "เลือกไฟล์ที่ต้องการลบ",
            options=df_hist["file"]
        )

        colA, colB = st.columns(2)

        with colA:
            if st.button("🗑️ ลบที่เลือก"):
                st.session_state.download_history = [
                    x for x in st.session_state.download_history
                    if x["file"] not in selected
                ]
                pd.DataFrame(st.session_state.download_history).to_csv(history_file, index=False)
                st.rerun()

        with colB:
            if st.button("❌ ลบทั้งหมด"):
                st.session_state.download_history = []
                if os.path.exists(history_file):
                    os.remove(history_file)
                st.rerun()

        st.markdown("---")

        for item in st.session_state.download_history:
            c1, c2 = st.columns([8, 1])
            with c1:
                st.write(f"✅ {item['time']} | {item['project']} | {item['file']}")
            with c2:
                if st.button("❌", key=f"del_{item['id']}"):
                    st.session_state.download_history = [
                        x for x in st.session_state.download_history
                        if x["id"] != item["id"]
                    ]
                    pd.DataFrame(st.session_state.download_history).to_csv(history_file, index=False)
                    st.rerun()

    else:
        st.info("ยังไม่มีข้อมูล")

# ---------------- AI MODE ----------------
elif system_mode == "รายงานความผิดปกติ":
    st.title("📸 ระบบตรวจจับความผิดปกติแผงโซลาร์เซลล์ด้วย AI")
    MODEL_URL = "https://teachablemachine.withgoogle.com/models/T5Nn28B2A/"
    html_code = f"""<div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #e9ecef; text-align: center;">
        <input type="file" id="image-selector" accept="image/*" style="margin-bottom: 20px;">
        <img id="selected-image" style="max-width: 300px; display: none; margin: 0 auto; border-radius: 8px;">
        <div id="label-container" style="margin-top: 20px; font-weight: bold; font-size: 20px;">กำลังโหลดโมเดล...</div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@latest/dist/tf.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@teachablemachine/image@latest/dist/teachablemachine-image.min.js"></script>
    <script>
        const URL = "{MODEL_URL}";
        let model;
        async function init() {{ try {{ model = await tmImage.load(URL + "model.json", URL + "metadata.json"); document.getElementById("label-container").innerHTML = "✨ โมเดลพร้อมใช้งาน!"; }} catch(e) {{ document.getElementById("label-container").innerHTML = "❌ โหลดโมเดลไม่สำเร็จ"; }} }}
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
    </script>"""
    components.html(html_code, height=500)