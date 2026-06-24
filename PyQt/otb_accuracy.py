import os
import tarfile
import tempfile
import shutil
import numpy as np
import xmltodict
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt


# ============================================================
# SETTINGS
# ============================================================

SHOW_PLOT = True

# ============================================================
# FILE PICKER
# ============================================================

root = tk.Tk()
root.withdraw()

otb_file = filedialog.askopenfilename(
    title="Select OTB4 recording",
    filetypes=[("OTB4 files", "*.otb4")]
)
root.destroy()

if not otb_file:
    raise SystemExit("No file selected.")

# ============================================================
# EXTRACT
# ============================================================

tmp_dir = tempfile.mkdtemp(prefix="otb4_")

try:

    with tarfile.open(otb_file, "r") as tar:
        tar.extractall(tmp_dir)

    # --------------------------------------------------------
    # Locate trapezoid XML
    # --------------------------------------------------------

    trap_xml = None

    for f in os.listdir(tmp_dir):
        if f.startswith("TrapezoidalTracks") and f.endswith(".xml"):
            trap_xml = os.path.join(tmp_dir, f)
            break

    if trap_xml is None:
        raise RuntimeError("No trapezoidal track found.")

    # --------------------------------------------------------
    # Parse XML
    # --------------------------------------------------------

    with open(trap_xml, "r", encoding="utf-8") as fd:
        xml = xmltodict.parse(fd.read())

    tracks = xml["ArrayOfTrackInfo"]["TrackInfo"]

    if not isinstance(tracks, list):
        tracks = [tracks]

    performed_track = tracks[0]
    target_track = tracks[1]

    fs = float(performed_track["SamplingFrequency"])

    sig_file = performed_track["SignalStreamPath"]

    sig_path = os.path.join(tmp_dir, sig_file)

    if not os.path.exists(sig_path):
        raise RuntimeError(
            f"Signal file not found:\n{sig_file}"
        )

    print("\n===================================")
    print("TRAPEZOID TRACK")
    print("===================================")

    print("Signal file :", sig_file)
    print("Sampling Hz :", fs)

    print(
        "Performed   :",
        performed_track["SubTitle"]
    )

    print(
        "Target      :",
        target_track["SubTitle"]
    )

    # --------------------------------------------------------
    # Read signal
    # --------------------------------------------------------

    # SampleSize = 8 bytes -> float64

    raw = np.fromfile(sig_path, dtype=np.float64)

    total_channels = int(
        performed_track["TotalChannelsInFile"]
    )

    data = raw.reshape(
        (total_channels, -1),
        order="F"
    )

    performed = data[0]
    target = data[1]

    # --------------------------------------------------------
    # Detect active protocol
    # --------------------------------------------------------

    diff_target = np.diff(target)

    active = np.where(
        np.abs(diff_target) > 1e-12
    )[0]

    if len(active) == 0:
        raise RuntimeError(
            "No trapezoid transitions detected."
        )

    start_idx = active[0]
    end_idx = active[-1] + 1

    performed_active = performed[start_idx:end_idx]
    target_active = target[start_idx:end_idx]

    t = np.arange(
        len(target_active)
    ) / fs

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    # Scientific metric (for publications)

    tracking_rmse = np.sqrt(
        np.mean(
            (performed_active - target_active) ** 2
        )
    )

    scientific_metric = tracking_rmse

    # Participant-friendly score
    # Adapt the division by 10 if the score is too
    # strict or too permissive

    participant_score = (
        100 *
        (1 - tracking_rmse / 10)
    )

    participant_score = np.clip(
        participant_score,
        0,
        100
    )

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    print("\n===================================")
    print("RESULTS")
    print("===================================")

    print(
        f"Protocol start : "
        f"{start_idx/fs:.2f} s"
    )

    print(
        f"Protocol end   : "
        f"{end_idx/fs:.2f} s"
    )

    print(
        f"Duration       : "
        f"{(end_idx-start_idx)/fs:.2f} s"
    )

    print(
        f"Target peak    : "
        f"{np.max(target_active):.2f} %MVC"
    )

    print(
        f"\nScientific metric (RMSE): "
        f"{scientific_metric:.3f} %MVC"
    )

    print(
        f"Participant score: "
        f"{participant_score:.1f}%"
    )
    # --------------------------------------------------------
    # Plot
    # --------------------------------------------------------

    if SHOW_PLOT:

        plt.figure(figsize=(12, 5))

        plt.plot(
            t,
            target_active,
            linewidth=3,
            label="Target"
        )

        plt.plot(
            t,
            performed_active,
            linewidth=2,
            label="Performed"
        )

        plt.xlabel("Time (s)")
        plt.ylabel("%MVC")

        plt.title(
            f"Score = {participant_score:.1f}% | "
            f"RMSE = {scientific_metric:.2f} %MVC"
        )

        plt.legend()
        plt.grid(True)

        plt.tight_layout()
        plt.show()

finally:

    shutil.rmtree(
        tmp_dir,
        ignore_errors=True
    )