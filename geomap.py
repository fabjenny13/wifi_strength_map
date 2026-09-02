import numpy as np
from sklearn.cluster import DBSCAN
import pandas as pd
import folium
from ssid_filter import filter_by_ssid


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

# Select SSIDs to display
selected_ssids = [
    "vivo T2x 5G",
    "pupu"
]

df = filter_by_ssid(df, selected_ssids)

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


# add measurement points

for _, row in df.iterrows():

    lat = row["Latitude"]
    lon = row["Longitude"]
    rssi = row["RSSI_dBm"]

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
    ).add_to(m)


m.save("wifi_points.html")

print("Map created successfully!")
print("Open wifi_points.html in your browser.")