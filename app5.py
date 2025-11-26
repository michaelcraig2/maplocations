
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
import random

st.set_page_config(layout="wide")
st.title("📍 Interactive Map Generator with Geocoding & Clustering Toggle")
st.write("Upload an Excel file with columns: **Company Name** (A) and **Full Address (created)** (F).")

# Google Maps API Key
API_KEY = "YOUR_GOOGLE_MAPS_API_KEY"
GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"

def get_lat_lng(address):
    params = {'address': address, 'key': API_KEY}
    response = requests.get(GEOCODE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
    return None, None

@st.cache_data
def generate_map(df, use_clusters):
    companies = df['Company Name'].unique()
    vibrant_colors = [
        "#FF0000", "#00FF00", "#0000FF", "#FFA500", "#800080",
        "#008080", "#FF1493", "#FFD700", "#00CED1", "#DC143C"
    ]
    colors = [vibrant_colors[i % len(vibrant_colors)] for i in range(len(companies))]
    color_map = dict(zip(companies, colors))

    center_lat = df['latitude'].mean()
    center_lon = df['longitude'].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=5)

    if use_clusters:
        from folium.plugins import MarkerCluster
        marker_cluster = MarkerCluster().add_to(m)
        for _, row in df.iterrows():
            popup_info = f"<b>{row['Company Name']}</b><br>{row['Full Address (created)']}"
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=6,
                color=color_map[row['Company Name']],
                fill=True,
                fill_color=color_map[row['Company Name']],
                popup=popup_info
            ).add_to(marker_cluster)
    else:
        for company in companies:
            fg = folium.FeatureGroup(name=company)
            company_data = df[df['Company Name'] == company]
            for _, row in company_data.iterrows():
                popup_info = f"<b>{company}</b><br>{row['Full Address (created)']}"
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=6,
                    color=color_map[company],
                    fill=True,
                    fill_color=color_map[company],
                    popup=popup_info
                ).add_to(fg)
            fg.add_to(m)
        folium.LayerControl().add_to(m)

    legend_html = '<div style="position: fixed; bottom: 50px; left: 50px; width: 250px; background-color: white; border:2px solid grey; z-index:9999; font-size:14px; color:#000000; padding:10px;">'
    legend_html += '<b style="color:#0000FF;">Company Legend</b><br>'
    for company, color in color_map.items():
        legend_html += f'<i style="background:{color};width:15px;height:15px;float:left;margin-right:8px;"></i>{company}<br>'
    legend_html += '</div>'
    m.get_root().html.add_child(folium.Element(legend_html))

    return m

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
use_clusters = st.checkbox("Enable Marker Clustering", value=False)

if uploaded_file:
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    required_cols = ['Company Name', 'Full Address (created)']

    if not all(col in df.columns for col in required_cols):
        st.error(f"Excel file must contain columns: {required_cols}")
    else:
        if 'latitude' not in df.columns:
            df['latitude'] = None
        if 'longitude' not in df.columns:
            df['longitude'] = None

        st.write("Geocoding addresses... This may take a few minutes.")
        for idx, row in df.iterrows():
            if pd.isna(row['latitude']) or pd.isna(row['longitude']):
                lat, lng = get_lat_lng(row['Full Address (created)'])
                if lat and lng:
                    df.at[idx, 'latitude'] = lat
                    df.at[idx, 'longitude'] = lng

        st.success("Geocoding complete! Generating map...")
        st.session_state["map"] = generate_map(df, use_clusters)

if "map" in st.session_state:
    st_folium(st.session_state["map"], width=1700, height=900)

