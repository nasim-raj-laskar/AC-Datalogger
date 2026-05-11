from dash import ClientsideFunction, Input, Output, State, dcc, html, no_update  #type: ignore
from pathlib import Path
import json
import re
from .dash_data import load_session
from .dash_figures import multiline, track_map, power_torque_curves


def _spec_card(value: str, label: str, theme: dict) -> html.Div:
    return html.Div(
        style={
            "backgroundColor": theme["surface2"],
            "border": f"1px solid {theme['border']}",
            "borderRadius": "8px",
            "padding": "16px 20px",
            "textAlign": "center",
            "minWidth": "110px",
            "flex": "1",
        },
        children=[
            html.Div(value, style={"fontSize": "22px", "fontWeight": "700", "color": theme["accent"]}),
            html.Div(label, style={"fontSize": "11px", "color": theme["muted"], "marginTop": "4px", "textTransform": "uppercase", "letterSpacing": "0.05em"}),
        ],
    )


def _kpi_card(value: str, label: str, theme: dict) -> html.Div:
    return html.Div(
        style={
            "backgroundColor": theme["surface2"],
            "border": f"1px solid {theme['border']}",
            "borderRadius": "8px",
            "padding": "14px 18px",
            "textAlign": "center",
            "flex": "1",
            "minWidth": "120px",
        },
        children=[
            html.Div(value, style={"fontSize": "20px", "fontWeight": "700", "color": theme["accent"]}),
            html.Div(label, style={"fontSize": "11px", "color": theme["muted"], "marginTop": "4px", "textTransform": "uppercase", "letterSpacing": "0.05em"}),
        ],
    )


def _section_title(text: str, theme: dict) -> html.Div:
    return html.Div(
        text,
        style={
            "fontSize": "11px",
            "fontWeight": "600",
            "color": theme["muted"],
            "textTransform": "uppercase",
            "letterSpacing": "0.12em",
            "marginBottom": "12px",
            "borderBottom": f"1px solid {theme['subtle']}",
            "paddingBottom": "6px",
        },
    )


def build_overview(df, info: dict, session: str, theme: dict) -> list:
    car_id = info["car"]
    track_id = info["track"]

    # load metadata
    meta_path = Path("metadata") / car_id / "specs.json"
    specs_data = {}
    if meta_path.exists():
        try:
            raw = meta_path.read_text(encoding="utf-8")
            # strip unescaped control chars (tabs, etc.) inside strings
            raw = re.sub(r'[\x00-\x1f](?=[^"]*")', ' ', raw)
            specs_data = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError):
            specs_data = {}
    specs = specs_data.get("specs", {})
    car_name  = specs_data.get("name", car_id)
    brand     = specs_data.get("brand", "")
    tags      = specs_data.get("tags", [])
    car_class = specs_data.get("class", "")

    # image paths — check existence server-side so we never render a broken img
    meta_base = Path("metadata")
    car_img_path   = f"/metadata/{car_id}/{car_id}.jpg"   if (meta_base / car_id / f"{car_id}.jpg").exists()   else None
    logo_img_path  = f"/metadata/{car_id}/{brand.lower()}.png" if brand and (meta_base / car_id / f"{brand.lower()}.png").exists() else None
    track_img_path = f"/metadata/track/{track_id}.png"    if (meta_base / "track" / f"{track_id}.png").exists() else None

    # tag badges
    tag_badges = [
        html.Span(
            t.lstrip("#").upper(),
            style={
                "backgroundColor": theme["subtle"],
                "border": f"1px solid {theme['border']}",
                "borderRadius": "4px",
                "padding": "2px 8px",
                "fontSize": "10px",
                "color": theme["muted"],
                "letterSpacing": "0.06em",
            },
        )
        for t in tags
    ]

    # track config label
    track_label = track_id.replace("ks_", "").replace("_", " ").title()
    if info.get("track_configuration"):
        track_label += f" — {info['track_configuration'].upper()}"

    # session duration
    duration = df["t"].iloc[-1]

    # clean description — strip HTML tags, collapse whitespace
    raw_desc = specs_data.get("description", "")
    clean_desc = re.sub(r"<[^>]+>", " ", raw_desc)
    clean_desc = re.sub(r" {2,}", " ", clean_desc).strip()

    # ── SECTION 1: Hero ──────────────────────────────────────────────────────
    hero = html.Div(
        style={
            "display": "flex",
            "gap": "24px",
            "alignItems": "stretch",
            "marginBottom": "24px",
            "flexWrap": "wrap",
        },
        children=[
            # car render
            html.Div(
                style={
                    "flex": "2",
                    "minWidth": "280px",
                    "borderRadius": "12px",
                    "overflow": "hidden",
                    "minHeight": "260px",
                },
                children=[
                    html.Img(src=car_img_path, style={"width": "100%", "height": "100%", "objectFit": "cover", "display": "block"})
                    if car_img_path else html.Div("No image", style={"color": theme["border"], "padding": "40px", "textAlign": "center", "backgroundColor": theme["deep"], "height": "100%"})
                ],
            ),
            # car info panel
            html.Div(
                style={
                    "flex": "3",
                    "minWidth": "300px",
                    "backgroundColor": theme["deep"],
                    "borderRadius": "12px",
                    "padding": "24px",
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "12px",
                },
                children=[
                    html.Div([
                        html.Img(src=logo_img_path, style={"height": "48px", "marginBottom": "8px", "opacity": "0.85"})
                        if logo_img_path else None,
                        html.Div(car_name, style={"fontSize": "26px", "fontWeight": "700", "color": theme["text"], "lineHeight": "1.2"}),
                    ]),
                    html.Div(
                        style={"display": "flex", "gap": "6px", "flexWrap": "wrap"},
                        children=tag_badges,
                    ),
                    html.Div(
                        clean_desc,
                        style={
                            "fontSize": "12px",
                            "color": theme["muted2"],
                            "lineHeight": "1.7",
                            "flex": "1",
                        },
                    ) if clean_desc else None,
                    html.Div(
                        style={
                            "borderTop": f"1px solid {theme['surface']}",
                            "paddingTop": "12px",
                            "display": "flex",
                            "gap": "20px",
                            "flexWrap": "wrap",
                        },
                        children=[
                            html.Div([
                                html.Div("Track", style={"fontSize": "10px", "color": theme["muted"], "textTransform": "uppercase", "letterSpacing": "0.08em"}),
                                html.Div(track_label, style={"fontSize": "14px", "color": theme["text_dim"], "fontWeight": "600"}),
                            ]),
                            html.Div([
                                html.Div("Duration", style={"fontSize": "10px", "color": theme["muted"], "textTransform": "uppercase", "letterSpacing": "0.08em"}),
                                html.Div(f"{duration:.0f}s", style={"fontSize": "14px", "color": theme["text_dim"], "fontWeight": "600"}),
                            ]),
                        ],
                    ),
                ],
            ),
        ],
    )

    # ── SECTION 2: Key Specs ─────────────────────────────────────────────────
    spec_items = [
        (specs.get("bhp",      "—"), "Power"),
        (specs.get("torque",   "—"), "Torque"),
        (specs.get("weight",   "—"), "Weight"),
        (specs.get("pwratio",  "—"), "Pwr/Weight"),
        (specs.get("topspeed", "—"), "Top Speed"),
        (" / ".join(t.lstrip("#").upper() for t in tags if t.lower() in ["rwd", "fwd", "awd"]) or "—", "Drive"),
    ]
    key_specs = html.Div(
        style={"marginBottom": "24px"},
        children=[
            _section_title("Key Specs", theme),
            html.Div(
                style={"display": "flex", "gap": "10px", "flexWrap": "wrap"},
                children=[_spec_card(v, l, theme) for v, l in spec_items],
            ),
        ],
    )

    # ── SECTION 3: Power & Torque Curves ─────────────────────────────────────
    power_fig, torque_fig = power_torque_curves(car_id, theme)
    curves_section = html.Div(
        style={"marginBottom": "24px"},
        children=[
            _section_title("Power & Torque Curves", theme),
            html.Div(
                style={"display": "flex", "gap": "16px", "flexWrap": "wrap"},
                children=[
                    html.Div(
                        dcc.Graph(figure=power_fig, config={"displayModeBar": False}) if power_fig else html.Div("No data", style={"color": theme["muted"]}),
                        style={"flex": "1", "minWidth": "300px"},
                    ),
                    html.Div(
                        dcc.Graph(figure=torque_fig, config={"displayModeBar": False}) if torque_fig else html.Div("No data", style={"color": theme["muted"]}),
                        style={"flex": "1", "minWidth": "300px"},
                    ),
                ],
            ),
        ],
    )

    # ── SECTION 4: Session Summary KPIs ──────────────────────────────────────
    top_speed   = df["speed_kmh"].max()          if "speed_kmh" in df.columns else None
    avg_speed   = df["speed_kmh"].mean()         if "speed_kmh" in df.columns else None
    fuel_used   = (df["fuel"].iloc[0] - df["fuel"].iloc[-1]) if "fuel" in df.columns else None
    max_g_lat   = df["g_lat"].abs().max()        if "g_lat"    in df.columns else None
    max_g_lon   = df["g_lon"].abs().max()        if "g_lon"    in df.columns else None
    peak_rpm    = df["rpms"].max()               if "rpms"     in df.columns else None
    brake_pct   = (df["brake"] > 0.05).mean() * 100 if "brake"    in df.columns else None
    throttle_pct= (df["throttle"] > 0.05).mean() * 100 if "throttle" in df.columns else None

    kpi_items = [
        (f"{top_speed:.0f} km/h"    if top_speed    is not None else "—", "Top Speed"),
        (f"{avg_speed:.0f} km/h"    if avg_speed    is not None else "—", "Avg Speed"),
        (f"{fuel_used:.2f} L"       if fuel_used    is not None else "—", "Fuel Used"),
        (f"{max_g_lat:.2f} g"       if max_g_lat    is not None else "—", "Max Lat G"),
        (f"{max_g_lon:.2f} g"       if max_g_lon    is not None else "—", "Max Long G"),
        (f"{peak_rpm:.0f} rpm"      if peak_rpm     is not None else "—", "Peak RPM"),
        (f"{brake_pct:.1f}%"        if brake_pct    is not None else "—", "Brake Usage"),
        (f"{throttle_pct:.1f}%"     if throttle_pct is not None else "—", "Throttle Usage"),
    ]
    # ── SECTIONS 4+5: Session Summary + Track Preview side by side ───────────
    session_summary = html.Div(
        style={"flex": "1", "minWidth": "400px"},
        children=[
            _section_title("Session Summary", theme),
            html.Div(
                style={"display": "flex", "gap": "10px", "flexWrap": "wrap"},
                children=[_kpi_card(v, l, theme) for v, l in kpi_items],
            ),
        ],
    )

    track_preview = html.Div(
        style={"flex": "1", "minWidth": "200px"},
        children=[
            _section_title("Track Preview", theme),
            html.Div(
                style={
                    "backgroundColor": theme["deep"],
                    "borderRadius": "12px",
                    "overflow": "hidden",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "minHeight": "200px",
                },
                children=[
                    html.Img(src=track_img_path, style={"maxWidth": "100%", "maxHeight": "180px", "objectFit": "contain", "display": "block"})
                    if track_img_path else html.Div("No track preview available", style={"color": theme["muted3"], "padding": "40px"})
                ],
            ),
        ],
    )

    bottom_row = html.Div(
        style={"display": "flex", "gap": "24px", "flexWrap": "wrap", "marginBottom": "24px"},
        children=[session_summary, track_preview],
    )

    return [hero, key_specs, curves_section, bottom_row]


def register_callbacks(app, cfg: dict):
    sessions_dir = cfg["output"]["sessions_dir"]
    theme        = cfg["theme"]
    chart_cfg    = cfg["charts"]
    tabs_cfg     = cfg["tabs"]
    tab_plots    = {t["id"]: t.get("plots", []) for t in tabs_cfg}

    @app.callback(
        Output("session-select", "options"),
        Input("session-refresh", "n_intervals"),
    )
    def refresh_sessions(_):
        from .dash_data import list_sessions as _ls
        return [{"label": s, "value": s} for s in _ls(sessions_dir)]

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

    # show/hide the three content areas based on active tab
    @app.callback(
        Output("overview-tab-content", "style"),
        Output("tab-content",         "style"),
        Output("map-tab-content",     "style"),
        Input("tabs", "value"),
    )
    def toggle_content_areas(tab):
        show = {"display": "block", "marginTop": "12px"}
        hide = {"display": "none",  "marginTop": "12px"}
        if tab == "overview":
            return show, hide, hide
        if tab == "map":
            return hide, hide, show
        return hide, show, hide

    # regular (non-map, non-overview) tabs
    @app.callback(
        Output("tab-content", "children"),
        Input("session-select", "value"),
        Input("tabs", "value"),
    )
    def update_tab(session, tab):
        if not session or tab in ("map", "overview"):
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

    # overview tab
    @app.callback(
        Output("overview-tab-content", "children"),
        Input("session-select", "value"),
        Input("tabs", "value"),
    )
    def update_overview(session, tab):
        if not session or tab != "overview":
            return ""
        df, info = load_session(sessions_dir, session)
        return build_overview(df, info, session, theme)

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
