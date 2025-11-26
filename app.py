
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import random

st.title("Interactive Map Generator")
st.write("Upload an Excel file with columns: Company Name, latitude, longitude")

uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])

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

        markers_js = "var allMarkers = [];\n"
        for _, row in df.iterrows():
            company = row['Company Name']
            lat = row['latitude']
            lon = row['longitude']
            marker = folium.CircleMarker(
                location=[lat, lon],
                radius=6,
                color=color_map[company],
                fill=True,
                fill_color=color_map[company],
                popup=f"{company}<br>{row.get('Full Address (created)', '')}"
            )
            marker.add_to(m)
            markers_js += f"allMarkers.push({{options: {{popup: '{company}'}}}});\n"

        legend_html = '<div style="position: fixed; bottom: 50px; left: 50px; width: 250px; background-color: white; border:2px solid grey; z-index:9999; font-size:14px; padding:10px;">'
        legend_html += '<b>Click Company to Highlight</b><br>'
        for company, color in color_map.items():
            legend_html += f'<div onclick="highlightMarkers(\\\"{company}\\\")" style="cursor:pointer;"><i style="background:{color};width:15px;height:15px;float:left;margin-right:8px;"></i>{company}</div>'
        legend_html += '</div>'

        js_script = f"""
        <script>
        {markers_js}
        function highlightMarkers(company) {{
            allMarkers.forEach(function(marker) {{
                if (marker.options.popup.includes(company)) {{
                    marker.setStyle({{radius: 10}});
                }} else {{
                    marker.setStyle({{radius: 4}});
                }}
            }});
        }}
        </script>
        """
        m.get_root().html.add_child(folium.Element(legend_html + js_script))

        st_folium(m, width=800, height=600)

st.write("### Deploy Instructions")
st.code("""
1. Save this script as app.py
2. Install dependencies:
   pip install streamlit pandas folium streamlit-folium openpyxl
3. Run locally:
   streamlit run app.py
4. Deploy online:
   - Push app.py to GitHub
   - Go to https://streamlit.io/cloud
   - Connect your repo and deploy
""")
