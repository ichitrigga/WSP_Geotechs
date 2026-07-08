#------------------------------
# User Instructions
#-----------------------------
print("")
print("Before running this script, ensure that the required packages are installed:")
print("- pandas")
print("- matplotlib")
print("- mplstereonet")
print("- numpy")
print("")
pause = input("Press Enter to continue or Ctrl+C to exit...")
print("")
print("ensure that the CSV file 'Simple_CSV_STRESS.csv' is in the same directory as this script.")
print("ensure that the CSV file has the following columns:")
print("- SampleID")
print("- S1Bearing_deg")
print("- S1Plunge_deg")
print("- S2Bearing_deg")
print("- S2Plunge_deg")
print("- S3Bearing_deg")
print("- S3Plunge_deg")
print("- S1Magnitude_MPa")
print("- S2Magnitude_MPa")
print("- S3Magnitude_MPa")
print("")
pause = input("Press Enter to continue or Ctrl+C to exit...")
print("")
#------------------------------
#import packages
#-----------------------------
import pandas as pd
import matplotlib.pyplot as plt
import mplstereonet #shows as unused but needed for plots - dont remove or disable
from pathlib import Path
import numpy as np

#------------------------------
# Read data
#-----------------------------
BASE_DIR = Path(__file__).parent
csv_file = BASE_DIR / "Simple_CSV_STRESS.csv"
df = pd.read_csv(csv_file)

#------------------------------
# Confirm orthogonality
#------------------------------
def line_to_vector(bearing_deg, plunge_deg): # type: ignore
    bearing = np.radians(bearing_deg)
    plunge = np.radians(plunge_deg)
    x = np.cos(plunge) * np.sin(bearing)
    y = np.cos(plunge) * np.cos(bearing)
    z = -np.sin(plunge)
    return np.array([x, y, z])
def axis_angle_degrees(v1, v2):
    dot = np.dot(v1, v2)
    dot = abs(dot)
    dot = np.clip(dot, -1.0, 1.0)
    return np.degrees(np.arccos(dot))
angles = []
for _, row in df.iterrows():
    s1 = line_to_vector(row["S1Bearing_deg"], row["S1Plunge_deg"])
    s2 = line_to_vector(row["S2Bearing_deg"], row["S2Plunge_deg"])
    s3 = line_to_vector(row["S3Bearing_deg"], row["S3Plunge_deg"])
    angle_s1_s2 = axis_angle_degrees(s1, s2)
    angle_s1_s3 = axis_angle_degrees(s1, s3)
    angle_s2_s3 = axis_angle_degrees(s2, s3)
    angles.append({
        "SampleID": row["SampleID"],
        "S1_S2_angle_deg": angle_s1_s2,
        "S1_S3_angle_deg": angle_s1_s3,
        "S2_S3_angle_deg": angle_s2_s3
    })
angle_df = pd.DataFrame(angles)
#print(angle_df.round(2))
print("\nOrthogonality summary:")
print(angle_df[[
    "S1_S2_angle_deg",
    "S1_S3_angle_deg",
    "S2_S3_angle_deg"
]].describe().round(2))
tolerance_deg = 5
bad_rows = angle_df[
    (abs(angle_df["S1_S2_angle_deg"] - 90) > tolerance_deg) |
    (abs(angle_df["S1_S3_angle_deg"] - 90) > tolerance_deg) |
    (abs(angle_df["S2_S3_angle_deg"] - 90) > tolerance_deg)
]
if bad_rows.empty:
    print("\nAll principal stress axes are orthogonal within tolerance.")
else:
    print("\nWARNING: Some records are not orthogonal:")
    print(bad_rows.round(2))

#------------------------------------------------------------
# Confirm tensor reconstruction
#------------------------------------------------------------
def line_to_vector(bearing_deg, plunge_deg):
    """
    Bearing clockwise from north
    Plunge positive downward
    x = East
    y = North
    z = Down
    """
    bearing = np.radians(bearing_deg)
    plunge = np.radians(plunge_deg)
    x = np.cos(plunge) * np.sin(bearing)
    y = np.cos(plunge) * np.cos(bearing)
    z = np.sin(plunge)
    return np.array([x, y, z])
tensor_results = []
for _, row in df.iterrows():
    # Principal stresses
    s1 = row["S1Magnitude_MPa"]
    s2 = row["S2Magnitude_MPa"]
    s3 = row["S3Magnitude_MPa"]
    # Direction vectors
    v1 = line_to_vector(
        row["S1Bearing_deg"],
        row["S1Plunge_deg"]
    )
    v2 = line_to_vector(
        row["S2Bearing_deg"],
        row["S2Plunge_deg"]
    )
    v3 = line_to_vector(
        row["S3Bearing_deg"],
        row["S3Plunge_deg"]
    )
    # Tensor reconstruction
    tensor = (
        s1 * np.outer(v1, v1)
        + s2 * np.outer(v2, v2)
        + s3 * np.outer(v3, v3)
    )
    Sxx = tensor[0, 0]
    Syy = tensor[1, 1]
    Szz = tensor[2, 2]
    # Horizontal tensor
    H = tensor[:2, :2]
    eigvals, eigvecs = np.linalg.eigh(H)
    SHmax = eigvals[1]
    SHmin = eigvals[0]
    shmax_vector = eigvecs[:, 1]
    theta = (
        np.degrees(
            np.arctan2(
                shmax_vector[0],   # east
                shmax_vector[1]    # north
            )
        )
    ) % 180
    tensor_results.append({
        "SampleID": row["SampleID"],
        "Sxx_calc": Sxx,
        "Syy_calc": Syy,
        "Szz_calc": Szz,
        "Theta_calc": theta
    })
tensor_df = pd.DataFrame(tensor_results)

required_cols = [
    "Sxx_Mpa",
    "Syy_MPa",
    "Szz_Mpa",
    "Theta_deg"
]
if all(col in df.columns for col in required_cols):
    check_df = pd.merge(
        df,
        tensor_df,
        on="SampleID"
    )
    check_df["dSxx"] = (
        check_df["Sxx_calc"]
        - check_df["Sxx_Mpa"]
    )
    check_df["dSyy"] = (
        check_df["Syy_calc"]
        - check_df["Syy_MPa"]
    )
    check_df["dSzz"] = (
        check_df["Szz_calc"]
        - check_df["Szz_Mpa"]
    )
    print("\nTensor Reconstruction Check")

    print("\nDifference Summary")
    print(
        check_df[
            [
                "dSxx",
                "dSyy",
                "dSzz"
            ]
        ].describe().round(3)
    )
    tolerance = 0.25
    failed = check_df[
        (abs(check_df["dSxx"]) > tolerance)
        | (abs(check_df["dSyy"]) > tolerance)
        | (abs(check_df["dSzz"]) > tolerance)
    ]
    if failed.empty:
        print(
            "\nAll Sxx, Syy and Szz values agree "
            f"within ±{tolerance} MPa."
        )
    else:
        print(
            "\nWARNING: Tensor reconstruction mismatch"
        )
        print(
            failed[
                [
                    "SampleID",
                    "dSxx",
                    "dSyy",
                    "dSzz"
                ]
            ].round(3)
        )

#-----------------------------
# Create figure
#-----------------------------
fig = plt.figure(figsize=(14,12))
# plots...
fig.subplots_adjust(
    wspace=0.15,
    hspace=0.35
)

# -----------------------------
# S1 Density needs matplotlib 3.7.1 
# -----------------------------
ax1 = fig.add_subplot(221, projection='stereonet')
cax1 = ax1.density_contourf( # type: ignore
    df["S1Bearing_deg"],
    df["S1Plunge_deg"],
    measurement="lines",
    cmap="Reds"
)
ax1.line( # type: ignore
    df["S1Plunge_deg"],
    df["S1Bearing_deg"],
    "k.",
    alpha=0.4
)
ax1.grid(True)
ax1.set_title("S1 Density", pad=22)

# -----------------------------
# S2 Density needs matplotlib 3.7.1
# -----------------------------
ax2 = fig.add_subplot(222, projection='stereonet')

cax2 = ax2.density_contourf( # type: ignore
    df["S2Bearing_deg"],
    df["S2Plunge_deg"],
    measurement="lines",
    cmap="Greens"
)
ax2.line( # type: ignore
    df["S2Plunge_deg"],
    df["S2Bearing_deg"],
    "k.",
    alpha=0.4
)
ax2.grid(True)
ax2.set_title("S2 Density", pad=22)

# -----------------------------
# S3 Density needs matplotlib 3.7.1
# -----------------------------
ax3 = fig.add_subplot(223, projection='stereonet') 
cax3 = ax3.density_contourf( # type: ignore
    df["S3Bearing_deg"],
    df["S3Plunge_deg"],
    measurement="lines",
    cmap="Blues"
)
ax3.line( # type: ignore
    df["S3Plunge_deg"],
    df["S3Bearing_deg"],
    "k.",
    alpha=0.4
)
ax3.grid(True)
ax3.set_title("S3 Density", pad=22)

# -----------------------------
# Combined Pole Plot needs matplotlib 3.7.1
# -----------------------------
ax4 = fig.add_subplot(224, projection='stereonet')

# Actual data (no labels)
ax4.line( # type: ignore
    df["S1Plunge_deg"],
    df["S1Bearing_deg"],
    marker="o",
    linestyle="None",
    color="red"
)
ax4.line( # type: ignore
    df["S2Plunge_deg"],
    df["S2Bearing_deg"],
    marker="o",
    linestyle="None",
    color="green"
)
ax4.line( # type: ignore
    df["S3Plunge_deg"],
    df["S3Bearing_deg"],
    marker="o",
    linestyle="None",
    color="blue"
)
# Dummy points for legend
ax4.line( # type: ignore
    [0], [0],
    marker="o",
    linestyle="None",
    color="red",
    label="S1"
)
ax4.line( # type: ignore
    [0], [0],
    marker="o",
    linestyle="None",
    color="green",
    label="S2"
)
ax4.line( # type: ignore
    [0], [0],
    marker="o",
    linestyle="None",
    color="blue",
    label="S3"
)
ax4.grid(True)

ax4.legend(
    loc="center left",
    bbox_to_anchor=(1.05, 0.5),
    frameon=False
)
ax4.set_title("Principal Stress Axes", pad=22)
#fig.tight_layout()
plt.savefig(
    "Stress_Stereonets.png",
    dpi=300,
    bbox_inches="tight"
)
print("")
pause = input("Press Enter to show plots or Ctrl+C to exit...")
plt.show()
exit()