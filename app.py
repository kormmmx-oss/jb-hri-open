import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests

# --- 1. 설정 및 지역 데이터 ---
st.set_page_config(page_title="전북 기상 HRI 시스템", layout="wide")

STATIONS = {
    "전주": "146", "군산": "140", "정읍": "245", 
    "남원": "248", "익산": "249", "고창": "251"
}

# --- 2. 데이터 가져오기 (API 예시) ---
# 실제 사용 시 서비스키 입력 필요
def fetch_weather_data(stn_id):
    # 실제 기상청 API 연동 구간 (인증키가 없을 경우 기본값 반환)
    try:
        # 여기에 실제 기상청 API 호출 로직을 넣으세요
        # 예: requests.get(url, params=...)
        return {"temp": 26.5, "pwat": 70.0, "v850": 22.0, "theta_e": 340.0}
    except:
        return {"temp": 26.5, "pwat": 70.0, "v850": 22.0, "theta_e": 340.0}

# --- 3. UI 및 입력 ---
st.title("🌧️ 전북지역 극한호우 예측 대시보드 v2.0")
selected_city = st.sidebar.selectbox("관측 지역 선택", list(STATIONS.keys()))
data = fetch_weather_data(STATIONS[selected_city])

st.sidebar.header("📊 관측값 조정")
sst = st.sidebar.slider("해수면 온도 (SST, °C)", 20.0, 32.0, data["temp"])
pwat = st.sidebar.slider("가용가강수량 (PWAT, mm)", 30.0, 90.0, data["pwat"])
v850 = st.sidebar.slider("하층제트 (V850, m/s)", 0.0, 40.0, data["v850"])
theta_e = st.sidebar.slider("상당온위 (Theta-e, K)", 310, 360, data["theta_e"])

# --- 4. HRI 계산 로직 ---
s_sst = (sst - 20) / (32 - 20) * 100
s_pwat = (pwat - 30) / (90 - 30) * 100
s_v850 = (v850 - 0) / (40 - 0) * 100
s_theta = (theta_e - 310) / (360 - 310) * 100

hri = (0.2 * s_sst) + (0.3 * s_pwat) + (0.2 * s_v850) + (0.3 * s_theta)

# --- 5. 결과 시각화 ---
col1, col2 = st.columns([1, 2])

with col1:
    st.metric(label=f"{selected_city} 현재 HRI", value=f"{hri:.1f}")
    if hri >= 80: st.error("🚨 등급: 극한(Extreme)")
    elif hri >= 60: st.warning("⚠️ 등급: 경계(Warning)")
    else: st.success("✅ 등급: 보통(Normal)")

with col2:
    fig = go.Figure(go.Scatterpolar(
        r=[s_sst, s_pwat, s_v850, s_theta],
        theta=['SST', 'PWAT', 'V850', 'Theta-e'],
        fill='toself'
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])))
    st.plotly_chart(fig, use_container_width=True)