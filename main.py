import yaml
import os

from src.logger import record

if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    # resolve sessions_dir relative to project root
    cfg["output"]["sessions_dir"] = os.path.join(
        os.path.dirname(__file__), cfg["output"]["sessions_dir"]
    )

    record(cfg)
