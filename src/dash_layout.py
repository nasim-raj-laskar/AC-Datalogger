from dash import dcc, html  #type: ignore


def build_layout(sessions: list[str], cfg: dict) -> html.Div:
    theme = cfg["theme"]
    tabs_cfg = cfg["tabs"]

    return html.Div(
        style={
            "fontFamily": "sans-serif",
            "backgroundColor": theme["background"],
            "color": theme["text"],
            "padding": "16px",
        },
        children=[
            html.H2("AC Telemetry Dashboard", style={"marginBottom": "8px"}),
            dcc.Dropdown(
                id="session-select",
                options=[{"label": s, "value": s} for s in sessions],
                value=sessions[0] if sessions else None,
                style={"color": "#111", "width": "480px"},
            ),
            html.Div(
                id="session-header",
                style={"margin": "12px 0", "fontSize": "14px", "color": theme["muted"]},
            ),
            dcc.Tabs(
                id="tabs",
                value=tabs_cfg[0]["id"],
                children=[dcc.Tab(label=t["label"], value=t["id"]) for t in tabs_cfg],
                colors={
                    "border":     theme["surface"],
                    "primary":    theme["accent"],
                    "background": theme["surface"],
                },
            ),
            dcc.Store(id="map-pos-store"),
            dcc.Store(id="map-dummy"),
            # regular tab content (non-map tabs)
            html.Div(id="tab-content", style={"marginTop": "12px"}),
            # map tab — permanently in DOM, hidden/shown via style
            html.Div(
                id="map-tab-content",
                style={"display": "none", "marginTop": "12px"},
                children=[
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "gap": "12px", "marginBottom": "8px"},
                        children=[
                            html.Label("Colour by:", style={"color": theme["muted"]}),
                            dcc.Dropdown(
                                id="map-color-select",
                                options=[{"label": c, "value": c} for c in cfg["tabs"][next(
                                    i for i, t in enumerate(cfg["tabs"]) if t["id"] == "map"
                                )]["color_channels"]],
                                value=cfg["tabs"][next(
                                    i for i, t in enumerate(cfg["tabs"]) if t["id"] == "map"
                                )]["color_channels"][0],
                                clearable=False,
                                style={"color": "#111", "width": "200px"},
                            ),
                        ],
                    ),
                    dcc.Graph(id="g-map", config={"displayModeBar": True}),
                    html.Label("Scrub position:", style={"color": theme["muted"], "marginTop": "8px"}),
                    dcc.Slider(
                        id="map-slider",
                        min=0, max=100, step=1, value=0,
                        marks=None,
                        tooltip={"placement": "bottom", "always_visible": True},
                        updatemode="drag",
                    ),
                ],
            ),
        ],
    )
