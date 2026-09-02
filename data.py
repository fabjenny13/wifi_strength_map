# data.py
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN

SHEET_URL = "https://docs.google.com/spreadsheets/d/1pHg-lgImRUUAHPI8eXAPXVKCM5IDRqp6lhoZE0FLwgg/export?format=csv&gid=0"
DISTANCE_THRESHOLD = 3  # meters
EARTH_RADIUS = 6371000


def fetch_data(url: str = SHEET_URL) -> pd.DataFrame:
    return pd.read_csv(url)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna(subset=["Latitude", "Longitude", "RSSI_dBm"])


def cluster_by_ssid(df: pd.DataFrame) -> pd.DataFrame:
    """Group nearby measurements per SSID into single points."""
    grouped_data = []

    for ssid, ssid_df in df.groupby("SSID"):
        coords = np.radians(ssid_df[["Latitude", "Longitude"]].values)

        db = DBSCAN(
            eps=DISTANCE_THRESHOLD / EARTH_RADIUS,
            min_samples=1,
            metric="haversine",
        )
        labels = db.fit_predict(coords)

        ssid_df = ssid_df.copy()
        ssid_df["cluster"] = labels

        for _, cluster in ssid_df.groupby("cluster"):
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
                "Timestamp": cluster["Timestamp"].iloc[0],
            })

    return pd.DataFrame(grouped_data)