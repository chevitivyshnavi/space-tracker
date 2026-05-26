import streamlit as st
import pandas as pd
import requests
import numpy as np

st.set_page_config(page_title="Space Mission Control", layout="wide")

st.title("🛰️ SPACE MISSION CONTROL DASHBOARD")
st.write("Live Starlink satellite tracking system")

# ---------------- LOAD DATA ---------------- #
@st.cache_data
def load_data():
    url = "https://api.spacexdata.com/v4/starlink"
    data = requests.get(url).json()
    df = pd.json_normalize(data)
    return df

df = load_data()

# ---------------- CLEAN ---------------- #
df = df.rename(columns={
    "spaceTrack.OBJECT_NAME": "Name",
    "spaceTrack.ALTITUDE": "Altitude",
    "spaceTrack.INCLINATION": "Inclination",
    "spaceTrack.LONGITUDE": "Longitude",
    "spaceTrack.LAUNCH_DATE": "Launch Date"
})

df = df.dropna(subset=["Altitude", "Inclination"])

# ---------------- SIDEBAR ---------------- #
st.sidebar.header("🛰️ Mission Controls")

alt_min, alt_max = int(df["Altitude"].min()), int(df["Altitude"].max())

alt_range = st.sidebar.slider(
    "Altitude Range (km)",
    alt_min,
    alt_max,
    (alt_min, alt_max)
)

df = df[(df["Altitude"] >= alt_range[0]) & (df["Altitude"] <= alt_range[1])]

# ---------------- KPI CARDS ---------------- #
st.markdown("## 📡 LIVE SATELLITE STATUS")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("### 🛰️ Total Objects")
    st.markdown(f"## {len(df)}")

with col2:
    st.markdown("### 📍 Avg Altitude")
    st.markdown(f"## {df['Altitude'].mean():.1f} km")

with col3:
    st.markdown("### 🔭 Avg Inclination")
    st.markdown(f"## {df['Inclination'].mean():.1f}°")

with col4:
    max_alt = df["Altitude"].max()
    st.markdown("### 🚀 Max Altitude")
    st.markdown(f"## {max_alt:.1f} km")

# ---------------- VISUAL: ALTITUDE BARS ---------------- #
st.markdown("## 🌌 Satellite Altitude Status")

for i in range(0, min(10, len(df))):
    name = df.iloc[i]["Name"] if "Name" in df.columns else f"Satellite {i}"
    alt = df.iloc[i]["Altitude"]

    progress = int((alt / df["Altitude"].max()) * 100)

    st.write(f"🛰️ **{name}**  | Altitude: {alt:.2f} km")
    st.progress(min(progress, 100))

# ---------------- VISUAL GRID (CLEAN VIEW) ---------------- #
st.markdown("## 🧭 Orbital Intelligence Grid")

grid_df = df.head(12)

cols = st.columns(3)

for i, row in enumerate(grid_df.itertuples()):
    with cols[i % 3]:
        st.markdown(
            f"""
            ### 🛰️ {row.Name if hasattr(row, 'Name') else 'Unknown'}

            📍 Altitude: **{row.Altitude:.1f} km**  
            🔭 Inclination: **{row.Inclination:.1f}°**  
            🌐 Longitude: **{getattr(row, 'Longitude', 'N/A')}**

            ---
            """
        )

# ---------------- SPACE HEALTH INDICATOR ---------------- #
st.markdown("## 🧠 System Health Indicator")

avg_alt = df["Altitude"].mean()

if avg_alt < 400:
    st.success("🟢 Low Orbit Stability - Normal Operations")
elif avg_alt < 550:
    st.warning("🟡 Medium Orbit Density - Monitor Traffic")
else:
    st.error("🔴 High Orbit Congestion - Risk Zone")

# ---------------- OPTIONAL RAW DATA ---------------- #
with st.expander("📦 View Raw Satellite Data"):
    st.dataframe(df)

st.success("🚀 Mission Control Dashboard Active")
