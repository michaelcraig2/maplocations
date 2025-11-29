
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
import random
from io import BytesIO

st.set_page_config(layout="wide")
st.title("📍 Interactive Map Generator with Geocoding & Clustering Toggle")
st.write("Upload an Excel file with columns: **Company Name** and **Full Address**.")

API_KEY = "AIzaSyDyr9TM2ovLL8ncZWywcZYwnAHkVHm7-Lk"
GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"

def get_lat_lng(address):
    try:
        params = {'address': address, 'key': API_KEY}
        response = requests.get(GEOCODE_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'OK':
                location = data['results'][0]['geometry']['location']
                return location['lat'], location['lng']
    except Exception:
        return None, None
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

    center_lat = df['latitude'].dropna().mean() if not df['latitude'].dropna().empty else 39.8283
    center_lon = df['longitude'].dropna().mean() if not df['longitude'].dropna().empty else -98.5795
    m = folium.Map(location=[center_lat, center_lon], zoom_start=5)

    valid_rows = df.dropna(subset=['latitude', 'longitude'])

    if use_clusters:
        from folium.plugins import MarkerCluster
        marker_cluster = MarkerCluster().add_to(m)
        for _, row in valid_rows.iterrows():
            popup_info = f"<b>{row['Company Name']}</b><br>{row['Full Address']}"
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
            company_data = valid_rows[valid_rows['Company Name'] == company]
            for _, row in company_data.iterrows():
                popup_info = f"<b>{company}</b><br>{row['Full Address']}"
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

    legend_html = '<div style="position: fixed; bottom: 50px; left: 50px; width: 250px; background-color: white; border:2px solid grey; z-index:9999; font-size:14px; padding:10px;">'
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
    required_cols = ['Company Name', 'Full Address']

    if not all(col in df.columns for col in required_cols):
        st.error(f"Excel file must contain columns: {required_cols}")
    else:
        if 'latitude' not in df.columns:
            df['latitude'] = None
        if 'longitude' not in df.columns:
            df['longitude'] = None

        st.write("Geocoding addresses... This may take a few minutes.")
        progress_bar = st.progress(0)
        total_rows = len(df)

        for idx, row in df.iterrows():
            if pd.isna(row['latitude']) or pd.isna(row['longitude']):
                lat, lng = get_lat_lng(row['Full Address'])
                if lat and lng:
                    df.at[idx, 'latitude'] = lat
                    df.at[idx, 'longitude'] = lng
            progress_bar.progress((idx + 1) / total_rows)

        missing_count = df[['latitude', 'longitude']].isna().any(axis=1).sum()
        if missing_count > 0:
            st.warning(f"{missing_count} addresses could not be geocoded and will not appear on the map.")

        st.success("Geocoding complete! Generating map...")
        m = generate_map(df, use_clusters)
        st.session_state["map"] = m

        # Download updated Excel file
        output_excel = BytesIO()
        df.to_excel(output_excel, index=False)
        st.download_button(
            label="Download Updated Excel",
            data=output_excel.getvalue(),
            file_name="updated_locations.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Download map as HTML
        output_html = BytesIO()
        m.save(output_html)
        output_html.seek(0)  # Reset pointer
        st.download_button(
            label="Download Map as HTML",
            data=output_html.getvalue(),
            file_name="interactive_map.html",
            mime="text/html"
        )

if "map" in st.session_state:
    st_folium(st.session_state["map"], width=1700, height=900)

st.write("### ✅ Deployment Instructions")
st.code("""
1. Save this script as app.py
2. Create requirements.txt with:
   streamlit
   pandas
   folium
   streamlit-folium
   openpyxl
   requests
3. Replace YOUR_GOOGLE_MAPS_API_KEY with your actual key
4. Push to GitHub
5. Deploy on https://streamlit.io/cloud
""")
