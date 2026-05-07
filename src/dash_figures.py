import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go


def track_map(df: pd.DataFrame, idx: int, color_col: str, theme: dict) -> go.Figure:
    """Full track trace coloured by `color_col`, with a marker at sample `idx`."""
    fig = go.Figure()

    # rotate 45° counterclockwise
    angle = np.pi / 2
    cos_a, sin_a = np.cos(angle), np.sin(angle)
    x_rot = df["pos_x"] * cos_a - df["pos_z"] * sin_a
    z_rot = df["pos_x"] * sin_a + df["pos_z"] * cos_a

    # track trace coloured by chosen channel
    fig.add_trace(go.Scattergl(
        x=x_rot, y=z_rot,
        mode="markers",
        marker=dict(
            size=3,
            color=df[color_col],
            colorscale="RdYlGn",
            showscale=True,
            colorbar=dict(title=color_col, thickness=12, len=0.8),
        ),
        name=color_col,
        hovertemplate=f"%{{customdata:.1f}} {color_col}<extra></extra>",
        customdata=df[color_col],
    ))

    # car position marker
    row = df.iloc[idx]
    marker_x = row["pos_x"] * cos_a - row["pos_z"] * sin_a
    marker_z = row["pos_x"] * sin_a + row["pos_z"] * cos_a
    fig.add_trace(go.Scatter(
        x=[marker_x], y=[marker_z],
        mode="markers",
        marker=dict(size=14, color=theme["accent"], symbol="circle", line=dict(width=2, color="white")),
        name="car",
        hovertemplate=f"t={row['t']:.1f}s  {color_col}={row[color_col]:.1f}<extra></extra>",
    ))

    fig.update_layout(
        title="Track Map",
        template=theme["plot_template"],
        height=600,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(scaleanchor="y", showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        legend=dict(orientation="h", y=-0.04),
        uirevision="track-map",  # keeps zoom/pan when marker updates
    )
    return fig


def multiline(df: pd.DataFrame, plot_cfg: dict, theme: dict, chart_cfg: dict) -> go.Figure:
    fig = go.Figure()
    for col in plot_cfg["cols"]:
        fig.add_trace(go.Scattergl(x=df["t"], y=df[col], name=col, mode="lines"))
    m = chart_cfg["margin"]
    fig.update_layout(
        title=plot_cfg["title"],
        xaxis_title="Time (s)",
        yaxis_title=plot_cfg.get("y_label", ""),
        template=theme["plot_template"],
        margin=dict(l=m["l"], r=m["r"], t=m["t"], b=m["b"]),
        height=chart_cfg["height"],
        legend=dict(orientation="h", y=-0.25),
    )
    return fig


def power_torque_curves(car_id: str, theme: dict) -> tuple[go.Figure, go.Figure]:
    """Load power and torque curves from metadata."""
    meta_path = Path("metadata") / car_id / "specs.json"
    if not meta_path.exists():
        return None, None
    
    import re
    raw = meta_path.read_text(encoding="utf-8")
    raw = re.sub(r'[\x00-\x1f](?=[^"]*")', ' ', raw)
    specs = json.loads(raw)
    power_curve = specs.get("powerCurve", [])
    torque_curve = specs.get("torqueCurve", [])
    
    # Power curve
    power_fig = go.Figure()
    if power_curve:
        rpm = [float(p[0]) for p in power_curve]
        bhp = [float(p[1]) for p in power_curve]
        power_fig.add_trace(go.Scatter(
            x=rpm, y=bhp,
            mode="lines",
            line=dict(color=theme["accent"], width=3),
            fill="tozeroy",
            fillcolor=f"rgba(231, 76, 60, 0.2)",
            name="Power"
        ))
    power_fig.update_layout(
        title="Power Curve",
        xaxis_title="RPM",
        yaxis_title="BHP",
        template=theme["plot_template"],
        height=300,
        margin=dict(l=50, r=20, t=40, b=40),
        showlegend=False
    )
    
    # Torque curve
    torque_fig = go.Figure()
    if torque_curve:
        rpm = [float(t[0]) for t in torque_curve]
        nm = [float(t[1]) for t in torque_curve]
        torque_fig.add_trace(go.Scatter(
            x=rpm, y=nm,
            mode="lines",
            line=dict(color=theme["accent"], width=3),
            fill="tozeroy",
            fillcolor=f"rgba(231, 76, 60, 0.2)",
            name="Torque"
        ))
    torque_fig.update_layout(
        title="Torque Curve",
        xaxis_title="RPM",
        yaxis_title="Nm",
        template=theme["plot_template"],
        height=300,
        margin=dict(l=50, r=20, t=40, b=40),
        showlegend=False
    )
    
    return power_fig, torque_fig
