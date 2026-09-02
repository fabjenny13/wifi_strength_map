# controls.py
import json
from branca.element import Element
import folium


def inject_view_toggle(m: folium.Map, ssid_layers: dict, heat_layer: folium.FeatureGroup) -> None:
    """
    Add a Point Map / Heatmap toggle control (top-left, below zoom).
    Switching to Heatmap hides all SSID layers + the layer control panel.
    Switching back restores each SSID layer per its checkbox's last state.
    """
    map_var_name = m.get_name()
    heat_var_name = heat_layer.get_name()
    sorted_ssids = sorted(ssid_layers.keys())
    ssid_layer_vars_json = json.dumps([ssid_layers[s].get_name() for s in sorted_ssids])

    toggle_html = f"""
    <script>
    document.addEventListener("DOMContentLoaded", function() {{
        setTimeout(function() {{
            const mapObj = window["{map_var_name}"];
            const heatLayer = window["{heat_var_name}"];
            const ssidLayerVars = {ssid_layer_vars_json};

            if (mapObj.hasLayer(heatLayer)) mapObj.removeLayer(heatLayer);

            const layerControlContainer = document.querySelector('.leaflet-control-layers');

            const ViewToggle = L.Control.extend({{
                options: {{ position: 'topleft' }},
                onAdd: function() {{
                    const container = L.DomUtil.create('div', 'leaflet-bar view-toggle-control');
                    container.style.background = 'white';
                    container.style.padding = '4px';

                    const pointBtn = L.DomUtil.create('a', 'view-toggle-btn active', container);
                    pointBtn.innerHTML = 'Point Map';
                    pointBtn.href = '#';

                    const heatBtn = L.DomUtil.create('a', 'view-toggle-btn', container);
                    heatBtn.innerHTML = 'Heatmap';
                    heatBtn.href = '#';

                    L.DomEvent.disableClickPropagation(container);

                    L.DomEvent.on(pointBtn, 'click', function(e) {{
                        L.DomEvent.preventDefault(e);
                        if (mapObj.hasLayer(heatLayer)) mapObj.removeLayer(heatLayer);

                        const checkboxes = document.querySelectorAll(
                            '.leaflet-control-layers-overlays input[type="checkbox"]'
                        );
                        checkboxes.forEach(function(cb, idx) {{
                            const layer = window[ssidLayerVars[idx]];
                            if (!layer) return;
                            if (cb.checked && !mapObj.hasLayer(layer)) mapObj.addLayer(layer);
                        }});

                        if (layerControlContainer) layerControlContainer.style.display = '';
                        pointBtn.classList.add('active');
                        heatBtn.classList.remove('active');
                    }});

                    L.DomEvent.on(heatBtn, 'click', function(e) {{
                        L.DomEvent.preventDefault(e);
                        ssidLayerVars.forEach(function(varName) {{
                            const layer = window[varName];
                            if (layer && mapObj.hasLayer(layer)) mapObj.removeLayer(layer);
                        }});
                        if (!mapObj.hasLayer(heatLayer)) mapObj.addLayer(heatLayer);

                        if (layerControlContainer) layerControlContainer.style.display = 'none';
                        heatBtn.classList.add('active');
                        pointBtn.classList.remove('active');
                    }});

                    return container;
                }}
            }});

            mapObj.addControl(new ViewToggle());

        }}, 500);
    }});
    </script>
<style>
.view-toggle-control {{
    width: auto !important;
}}
.view-toggle-btn {{
    display: block;
    width: auto !important;
    height: auto !important;
    line-height: normal !important;
    padding: 6px 12px;
    text-decoration: none;
    color: #333;
    font-size: 13px;
    white-space: nowrap;
}}
.view-toggle-btn.active {{
    background: #e6e6e6;
    font-weight: bold;
}}
</style>
    """

    m.get_root().html.add_child(Element(toggle_html))