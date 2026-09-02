# point_layers.py
import json
import folium
from branca.element import Element


def rssi_color(rssi: float) -> str:
    if rssi >= -50:
        return "green"
    elif rssi >= -60:
        return "lightgreen"
    elif rssi >= -70:
        return "orange"
    elif rssi >= -80:
        return "red"
    else:
        return "darkred"


def build_ssid_layers(df, m: folium.Map) -> dict:
    """Create one FeatureGroup per SSID, populated with markers, added to m."""
    ssid_layers = {}

    for ssid in sorted(df["SSID"].unique()):
        ssid_layers[ssid] = folium.FeatureGroup(name=ssid, show=True)
        ssid_layers[ssid].add_to(m)

    for _, row in df.iterrows():
        lat, lon, rssi, ssid = row["Latitude"], row["Longitude"], row["RSSI_dBm"], row["SSID"]

        popup_text = f"""
        <b>SSID:</b> {row["SSID"]}<br>
        <b>RSSI:</b> {rssi} dBm<br>
        <b>Channel:</b> {row["Channel"]}<br>
        <b>Encryption:</b> {row["Encryption"]}<br>
        <b>Signal Quality:</b> {row["SignalQuality"]}<br>
        <b>Latitude:</b> {lat}<br>
        <b>Longitude:</b> {lon}<br>
        <b>Altitude:</b> {row["Altitude"]} m<br>
        <b>Timestamp:</b> {row["Timestamp"]}
        """

        folium.CircleMarker(
            location=[lat, lon],
            radius=6,
            color="black",
            weight=1,
            fill=True,
            fill_color=rssi_color(rssi),
            fill_opacity=0.8,
            popup=folium.Popup(popup_text, max_width=300),
        ).add_to(ssid_layers[ssid])

    return ssid_layers


def inject_select_all_script(m: folium.Map, ssid_layers: dict) -> None:
    """Add the 'Select All' checkbox + wiring to directly toggle map layers."""
    map_var_name = m.get_name()
    sorted_ssids = sorted(ssid_layers.keys())
    layer_var_names = [ssid_layers[ssid].get_name() for ssid in sorted_ssids]
    layer_var_names_json = json.dumps(layer_var_names)

    select_all_html = f"""
    <script>
    document.addEventListener("DOMContentLoaded", function() {{
        setTimeout(function() {{
            const layerControl = document.querySelector('.leaflet-control-layers-list');
            if (!layerControl) return;

            const mapObj = window["{map_var_name}"];
            const layerVars = {layer_var_names_json};

            const container = document.createElement("div");
            container.style.padding = "5px 0";
            container.style.borderBottom = "1px solid #ccc";
            container.style.marginBottom = "5px";

            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.id = "select-all-ssid";
            checkbox.checked = true;

            const label = document.createElement("label");
            label.htmlFor = "select-all-ssid";
            label.innerText = " Select All";
            label.style.fontWeight = "bold";
            label.style.cursor = "pointer";

            container.appendChild(checkbox);
            container.appendChild(label);
            layerControl.insertBefore(container, layerControl.firstChild);

            const layerInputs = layerControl.querySelectorAll(
                'input[type="checkbox"]:not(#select-all-ssid)'
            );

            checkbox.addEventListener("change", function() {{
                layerInputs.forEach(function(input, idx) {{
                    const layer = window[layerVars[idx]];
                    if (!layer || !mapObj) return;

                    input.checked = checkbox.checked;

                    if (checkbox.checked) {{
                        if (!mapObj.hasLayer(layer)) mapObj.addLayer(layer);
                    }} else {{
                        if (mapObj.hasLayer(layer)) mapObj.removeLayer(layer);
                    }}
                }});
            }});

            layerInputs.forEach(function(input) {{
                input.addEventListener("change", function() {{
                    const allSelected = Array.from(layerInputs).every((i) => i.checked);
                    const noneSelected = Array.from(layerInputs).every((i) => !i.checked);
                    checkbox.checked = allSelected;
                    checkbox.indeterminate = !allSelected && !noneSelected;
                }});
            }});

        }}, 500);
    }});
    </script>
    """

    m.get_root().html.add_child(Element(select_all_html))