import numpy as np
from sklearn.cluster import DBSCAN
import pandas as pd
import folium


url = "https://docs.google.com/spreadsheets/d/1pHg-lgImRUUAHPI8eXAPXVKCM5IDRqp6lhoZE0FLwgg/export?format=csv&gid=0"

df = pd.read_csv(url)

print(df.head())


# Remove rows where GPS or RSSI is missing
df = df.dropna(
    subset=["Latitude", "Longitude", "RSSI_dBm"]
)


# group nearby measurements
DISTANCE_THRESHOLD = 3  # meters

earth_radius = 6371000

grouped_data = []


for ssid, ssid_df in df.groupby("SSID"):

    coords = np.radians(
        ssid_df[["Latitude", "Longitude"]].values
    )

    db = DBSCAN(
        eps=DISTANCE_THRESHOLD / earth_radius,
        min_samples=1,
        metric="haversine"
    )

    labels = db.fit_predict(coords)

    ssid_df = ssid_df.copy()
    ssid_df["cluster"] = labels


    for cluster_id, cluster in ssid_df.groupby("cluster"):

        grouped_data.append({

            "Latitude": cluster["Latitude"].mean(),

            "Longitude": cluster["Longitude"].mean(),

            "SSID": ssid,

            "RSSI_dBm": cluster["RSSI_dBm"].median(),

            "Channel": cluster["Channel"].mode().iloc[0],

            "Encryption": cluster["Encryption"].mode().iloc[0],

            "SignalQuality": cluster["SignalQuality"].mode().iloc[0],

            "Altitude": cluster["Altitude"].mean(),

            "Measurements": len(cluster),

            "Timestamp": cluster["Timestamp"].iloc[0]
        })


df = pd.DataFrame(grouped_data)

# create map

center_lat = df["Latitude"].mean()
center_lon = df["Longitude"].mean()


m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=18,
    tiles="OpenStreetMap"
)


# determine point color based on RSSI value

def rssi_color(rssi):

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


# create a layer for each SSID

ssid_layers = {}


for ssid in sorted(df["SSID"].unique()):

    ssid_layers[ssid] = folium.FeatureGroup(
        name=ssid,
        show=True
    )

    ssid_layers[ssid].add_to(m)


# add measurement points

for _, row in df.iterrows():

    lat = row["Latitude"]
    lon = row["Longitude"]
    rssi = row["RSSI_dBm"]
    ssid = row["SSID"]

    # Information shown when clicking a point
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
        popup=folium.Popup(
            popup_text,
            max_width=300
        )
    ).add_to(ssid_layers[ssid])


# ssid filter control

folium.LayerControl(
    collapsed=False
).add_to(m)


# select all checkbox

select_all_html = """
<script>
document.addEventListener("DOMContentLoaded", function() {

    // Wait for Folium's layer control to appear
    setTimeout(function() {

        const layerControl = document.querySelector(
            '.leaflet-control-layers-list'
        );

        if (!layerControl) {
            return;
        }

        // Create Select All container
        const container = document.createElement("div");

        container.style.padding = "5px 0";
        container.style.borderBottom = "1px solid #ccc";
        container.style.marginBottom = "5px";

        // Create checkbox
        const checkbox = document.createElement("input");

        checkbox.type = "checkbox";
        checkbox.id = "select-all-ssid";
        checkbox.checked = true;

        // Create label
        const label = document.createElement("label");

        label.htmlFor = "select-all-ssid";
        label.innerText = " Select All";
        label.style.fontWeight = "bold";
        label.style.cursor = "pointer";

        container.appendChild(checkbox);
        container.appendChild(label);

        // Put it at the top of the layer list
        layerControl.insertBefore(
            container,
            layerControl.firstChild
        );


        // --------------------------------------------------
        // SELECT / DESELECT ALL
        // --------------------------------------------------

        checkbox.addEventListener("change", function() {

            const layerInputs = layerControl.querySelectorAll(
                'input[type="checkbox"]:not(#select-all-ssid)'
            );

            layerInputs.forEach(function(input) {

                if (input.checked !== checkbox.checked) {
                    input.click();
                }

            });

        });


        // --------------------------------------------------
        // UPDATE SELECT ALL STATE
        // --------------------------------------------------

        const layerInputs = layerControl.querySelectorAll(
            'input[type="checkbox"]:not(#select-all-ssid)'
        );

        layerInputs.forEach(function(input) {

            input.addEventListener("change", function() {

                const allSelected = Array.from(layerInputs)
                    .every(function(input) {
                        return input.checked;
                    });

                const noneSelected = Array.from(layerInputs)
                    .every(function(input) {
                        return !input.checked;
                    });

                checkbox.checked = allSelected;
                checkbox.indeterminate =
                    !allSelected && !noneSelected;

            });

        });

    }, 500);

});
</script>
"""

from branca.element import Element

m.get_root().html.add_child(
    Element(select_all_html)
)

m.save("wifi_points.html")

print("Map created successfully!")
print("Open wifi_points.html in your browser.")