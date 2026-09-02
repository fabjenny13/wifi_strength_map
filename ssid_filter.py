def get_available_ssids(df):
    return sorted(df["SSID"].dropna().unique())


def filter_by_ssid(df, selected_ssids):
    """
    Keep only rows belonging to the selected SSIDs.
    """

    if not selected_ssids:
        return df

    return df[df["SSID"].isin(selected_ssids)].copy()