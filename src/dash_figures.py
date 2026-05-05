import pandas as pd
import plotly.graph_objects as go


def track_map(df: pd.DataFrame, idx: int, color_col: str, theme: dict) -> go.Figure:
    """Full track trace coloured by `color_col`, with a marker at sample `idx`."""
    fig = go.Figure()

    # track trace coloured by chosen channel
    fig.add_trace(go.Scattergl(
        x=df["pos_x"], y=df["pos_z"],
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
    fig.add_trace(go.Scatter(
        x=[row["pos_x"]], y=[row["pos_z"]],
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
