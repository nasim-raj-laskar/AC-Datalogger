from dash import Input, Output, dcc

from .dash_data import load_session
from .dash_figures import multiline


def register_callbacks(app, cfg: dict):
    sessions_dir = cfg["output"]["sessions_dir"]
    theme = cfg["theme"]
    chart_cfg = cfg["charts"]
    tabs_cfg = cfg["tabs"]

    tab_plots = {t["id"]: t["plots"] for t in tabs_cfg}

    @app.callback(Output("session-header", "children"), Input("session-select", "value"))
    def update_header(session):
        if not session:
            return ""
        _, info = load_session(sessions_dir, session)
        track = info["track"]
        if info.get("track_configuration"):
            track += f" ({info['track_configuration']})"
        return f"Car: {info['car']}  |  Track: {track}  |  Max RPM: {info['max_rpm']}  |  Fuel: {info['max_fuel_kg']} kg"

    @app.callback(
        Output("tab-content", "children"),
        Input("session-select", "value"),
        Input("tabs", "value"),
    )
    def update_tab(session, tab):
        if not session or tab not in tab_plots:
            return ""
        df, _ = load_session(sessions_dir, session)
        return [
            dcc.Graph(
                id=f"g-{p['id']}",
                figure=multiline(df, p, theme, chart_cfg),
                config={"displayModeBar": False},
            )
            for p in tab_plots[tab]
        ]
