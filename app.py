import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="Space Tracker", layout="wide")

st.title("🛰️ Real-Time Space Objects Tracker Dashboard")
st.write("Live tracking of satellites (Starlink dataset) from public API")

# Fetch live data
@st.cache_data
def load_data():
    url = "https://api.spacexdata.com/v4/starlink"
    response = requests.get(url)
    data = response.json()
    return pd.json_normalize(data)

df = load_data()

# Clean important columns
df = df[[
    "spaceTrack.OBJECT_NAME",
    "spaceTrack.LAUNCH_DATE",
    "spaceTrack.INCLINATION",
    "spaceTrack.LONGITUDE",
    "spaceTrack.ALTITUDE"
]].dropna()

df.columns = ["Name", "Launch Date", "Inclination", "Longitude", "Altitude"]

st.sidebar.header("🔍 Filters")

# Filter by altitude range
alt_range = st.sidebar.slider(
    "Select Altitude Range (km)",
    int(df["Altitude"].min()),
    int(df["Altitude"].max()),
    (300, 600)
)

filtered_df = df[
    (df["Altitude"] >= alt_range[0]) &
    (df["Altitude"] <= alt_range[1])
]

# Show raw data
if st.checkbox("Show raw satellite data"):
    st.dataframe(filtered_df)

# 🌍 Satellite altitude distribution
st.subheader("📊 Satellite Altitude Distribution")

fig1 = px.histogram(
    filtered_df,
    x="Altitude",
    nbins=30,
    title="Altitude Distribution of Satellites"
)

st.plotly_chart(fig1, use_container_width=True)

# 🛰️ Orbital inclination vs altitude
st.subheader("🛰️ Orbit Patterns")

fig2 = px.scatter(
    filtered_df,
    x="Inclination",
    y="Altitude",
    hover_data=["Name"],
    title="Inclination vs Altitude (Orbital Map)"
)

st.plotly_chart(fig2, use_container_width=True)

# 🌐 Satellite positions (simplified world view)
st.subheader("🌍 Satellite Longitude Distribution")

fig3 = px.scatter_geo(
    filtered_df,
    lon="Longitude",
    lat="Inclination",
    hover_name="Name",
    title="Satellite Distribution in Space View",
    projection="natural earth"
)

st.plotly_chart(fig3, use_container_width=True)

st.success("Live Space Tracker Running 🚀")