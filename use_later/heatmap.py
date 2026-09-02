import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import RBFInterpolator

def create_heatmap(coordinates, signals, grid_resolution=100):
    """
    Create a radial-style Wi-Fi signal strength heatmap.

    coordinates: list of (x, y) positions
    signals: corresponding Wi-Fi signal strengths in dBm
    """

    if len(coordinates) != len(signals):
        raise ValueError("Number of coordinates must match number of signals.")

    coordinates = np.array(coordinates, dtype=float)
    signals = np.array(signals, dtype=float)

    x = coordinates[:, 0]
    y = coordinates[:, 1]

    grid_x = np.linspace(x.min(), x.max(), grid_resolution)
    grid_y = np.linspace(y.min(), y.max(), grid_resolution)

    grid_x, grid_y = np.meshgrid(grid_x, grid_y)

    # Radial mapping
    rbf = RBFInterpolator(
        coordinates,
        signals,
        kernel="gaussian",
        epsilon=1.0
    )

    grid_points = np.column_stack([
        grid_x.ravel(),
        grid_y.ravel()
    ])

    grid_signal = rbf(grid_points)
    grid_signal = grid_signal.reshape(grid_x.shape)

    plt.figure(figsize=(10, 8))

    heatmap = plt.contourf(
        grid_x,
        grid_y,
        grid_signal,
        levels=50,
        cmap="RdYlGn"
    )

    plt.scatter(
        x,
        y,
        c=signals,
        cmap="RdYlGn",
        edgecolors="black",
        s=60,
        zorder=2
    )

    plt.colorbar(
        heatmap,
        label="Wi-Fi Signal Strength (dBm)"
    )

    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.title("Wi-Fi Signal Strength Heatmap")

    plt.show()

coordinates = [
    (0, 0),
    (1, 0),
    (2, 0),
    (0, 1),
    (1, 1),
    (2, 1),
    (0, 2),
    (1, 2),
    (2, 2)
]

signals = [
    -100, -45, -60,
    -42, -65, -50,
    -20, -10, -70
]

create_heatmap(coordinates, signals)