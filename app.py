import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="Space Tracker", layout="wide")

st.title("🛰️ Real-Time Space Objects Tracker Dashboard")
st.write("Live Starlink satellite data from SpaceX API")

# ---------------- LOAD DATA ---------------- #
@st.cache_data
def load_data():
    url = "https://api.spacexdata.com/v4/starlink"
    response = requests.get(url)
    data = response.json()
    df = pd.json_normalize(data)
    return df

df = load_data()

st.write("### 📦 Dataset Preview")
st.dataframe(df.head())

# ---------------- COLUMN CLEANING ---------------- #
cols_map = {
    "spaceTrack.OBJECT_NAME": "Name",
    "spaceTrack.LAUNCH_DATE": "Launch Date",
    "spaceTrack.INCLINATION": "Inclination",
    "spaceTrack.LONGITUDE": "Longitude",
    "spaceTrack.ALTITUDE": "Altitude",
}

df = df.rename(columns=cols_map)

available_cols = [c for c in cols_map.values() if c in df.columns]
df = df[available_cols].dropna()

# ---------------- SIDEBAR FILTER ---------------- #
st.sidebar.header("🔍 Filters")

if "Altitude" in df.columns:
    min_alt = int(df["Altitude"].min())
    max_alt = int(df["Altitude"].max())

    alt_range = st.sidebar.slider(
        "Altitude Range (km)",
        min_alt,
        max_alt,
        (min_alt, max_alt)
    )

    df = df[(df["Altitude"] >= alt_range[0]) & (df["Altitude"] <= alt_range[1])]

# ---------------- KPI METRICS ---------------- #
st.subheader("📊 Key Metrics")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Satellites", len(df))

with col2:
    if "Altitude" in df.columns:
        st.metric("Avg Altitude", f"{df['Altitude'].mean():.2f} km")

with col3:
    if "Inclination" in df.columns:
        st.metric("Avg Inclination", f"{df['Inclination'].mean():.2f}°")

# ---------------- VISUAL 1 ---------------- #
st.subheader("📊 Altitude Distribution (Density View)")

if "Altitude" in df.columns:
    fig1 = px.histogram(
        df,
        x="Altitude",
        nbins=40,
        color_discrete_sequence=["#00BFFF"],
        title="Satellite Altitude Distribution"
    )
    fig1.update_layout(bargap=0.1)
    st.plotly_chart(fig1, use_container_width=True)

# ---------------- VISUAL 2 ---------------- #
st.subheader("🛰️ Orbital Structure Map")

if "Inclination" in df.columns and "Altitude" in df.columns:
    fig2 = px.scatter(
        df,
        x="Inclination",
        y="Altitude",
        color="Altitude",
        color_continuous_scale="Viridis",
        size_max=10,
        title="Inclination vs Altitude (Orbital Pattern)"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---------------- VISUAL 3 ---------------- #
st.subheader("🌌 Space Object Heat View")

if "Longitude" in df.columns and "Altitude" in df.columns:
    fig3 = px.density_heatmap(
        df,
        x="Longitude",
        y="Altitude",
        color_continuous_scale="Turbo",
        title="Spatial Density of Satellites"
    )
    st.plotly_chart(fig3, use_container_width=True)

# ---------------- RAW DATA ---------------- #
if st.checkbox("Show raw data"):
    st.dataframe(df)

st.success("🚀 Aesthetic Space Dashboard Loaded Successfully")
