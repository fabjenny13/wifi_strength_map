from data import fetch_data, clean_data, cluster_by_ssid
from point_layers import build_ssid_layers, inject_select_all_script
import folium

df = cluster_by_ssid(clean_data(fetch_data()))
m = folium.Map(location=[df.Latitude.mean(), df.Longitude.mean()], zoom_start=18)
ssid_layers = build_ssid_layers(df, m)
folium.LayerControl(collapsed=False).add_to(m)
inject_select_all_script(m, ssid_layers)
m.save("test.html")