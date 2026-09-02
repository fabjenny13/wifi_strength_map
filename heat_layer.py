# heat_layer.py
import numpy as np
import folium
from folium.plugins import HeatMap

# Typical WiFi RSSI range for normalization
RSSI_MIN = -90  # weakest signal we care about
RSSI_MAX = -30  # strongest realistic signal


def normalize_rssi(rssi: float) -> float:
    """Map RSSI (dBm) to a 0-1 weight, clipped to [RSSI_MIN, RSSI_MAX]."""
    clipped = np.clip(rssi, RSSI_MIN, RSSI_MAX)
    return (clipped - RSSI_MIN) / (RSSI_MAX - RSSI_MIN)


def build_heat_layer(df, name: str = "Signal Heatmap") -> folium.FeatureGroup:
    """
    Build a HeatMap layer wrapped in a FeatureGroup so it behaves like
    the other toggleable layers (has .get_name(), can be add/removed).

    Expects raw (unclustered) rows — don't feed this the DBSCAN-clustered
    output from cluster_by_ssid, since averaging nearby points throws away
    the density signal a heatmap is meant to show.
    """
    heat_points = [
        [row["Latitude"], row["Longitude"], normalize_rssi(row["RSSI_dBm"])]
        for _, row in df.iterrows()
    ]

    heat_group = folium.FeatureGroup(name=name, show=False)

    HeatMap(
        heat_points,
        radius=18,
        blur=22,
        max_zoom=19,
        min_opacity=0.3,
    ).add_to(heat_group)

    return heat_group