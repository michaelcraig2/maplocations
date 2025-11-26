
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import random

st.set_page_config(layout="wide")
st.title("Interactive Map Generator")

# Initialize session state
if "map" not in st.session_state:
    st.session_state["map"] = None

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    required_cols = ['Company Name', 'latitude', 'longitude']

    if not all(col in df.columns for col in required_cols):
        st.error(f"Excel file must contain columns: {required_cols}")
    else:
        df = df.dropna(subset=['latitude', 'longitude'])
        companies = df['Company Name'].unique()
        colors = [f"#{random.randint(0, 0xFFFFFF):06x}" for _ in companies]
        color_map = dict(zip(companies, colors))

        center_lat = df['latitude'].mean()
        center_lon = df['longitude'].mean()
        m = folium.Map(location=[center_lat, center_lon], zoom_start=5)

        # Add markers
        for _, row in df.iterrows():
            company = row['Company Name']
            lat = row['latitude']
            lon = row['longitude']
            folium.CircleMarker(
                location=[lat, lon],
                radius=6,
                color=color_map[company],
                fill=True,
                fill_color=color_map[company],
                popup=f"{company}<br>{row.get('Full Address (created)', '')}"
            ).add_to(m)

        # Add legend
        legend_html = '<div style="position: fixed; bottom: 50px; left: 50px; width: 250px; background-color: white; border:2px solid grey; z-index:9999; font-size:14px; padding:10px;">'
        legend_html += '<b>Company Legend</b><br>'
        for company, color in color_map.items():
            legend_html += f'<i style="background:{color};width:15px;height:15px;float:left;margin-right:8px;"></i>{company}<br>'
        legend_html += '</div>'
        m.get_root().html.add_child(folium.Element(legend_html))

        st.session_state["map"] = m

# Display map if available
if st.session_state["map"]:
    st_folium(st.session_state["map"], width=1000, height=600)
