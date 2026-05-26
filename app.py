import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="Space Tracker", layout="wide")

st.title("🛰️ Real-Time Space Objects Tracker Dashboard")
st.write("Live Starlink satellite data from SpaceX API")

@st.cache_data
def load_data():
    url = "https://api.spacexdata.com/v4/starlink"
    response = requests.get(url)
    data = response.json()
    df = pd.json_normalize(data)
    return df

df = load_data()

# ✅ Check available columns (IMPORTANT FIX)
st.write("Available columns:", df.columns)

# Keep only existing safe columns
cols = []

if "spaceTrack.OBJECT_NAME" in df.columns:
    cols.append("spaceTrack.OBJECT_NAME")

if "spaceTrack.LAUNCH_DATE" in df.columns:
    cols.append("spaceTrack.LAUNCH_DATE")

if "spaceTrack.INCLINATION" in df.columns:
    cols.append("spaceTrack.INCLINATION")

if "spaceTrack.LONGITUDE" in df.columns:
    cols.append("spaceTrack.LONGITUDE")

if "spaceTrack.ALTITUDE" in df.columns:
    cols.append("spaceTrack.ALTITUDE")

# If API structure changes, fallback
if len(cols) == 0:
    st.error("API structure changed. Showing raw data instead.")
    st.dataframe(df)
    st.stop()

df = df[cols].dropna()

# Rename safely
rename_map = {
    "spaceTrack.OBJECT_NAME": "Name",
    "spaceTrack.LAUNCH_DATE": "Launch Date",
    "spaceTrack.INCLINATION": "Inclination",
    "spaceTrack.LONGITUDE": "Longitude",
    "spaceTrack.ALTITUDE": "Altitude",
}

df = df.rename(columns=rename_map)

st.sidebar.header("Filters")

if "Altitude" in df.columns:
    alt_range = st.sidebar.slider(
        "Altitude Range",
        int(df["Altitude"].min()),
        int(df["Altitude"].max()),
        (300, 600)
    )

    df = df[(df["Altitude"] >= alt_range[0]) & (df["Altitude"] <= alt_range[1])]

st.subheader("📊 Satellite Altitude Distribution")

if "Altitude" in df.columns:
    fig1 = px.histogram(df, x="Altitude", nbins=30)
    st.plotly_chart(fig1, use_container_width=True)

st.subheader("🛰️ Orbit Analysis")

if "Inclination" in df.columns and "Altitude" in df.columns:
    fig2 = px.scatter(df, x="Inclination", y="Altitude")
    st.plotly_chart(fig2, use_container_width=True)

st.success("Dashboard running successfully 🚀")
