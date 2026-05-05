import sys
from pathlib import Path

import yaml
from dash import Dash  #type: ignore

sys.path.insert(0, str(Path(__file__).parent))

from src.dash_callbacks import register_callbacks
from src.dash_data import list_sessions
from src.dash_layout import build_layout

with open("config.yaml") as f:
    app_cfg = yaml.safe_load(f)

with open("dashboard.yaml") as f:
    dash_cfg = yaml.safe_load(f)

# merge so callbacks have access to sessions_dir alongside dashboard settings
cfg = {**dash_cfg, "output": app_cfg["output"]}

app = Dash(__name__)
app.layout = build_layout(list_sessions(app_cfg["output"]["sessions_dir"]), cfg)
register_callbacks(app, cfg)

if __name__ == "__main__":
    srv = dash_cfg["server"]
    app.run(host=srv["host"], port=srv["port"], debug=srv["debug"])
