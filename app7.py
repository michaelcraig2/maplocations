import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
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

def generate_map(df, use_clusters, show_legend):
    # Keep company list for layer groups (unchanged behavior)
    companies = df['Company Name'].unique()

    # --- NEW: build colors per Status (not per Company) ---
    # Gather Statuss present in this file; put 'Unknown' last for a cleaner legend
    Statuss = sorted([p for p in df['Status'].dropna().unique() if p != 'Unknown'])
    if 'Unknown' in df['Status'].values:
        Statuss.append('Unknown')

    # Color palette (enough distinct colors; will cycle if there are many Statuss)
    vibrant_colors = [
        "#FF0000", "#00A65A", "#1F77B4", "#FFA500", "#800080",
        "#008080", "#FF1493", "#FFD700", "#00CED1", "#DC143C",
        "#17BECF", "#9467BD", "#2CA02C", "#E377C2", "#7F7F7F"
    ]
    Status_colors = {Status: vibrant_colors[i % len(vibrant_colors)] for i, Status in enumerate(Statuss)}
    default_color = "#7F7F7F"

    # Map center (unchanged)
    center_lat = df['latitude'].dropna().mean() if not df['latitude'].dropna().empty else 39.8283
    center_lon = df['longitude'].dropna().mean() if not df['longitude'].dropna().empty else -98.5795
    m = folium.Map(location=[center_lat, center_lon], zoom_start=5)

    # Only plot rows with coordinates (unchanged)
    valid_rows = df.dropna(subset=['latitude', 'longitude'])

    if use_clusters:
        # --- Cluster mode: same behavior, now colored by Status ---
        from folium.plugins import MarkerCluster
        marker_cluster = MarkerCluster().add_to(m)
        for _, row in valid_rows.iterrows():
            Status = row.get('Status', 'Unknown')
            color = Status_colors.get(Status, default_color)
            
            popup_info = (
                f"<div style='font-size:10pt;'>"
                f"<b>{row['Company Name']}</b><br>"
                f"<a href='{row['CRM Link']}' target='_blank'>CRM Link</a>"
                f"</div>"
            )

            # popup_info = f"<b>{row['Company Name']}</b><br>{row['CRM Link']}"
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=6,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.9,
                popup=popup_info
            ).add_to(marker_cluster)
    else:
        # --- Non-cluster mode: keep per-company FeatureGroups (unchanged), colored by Status ---
        for company in companies:
            fg = folium.FeatureGroup(name=company)
            company_data = valid_rows[valid_rows['Company Name'] == company]
            for _, row in company_data.iterrows():
                Status = row.get('Status', 'Unknown')
                color = Status_colors.get(Status, default_color)
                
                #popup_info = (
                #    f"<div style='font-size:10pt;'>"
                #    f"<b>{row['Company Name']}</b><br>"
                #    f"<a href='{row['CRM Link']}' target='_blank'>CRM Link</a>"
                #    f"</div>"
                #)

                from urllib.parse import quote_plus
                
                address = row['Full Address']  # e.g., "123 Main St, Minneapolis, MN 55401"
                gmaps_url = f"https://www.google.com/maps/search/?api=1&query={quote_plus(address)}"
                
                popup_info = (
                    f"<div style='font-size:10pt;'>"
                    f"<b>{row['Company Name']}</b><br>"
                    f"<a href='{row['CRM Link']}' target='_blank' rel='noopener'>CRM Link</a><br>"
                    f"<a href='{gmaps_url}' target='_blank' rel='noopener'>{address}</a>"
                    f"</div>"
                )
                
                #popup_info = f"<b>{company}"
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=6,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.2,
                    popup=popup_info
                ).add_to(fg)
            fg.add_to(m)
        folium.LayerControl().add_to(m)

    # --- NEW: Status legend (replaces company legend) ---
    if show_legend:
        legend_items = ""
        for Status in Statuss:
            color = Status_colors.get(Status, default_color)
            legend_items += (
                f'<div style="display:flex;align-items:center;margin-bottom:4px;">'
                f'  <span style="display:inline-block;width:12px;height:12px;'
                f'             background:{color};border:1px solid #333;'
                f'             margin-right:8px;"></span>'
                f'  <span style="font-size:12px;">{Status}</span>'
                f'</div>'
            )

        legend_html = f"""
        <div style="
            position: fixed;
            bottom: 50px;
            left: 50px;
            z-index: 9999;
            background: white;
            border: 1px solid #bbb;
            border-radius: 6px;
            padding: 10px 12px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.3);
            color: #000;
            font-size: 14px;
        ">
            <div style="font-weight:600;margin-bottom:6px;">Status Legend</div>
            {legend_items}
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend_html))
    else:
        st.write("IF YOU ALREADY CREATED A MAP WITH A LEGEND, YOU'LL NEED TO RELOAD THE ENTIRE PAGE TO REMOVE THE LEGEND")

    return m


uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
use_clusters = st.checkbox("Enable Marker Clustering", value=False)
show_legend = st.checkbox("Show Company Legend", value=True)

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
        m = generate_map(df, use_clusters, show_legend)
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

        
        # Generate HTML content as string
        html_content = m.get_root().render()
        
        # Download map as HTML
        st.download_button(
            label="Download Map as HTML",
            data=html_content,
            file_name="interactive_map.html",
            mime="text/html"
        )

       
if "map" in st.session_state:
    st_folium(st.session_state["map"], width=1700, height=900)

st.write("### ✅ Important Information")
st.code("""
Notes:  
   - You can turn on/off clustering of locations with the check box above the map
   - You can use the layer button in the top right area of the map to turn on/off different company locations
   - You can download your original excel file with latitude and longitude now added
   - You can download the HTML of your map and share it
""")
