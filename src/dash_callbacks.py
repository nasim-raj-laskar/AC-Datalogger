from dash import ClientsideFunction, Input, Output, State, dcc, no_update
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
        return f"Car: {info['car']}  |  Track: {track}  |  Max RPM: {info['max_rpm']}  |  Fuel: {info['max_fuel_kg']} kg"

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
        fig   = track_map(df, 0, color_col or "speed_kmh", theme)
        store = {"pos_x": df["pos_x"].tolist(), "pos_z": df["pos_z"].tolist()}
        return fig, len(df) - 1, store

    # move car marker — pure JS, no server round-trip
    app.clientside_callback(
        ClientsideFunction(namespace="map", function_name="move_marker"),
        Output("map-dummy",    "data"),
        Input("map-slider",    "value"),
        State("map-pos-store", "data"),
        prevent_initial_call=True,
    )
