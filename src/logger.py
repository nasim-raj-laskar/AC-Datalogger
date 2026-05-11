import mmap
import ctypes
import time
import os
import json
import numpy as np
import pandas as pd
from datetime import datetime

from src.shared_memory import SPageFilePhysics, SPageFileGraphic, SPageFileStatic
from src.sampler import extract_sample


def record(cfg):
    print("Connecting to Assetto Corsa...")

    shm_cfg = cfg["shared_memory"]
    rec_cfg = cfg["recording"]
    out_cfg = cfg["output"]

    try:
        shm_physics = mmap.mmap(-1, ctypes.sizeof(SPageFilePhysics), shm_cfg["physics_map"])
        shm_graphic = mmap.mmap(-1, 820, shm_cfg["graphic_map"])
        shm_static  = mmap.mmap(-1, ctypes.sizeof(SPageFileStatic),  shm_cfg["static_map"])
    except Exception:
        print("Could not connect. Is Assetto Corsa running?")
        return

    static = SPageFileStatic.from_buffer_copy(shm_static)
    session_meta = {
        "car":                static.carModel,
        "track":              static.track,
        "track_configuration": static.trackConfiguration,
        "max_rpm":            static.maxRpm,
        "max_power_w":        static.maxPower,
        "max_torque_nm":      static.maxTorque,
        "max_fuel_l":         static.maxFuel,
    }

    data_buffer = []
    print("Connected! Waiting for you to hit the track...")
    print("Press Ctrl+C to stop recording and save the data.")

    try:
        while True:
            physics = SPageFilePhysics.from_buffer_copy(shm_physics)
            graphic = SPageFileGraphic.from_buffer_copy(shm_graphic)

            if physics.speedKmh > rec_cfg["speed_threshold_kmh"]:
                data_buffer.append(extract_sample(physics, graphic))

            time.sleep(rec_cfg["sample_interval_sec"])

    except KeyboardInterrupt:
        print(f"\nRecording stopped. Processing {len(data_buffer)} data points...")
        _save(data_buffer, session_meta, out_cfg)


def _save(data_buffer, session_meta, out_cfg):
    if not data_buffer:
        print("No data was recorded. Did you drive out of the pits?")
        return

    df = pd.DataFrame(data_buffer)

    dt = df["timestamp"].diff().fillna(0)
    heading = df["heading"]
    df["pos_x"] = (df["vel_x"] * np.cos(heading) - df["vel_z"] * np.sin(heading))
    df["pos_z"] = (df["vel_x"] * np.sin(heading) + df["vel_z"] * np.cos(heading))
    df["pos_x"] = (df["pos_x"] * dt).cumsum()
    df["pos_z"] = (df["pos_z"] * dt).cumsum()

    car   = session_meta["car"].replace(" ", "_") or "unknown_car"
    track = session_meta["track"].replace(" ", "_") or "unknown_track"
    ts    = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = os.path.join(out_cfg["sessions_dir"], f"{track}_{car}_{ts}")
    os.makedirs(session_dir, exist_ok=True)

    with open(os.path.join(session_dir, "session_info.json"), "w") as f:
        json.dump(session_meta, f, indent=2)

    if out_cfg["save_parquet"]:
        df.to_parquet(os.path.join(session_dir, "telemetry.parquet"), engine="pyarrow")

    if out_cfg["save_csv"]:
        df.to_csv(os.path.join(session_dir, "telemetry.csv"), index=False)

    print(f"Saved {len(df)} rows to {session_dir}")
