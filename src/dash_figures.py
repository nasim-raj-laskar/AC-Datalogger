import pandas as pd
import plotly.graph_objects as go


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
