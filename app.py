import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Space Mission Control", layout="wide")

st.title("🛰️ Space Mission Control Dashboard")

# ---------------- LOAD DATA ---------------- #
@st.cache_data
def load_data():
    url = "https://api.spacexdata.com/v4/starlink"
    data = requests.get(url).json()
    df = pd.json_normalize(data)
    return df

df = load_data()

# ---------------- SAFE COLUMN HANDLING ---------------- #
st.write("### 📦 Raw Columns Available")
st.write(df.columns)

# Safe mapping (only if exists)
rename_map = {
    "spaceTrack.OBJECT_NAME": "Name",
    "spaceTrack.ALTITUDE": "Altitude",
    "spaceTrack.INCLINATION": "Inclination",
    "spaceTrack.LONGITUDE": "Longitude",
    "spaceTrack.LAUNCH_DATE": "LaunchDate"
}

df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

# Keep only existing columns
required = [c for c in ["Name", "Altitude", "Inclination", "Longitude"] if c in df.columns]
df = df[required]

# ---------------- HANDLE EMPTY DATA SAFELY ---------------- #
if df.empty:
    st.error("No usable satellite tracking fields found in API response.")
    st.stop()

# Convert numeric safely
for col in ["Altitude", "Inclination"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna()

# ---------------- DASHBOARD UI ---------------- #
st.markdown("## 📡 Live Satellite Overview")

col1, col2, col3 = st.columns(3)

col1.metric("🛰️ Satellites", len(df))

if "Altitude" in df.columns:
    col2.metric("📍 Avg Altitude", f"{df['Altitude'].mean():.1f} km")

if "Inclination" in df.columns:
    col3.metric("🔭 Avg Inclination", f"{df['Inclination'].mean():.1f}°")

# ---------------- SIMPLE VISUAL (NO CRASH) ---------------- #
st.markdown("## 🌌 Satellite Snapshot")

st.dataframe(df.head(15), use_container_width=True)

# ---------------- ALTITUDE BARS ---------------- #
if "Altitude" in df.columns:
    st.markdown("## 🚀 Altitude Progress View")

    max_alt = df["Altitude"].max()

    for i in range(min(10, len(df))):
        name = df.iloc[i]["Name"] if "Name" in df.columns else f"Satellite {i}"
        alt = df.iloc[i]["Altitude"]

        progress = int((alt / max_alt) * 100)

        st.write(f"🛰️ {name}")
        st.progress(min(progress, 100))

st.success("🚀 Dashboard running without errors")
