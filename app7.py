@st.cache_data
def generate_map(df, use_clusters: bool, show_legend: bool):
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
            popup_info = f"&lt;b&gt;{row['Company Name']}&lt;/b&gt;&lt;br&gt;{row['Full Address']}"
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
                popup_info = f"&lt;b&gt;{company}&lt;/b&gt;&lt;br&gt;{row['Full Address']}"
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

    if show_legend:
        legend_html = (
            '&lt;div style="position: fixed; bottom: 50px; left: 50px; width: 250px; '
            'background-color: white; border:2px solid grey; z-index:9999; color:#000000; '
            'font-size:14px; padding:10px;"&gt;'
        )
        legend_html += '&lt;b style="color:#0000FF;"&gt;Company Legend&lt;/b&gt;&lt;br&gt;'
        for company, color in color_map.items():
            legend_html += (
                f'&lt;i style="background:{color};width:15px;height:15px;'
                f'float:left;margin-right:8px;"&gt;&lt;/i&gt;{company}&lt;br&gt;'
            )
        legend_html += '&lt;/div&gt;'
        m.get_root().html.add_child(folium.Element(legend_html))

    return m
