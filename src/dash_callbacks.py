from dash import Input, Output, dcc, no_update

from .dash_data import load_session
from .dash_figures import multiline, track_map


def register_callbacks(app, cfg: dict):
    sessions_dir = cfg["output"]["sessions_dir"]
    theme = cfg["theme"]
    chart_cfg = cfg["charts"]
    tabs_cfg = cfg["tabs"]

    tab_plots = {t["id"]: t.get("plots", []) for t in tabs_cfg}

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
        Output("map-controls", "style"),
        Output("map-slider", "max"),
        Input("tabs", "value"),
        Input("session-select", "value"),
    )
    def toggle_map_controls(tab, session):
        visible = {"display": "block", "marginTop": "12px"}
        hidden  = {"display": "none",  "marginTop": "12px"}
        if tab != "map" or not session:
            return hidden, no_update
        df, _ = load_session(sessions_dir, session)
        return visible, len(df) - 1

    @app.callback(
        Output("tab-content", "children"),
        Input("session-select", "value"),
        Input("tabs", "value"),
        Input("map-slider", "value"),
        Input("map-color-select", "value"),
    )
    def update_tab(session, tab, slider_idx, color_col):
        if not session:
            return ""
        df, _ = load_session(sessions_dir, session)

        if tab == "map":
            has_pos = "pos_x" in df.columns and "pos_z" in df.columns
            if not has_pos:
                return dcc.Markdown("_pos_x / pos_z not available in this session._")
            idx = min(slider_idx or 0, len(df) - 1)
            return dcc.Graph(
                id="g-map",
                figure=track_map(df, idx, color_col or "speed_kmh", theme),
                config={"displayModeBar": True},
            )

        return [
            dcc.Graph(
                id=f"g-{p['id']}",
                figure=multiline(df, p, theme, chart_cfg),
                config={"displayModeBar": False},
            )
            for p in tab_plots.get(tab, [])
        ]
