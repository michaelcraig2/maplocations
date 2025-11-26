
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
    colors = [f"#{random.randint(0, 0xFFFFFF):06x}" for _ in companies]
    color_map = dict(zip(companies, colors))

    center_lat = df['latitude'].mean()
    center_lon = df['longitude'].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=5)

    # Add individual markers (no clustering)
    for _, row in df.iterrows():
        company = row['Company Name']
        lat = row['latitude']
        lon = row['longitude']
        popup_info = f"<b>{company}</b><br>{row.get('Full Address (created)', '')}"
        folium.CircleMarker(
            location=[lat, lon],
            radius=6,
            color=color_map[company],
            fill=True,
            fill_color=color_map[company],
            popup=popup_info
        ).add_to(m)

    # Custom legend with text color
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

# Deployment instructions
st.write("### ✅ Deployment Instructions")
st.code("""
1. Save this script as app.py
2. Create requirements.txt with:
   streamlit
   pandas
   folium
   streamlit-folium
   openpyxl
3. Push to GitHub
4. Go to https://streamlit.io/cloud and deploy your app
""")

