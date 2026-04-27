import streamlit as st
import requests
import random
import pandas as pd
import yagmail
import time


st.set_page_config(page_title="PredictX Pro", layout="wide", page_icon="⚙️")


def send_email_alert(confidence):
    try:
        sender = "prajval26112005@gmail.com"
        pwd = "exzvxidcdradfdnm" 
        receiver = "prajval26112005@gmail.com"
        
        yag = yagmail.SMTP(sender, pwd)
        contents = [
            f"<h2>⚠️ Machine Failure Risk Detected</h2>",
            f"<p>The PredictX AI system has identified a high risk of equipment failure.</p>",
            f"<ul><li><b>AI Confidence:</b> {confidence:.2f}%</li>",
            f"<li><b>System Time:</b> {time.strftime('%Y-%m-%d %H:%M:%S')}</li></ul>",
            "<p>Please inspect the hardware immediately.</p>"
        ]
        yag.send(to=receiver, subject="🚨 URGENT: PredictX Alert", contents=contents)
        return True
    except Exception as e:
        st.sidebar.error(f"Mail Error: {e}")
        return False


if "history" not in st.session_state:
    st.session_state.history = []
if "chart_data" not in st.session_state:
    st.session_state.chart_data = pd.DataFrame(columns=["Temperature", "Vibration", "Pressure"])
if "last_result" not in st.session_state:
    st.session_state.last_result = None

st.title("⚙️ PredictX Pro")
st.markdown("### AI-Powered Predictive Maintenance Dashboard")

with st.sidebar:
    st.header("System Settings")
    auto_mode = st.toggle("🔄 Continuous Auto-Simulation", value=False)
    refresh_rate = st.select_slider("Refresh Rate (seconds)", options=[1, 2, 5, 10], value=2)
    st.divider()
    if st.button("🗑️ Clear All Data"):
        st.session_state.history = []
        st.session_state.chart_data = pd.DataFrame(columns=["Temperature", "Vibration", "Pressure"])
        st.session_state.last_result = None
        st.rerun()

col_input, col_res = st.columns([1, 1.2])

with col_input:
    st.subheader("📡 Sensor Input")
    
    if auto_mode:
       
        if not st.session_state.chart_data.empty:
            last = st.session_state.chart_data.iloc[-1]
            temp = last["Temperature"] + random.uniform(-2, 3)
            vib = last["Vibration"] + random.uniform(-5, 6)
            pres = last["Pressure"] + random.uniform(-3, 3)
        else:
            temp, vib, pres = 70.0, 30.0, 45.0
        
    
        temp = max(40, min(130, temp))
        vib = max(10, min(100, vib))
        pres = max(10, min(120, pres))
        
        st.info(f"LIVE FEED: Temp {temp:.1f}°C | Vib {vib:.1f} | Pres {pres:.1f}")
       
        trigger_prediction = True
    else:
        temp = st.slider("Temperature (°C)", 40, 130, 75)
        vib = st.slider("Vibration (mm/s)", 10, 100, 35)
        pres = st.slider("Pressure (PSI)", 10, 120, 50)
        trigger_prediction = st.button("🔍 Run Manual Diagnostic", use_container_width=True)


if trigger_prediction:
    try:
        payload = {"temperature": float(temp), "vibration": float(vib), "pressure": float(pres)}
        response = requests.post("http://127.0.0.1:8000/predict", json=payload)
        res_data = response.json()
        
        
        st.session_state.last_result = res_data
        new_row = pd.DataFrame([[temp, vib, pres]], columns=["Temperature", "Vibration", "Pressure"])
        st.session_state.chart_data = pd.concat([st.session_state.chart_data, new_row], ignore_index=True)
        
        
        st.session_state.history.append({
            "Time": time.strftime("%H:%M:%S"),
            "Temp": round(temp, 1),
            "Vib": round(vib, 1),
            "Pres": round(pres, 1),
            "Status": "🚨 FAILURE" if res_data["prediction"] == 1 else "✅ OK"
        })
    except:
        st.error("Backend Offline")


with col_res:
    st.subheader("📊 AI Analytics")
    if st.session_state.last_result:
        res = st.session_state.last_result
        conf = res["confidence"] * 100
        
        m1, m2 = st.columns(2)
        if res["prediction"] == 1:
            m1.metric("Status", "⚠️ FAILURE RISK", delta="CRITICAL", delta_color="inverse")
            m2.metric("AI Confidence", f"{conf:.1f}%")
            
           
            if auto_mode: st.toast("Failure Detected!", icon="⚠️")
            
            if st.button("🚨 SEND ALERT EMAIL", use_container_width=True, type="primary"):
                if send_email_alert(conf):
                    st.success("📩 Alert Sent!")
        else:
            m1.metric("Status", "✅ STABLE", delta="OPTIMAL")
            m2.metric("Safety Margin", f"{100-conf:.1f}%")
    else:
        st.info("Start simulation or manual predict to view data.")

# --- TRENDS ---
st.divider()
if not st.session_state.chart_data.empty:
    st.write("### 📈 Live Telemetry")
    # Using tail(20) for a scrolling window effect
    st.line_chart(st.session_state.chart_data.tail(20))

# --- AUTO-REFRESH TRIGGER ---
if auto_mode:
    time.sleep(refresh_rate)
    st.rerun()