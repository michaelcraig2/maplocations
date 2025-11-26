
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import random

st.set_page_config(layout="wide")
st.title("📍 Interactive Map Generator")
st.write("Upload an Excel file with columns: **Company Name**, **latitude**, **longitude**")

# Cache map generation
@st.cache_data
def generate_map(df):
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

    # Create FeatureGroups for each company
    for company in companies:
        fg = folium.FeatureGroup(name=company)
        company_data = df[df['Company Name'] == company]
        for _, row in company_data.iterrows():
            popup_info = f"<b>{company}</b><br>{row.get('Full Address (created)', '')}"
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=6,
                color=color_map[company],
                fill=True,
                fill_color=color_map[company],
                popup=popup_info
            ).add_to(fg)
        fg.add_to(m)

    # Add Layer Control
    folium.LayerControl().add_to(m)

    # Add legend for color reference
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; width: 250px; 
    background-color: white; border:2px solid grey; z-index:9999; font-size:14px; 
    padding:10px; color:#333333;">
    <b style="color:#0000FF;">Company Legend</b><br>
    '''
    for company, color in color_map.items():
        legend_html += f'<i style="background:{color};width:15px;height:15px;float:left;margin-right:8px;"></i><span style="color:#000000;">{company}</span><br>'
    legend_html += '</div>'
    m.get_root().html.add_child(folium.Element(legend_html))

    return m

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    required_cols = ['Company Name', 'latitude', 'longitude']

    if not all(col in df.columns for col in required_cols):
        st.error(f"Excel file must contain columns: {required_cols}")
    else:
        df = df.dropna(subset=['latitude', 'longitude'])
        st.session_state["map"] = generate_map(df)

if "map" in st.session_state:
    st_folium(st.session_state["map"], width=1700, height=900)

# Search/filter feature
if uploaded_file:
    st.subheader("🔍 Filter by Company")
    selected_company = st.selectbox("Choose a company", options=["All"] + list(df['Company Name'].unique()))
    if selected_company != "All":
        filtered_df = df[df['Company Name'] == selected_company]
        st.write(f"Showing {len(filtered_df)} locations for **{selected_company}**")
        st.dataframe(filtered_df[['Company Name', 'Full Address (created)', 'latitude', 'longitude']])


