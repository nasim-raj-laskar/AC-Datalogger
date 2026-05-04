import mmap
import ctypes
import time
import os
import pandas as pd
from datetime import datetime

from src.shared_memory import SPageFilePhysics, SPageFileGraphic
from src.sampler import extract_sample


def record(cfg):
    print("Connecting to Assetto Corsa...")

    shm_cfg = cfg["shared_memory"]
    rec_cfg = cfg["recording"]
    out_cfg = cfg["output"]

    try:
        shm_physics = mmap.mmap(-1, ctypes.sizeof(SPageFilePhysics), shm_cfg["physics_map"])
        shm_graphic = mmap.mmap(-1, ctypes.sizeof(SPageFileGraphic), shm_cfg["graphic_map"])
    except Exception:
        print("Could not connect. Is Assetto Corsa running?")
        return

    data_buffer = []
    print("Connected! Waiting for you to hit the track...")
    print("Press Ctrl+C to stop recording and save the data.")

    try:
        while True:
            physics = SPageFilePhysics.from_buffer_copy(shm_physics)
            graphic = SPageFileGraphic.from_buffer_copy(shm_graphic)

            if physics.speedKmh > rec_cfg["speed_threshold_kmh"]:
                data_buffer.append(extract_sample(physics))

            time.sleep(rec_cfg["sample_interval_sec"])

    except KeyboardInterrupt:
        print(f"\nRecording stopped. Processing {len(data_buffer)} data points...")
        _save(data_buffer, out_cfg)


def _save(data_buffer, out_cfg):
    if not data_buffer:
        print("No data was recorded. Did you drive out of the pits?")
        return

    df = pd.DataFrame(data_buffer)

    session_ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = os.path.join(out_cfg["sessions_dir"], session_ts)
    os.makedirs(session_dir, exist_ok=True)

    if out_cfg["save_parquet"]:
        df.to_parquet(os.path.join(session_dir, "telemetry.parquet"), engine="pyarrow")

    if out_cfg["save_csv"]:
        df.to_csv(os.path.join(session_dir, "telemetry.csv"), index=False)

    print(f"Saved {len(df)} rows to {session_dir}")
