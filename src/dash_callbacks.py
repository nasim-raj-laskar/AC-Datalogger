from dash import ClientsideFunction, Input, Output, State, dcc, html, no_update  #type: ignore
from .dash_data import load_session
from .dash_figures import multiline, track_map

def register_callbacks(app, cfg: dict):
    sessions_dir = cfg["output"]["sessions_dir"]
    theme        = cfg["theme"]
    chart_cfg    = cfg["charts"]
    tabs_cfg     = cfg["tabs"]
    tab_plots    = {t["id"]: t.get("plots", []) for t in tabs_cfg}

    @app.callback(Output("session-header", "children"), Input("session-select", "value"))
    def update_header(session):
        if not session:
            return ""
        _, info = load_session(sessions_dir, session)
        track = info["track"]
        if info.get("track_configuration"):
            track += f" ({info['track_configuration']})"
        return f"Car: {info['car']}  |  Track: {track}  |  Max RPM: {info['max_rpm']}  |  Tank: {info.get('max_fuel_l', info.get('max_fuel_kg', '?'))} L"

    @app.callback(Output("stats-panel", "children"), Input("session-select", "value"))
    def update_stats(session):
        if not session:
            return []
        df, _ = load_session(sessions_dir, session)

        def _stat(label, value):
            return html.Div(
                style={
                    "backgroundColor": theme["surface"],
                    "borderRadius": "6px",
                    "padding": "8px 16px",
                    "minWidth": "120px",
                    "textAlign": "center",
                },
                children=[
                    html.Div(value, style={"fontSize": "20px", "fontWeight": "bold", "color": theme["accent"]}),
                    html.Div(label, style={"fontSize": "11px", "color": theme["muted"], "marginTop": "2px"}),
                ],
            )

        duration = df["t"].iloc[-1]
        top_speed = df["speed_kmh"].max() if "speed_kmh" in df.columns else None
        max_g_lat = df["g_lat"].abs().max() if "g_lat" in df.columns else None
        max_g_lon = df["g_lon"].abs().max() if "g_lon" in df.columns else None
        fuel_used = (df["fuel"].iloc[0] - df["fuel"].iloc[-1]) if "fuel" in df.columns else None

        stats = [
            _stat("Duration",   f"{duration:.0f} s"),
            _stat("Samples",    f"{len(df):,}"),
        ]
        if top_speed  is not None: stats.append(_stat("Top Speed",   f"{top_speed:.0f} km/h"))
        if max_g_lat  is not None: stats.append(_stat("Max Lat G",   f"{max_g_lat:.2f} g"))
        if max_g_lon  is not None: stats.append(_stat("Max Lon G",   f"{max_g_lon:.2f} g"))
        if fuel_used  is not None: stats.append(_stat("Fuel Used",   f"{fuel_used:.2f} L"))
        return stats

    # show/hide the two content areas based on active tab
    @app.callback(
        Output("tab-content",     "style"),
        Output("map-tab-content", "style"),
        Input("tabs", "value"),
    )
    def toggle_content_areas(tab):
        show = {"display": "block", "marginTop": "12px"}
        hide = {"display": "none",  "marginTop": "12px"}
        if tab == "map":
            return hide, show
        return show, hide

    # regular (non-map) tabs
    @app.callback(
        Output("tab-content", "children"),
        Input("session-select", "value"),
        Input("tabs", "value"),
    )
    def update_tab(session, tab):
        if not session or tab == "map":
            return ""
        df, _ = load_session(sessions_dir, session)
        return [
            dcc.Graph(
                id=f"g-{p['id']}",
                figure=multiline(df, p, theme, chart_cfg),
                config={"displayModeBar": False},
            )
            for p in tab_plots.get(tab, [])
        ]

    # rebuild map figure when session or colour changes
    @app.callback(
        Output("g-map",        "figure"),
        Output("map-slider",   "max"),
        Output("map-pos-store","data"),
        Input("session-select",   "value"),
        Input("map-color-select", "value"),
    )
    def update_map(session, color_col):
        if not session:
            return no_update, no_update, no_update
        df, _ = load_session(sessions_dir, session)
        if "pos_x" not in df.columns or "pos_z" not in df.columns:
            return no_update, no_update, no_update
        import numpy as np
        angle = np.pi / 2
        cos_a, sin_a = np.cos(angle), np.sin(angle)
        x_rot = (df["pos_x"] * cos_a - df["pos_z"] * sin_a).tolist()
        z_rot = (df["pos_x"] * sin_a + df["pos_z"] * cos_a).tolist()
        fig   = track_map(df, 0, color_col or "speed_kmh", theme)
        store = {"pos_x": x_rot, "pos_z": z_rot}
        return fig, len(df) - 1, store

    # move car marker — pure JS, no server round-trip
    app.clientside_callback(
        ClientsideFunction(namespace="map", function_name="move_marker"),
        Output("map-dummy",    "data"),
        Input("map-slider",    "value"),
        State("map-pos-store", "data"),
        prevent_initial_call=True,
    )
