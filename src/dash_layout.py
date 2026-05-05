from dash import dcc, html


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
                    "border":      theme["surface"],
                    "primary":     theme["accent"],
                    "background":  theme["surface"],
                },
            ),
            html.Div(id="tab-content", style={"marginTop": "12px"}),
            # map controls — shown only when map tab is active
            html.Div(
                id="map-controls",
                style={"display": "none", "marginTop": "12px", "gap": "12px"},
                children=[
                    html.Label("Colour by:", style={"color": theme["muted"], "marginRight": "8px"}),
                    dcc.Dropdown(
                        id="map-color-select",
                        options=[{"label": c, "value": c} for c in cfg["tabs"][next(
                            i for i, t in enumerate(cfg["tabs"]) if t["id"] == "map"
                        )]["color_channels"]],
                        value=cfg["tabs"][next(
                            i for i, t in enumerate(cfg["tabs"]) if t["id"] == "map"
                        )]["color_channels"][0],
                        clearable=False,
                        style={"color": "#111", "width": "200px", "display": "inline-block"},
                    ),
                    html.Div(
                        id="map-slider-container",
                        style={"marginTop": "12px"},
                        children=[
                            html.Label("Scrub position:", style={"color": theme["muted"]}),
                            dcc.Slider(
                                id="map-slider",
                                min=0, max=100, step=1, value=0,
                                marks=None,
                                tooltip={"placement": "bottom", "always_visible": True},
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
