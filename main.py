# main.py
import folium

from data import fetch_data, clean_data, cluster_by_ssid
from point_layers import build_ssid_layers, inject_select_all_script
from heat_layer import build_heat_layer
from controls import inject_view_toggle


def main():
    raw_df = fetch_data()
    df = clean_data(raw_df)

    clustered_df = cluster_by_ssid(df)   # for point markers
    heatmap_df = df                       # raw, unclustered — per earlier decision

    center_lat = clustered_df["Latitude"].mean()
    center_lon = clustered_df["Longitude"].mean()

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=18,
        tiles="OpenStreetMap",
    )

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri, Maxar, Earthstar Geographics",
        name="Satellite",
        overlay=False,
        control=True,
    ).add_to(m)

    # Point map layers (one FeatureGroup per SSID)
    ssid_layers = build_ssid_layers(clustered_df, m)

    # Heatmap layer (hidden by default)
    heat_layer = build_heat_layer(heatmap_df)
    heat_layer.add_to(m)

    # Layer control (SSID checkboxes)
    folium.LayerControl(collapsed=False).add_to(m)

    # Select-all checkbox wiring
    inject_select_all_script(m, ssid_layers)

    # Point Map / Heatmap toggle
    inject_view_toggle(m, ssid_layers, heat_layer)

    m.save("wifi_map.html")
    print("Map created successfully!")
    print("Open wifi_map.html in your browser.")


if __name__ == "__main__":
    main()