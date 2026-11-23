"""Reusable interactive charts for the WireGuard research dashboard."""

from __future__ import annotations

import pandas as pd
import streamlit as st

try:
    import plotly.express as px
    import plotly.graph_objects as go

    PLOTLY_AVAILABLE = True
except ImportError:  # Streamlit's bundled Altair remains a local fallback.
    import altair as alt

    PLOTLY_AVAILABLE = False


PINKS = {"BASELINE": "#C9829F", "WIREGUARD": "#684B60"}
SERIES_PALETTE = ["#C9829F", "#A96F8B", "#684B60"]


def _label(value: float, decimals: int) -> str:
    return f"{value:.{decimals}f}"


def _loss_range(values: pd.Series) -> list[float]:
    maximum = float(values.max()) if not values.empty else 0.0
    if maximum <= 0:
        return [0.0, 0.0001]
    return [0.0, maximum * 1.3]


def comparison_chart(
    data: pd.DataFrame,
    metric: str,
    label: str,
    unit: str,
    decimals: int,
):
    chart_data = data[["target_rate", "condition", metric]].dropna().copy()
    chart_data["Nilai"] = chart_data[metric]
    chart_data["Label"] = chart_data["Nilai"].map(lambda value: _label(value, decimals))
    chart_data["condition"] = chart_data["condition"].replace(
        {"BASELINE": "Baseline", "WIREGUARD": "WireGuard"}
    )
    if PLOTLY_AVAILABLE:
        rates = [rate for rate in ["10M", "50M", "100M"] if rate in set(chart_data["target_rate"].astype(str))]
        value_table = chart_data.pivot_table(index="target_rate", columns="condition", values="Nilai", aggfunc="mean").reindex(rates)
        centers = list(range(len(rates)))
        baseline = value_table["Baseline"].tolist() if "Baseline" in value_table else [None] * len(rates)
        wireguard = value_table["WireGuard"].tolist() if "WireGuard" in value_table else [None] * len(rates)
        baseline = [None if pd.isna(value) else float(value) for value in baseline]
        wireguard = [None if pd.isna(value) else float(value) for value in wireguard]
        max_value = max([abs(value) for value in baseline + wireguard if value is not None] + [0.0])
        label_gap = max_value * 0.025 if max_value else 0.000001

        fig = go.Figure()
        for condition, values, color, center_shift, label_shift in [
            ("Baseline", baseline, PINKS["BASELINE"], -0.18, -0.31),
            ("WireGuard", wireguard, PINKS["WIREGUARD"], 0.18, 0.31),
        ]:
            bar_x = [center + center_shift for center in centers]
            fig.add_trace(
                go.Bar(
                    name=condition,
                    x=bar_x,
                    y=values,
                    width=0.34,
                    marker_color=color,
                    customdata=rates,
                    hovertemplate=f"Target bitrate %{{customdata}}<br>{condition}: %{{y:.{decimals}f}} {unit}<extra></extra>",
                )
            )
            valid_points = [
                (center + label_shift, value + label_gap, _label(value, decimals))
                for center, value in zip(centers, values)
                if value is not None
            ]
            if valid_points:
                label_x, label_y, label_text = zip(*valid_points)
                fig.add_trace(
                    go.Scatter(
                        x=label_x,
                        y=label_y,
                        text=label_text,
                        mode="text",
                        textposition="top center",
                        textfont=dict(size=9, color="#59434D"),
                        hoverinfo="skip",
                        showlegend=False,
                        cliponaxis=False,
                    )
                )
        fig.update_layout(
            template="plotly_white",
            height=430,
            margin=dict(t=42, b=45, l=30, r=30),
            font=dict(family="Inter, Aptos, Segoe UI, sans-serif", size=12, color="#59434D"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title_text=""),
            barmode="overlay",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        fig.update_xaxes(
            title="Target Bitrate",
            tickmode="array",
            tickvals=centers,
            ticktext=rates,
            range=[-0.62, max(len(rates) - 1, 0) + 0.62],
            showgrid=False,
            linecolor="#EADDE2",
            tickfont=dict(color="#806C76"),
        )
        fig.update_yaxes(showgrid=True, gridcolor="#F0E7EB", zeroline=False, tickfont=dict(color="#806C76"))
        fig.update_yaxes(title=f"{label} ({unit})")
        if metric == "packet_loss_percent":
            fig.update_yaxes(range=_loss_range(chart_data["Nilai"]), tickformat=".6f")
        else:
            fig.update_yaxes(rangemode="tozero")
        return fig

    y_scale = (
        alt.Scale(domain=_loss_range(chart_data["Nilai"]))
        if metric == "packet_loss_percent"
        else alt.Scale(zero=True)
    )
    y_axis = alt.Axis(
        gridColor="#F0E7EB",
        domainColor="#EADDE2",
        labelColor="#806C76",
        titleColor="#59434D",
        format=".6f" if metric == "packet_loss_percent" else "~g",
    )
    chart = (
        alt.Chart(chart_data)
        .mark_bar()
        .encode(
            x=alt.X("target_rate:N", sort=["10M", "50M", "100M"], title="Target Bitrate"),
            xOffset="condition:N",
            y=alt.Y("Nilai:Q", title=f"{label} ({unit})", scale=y_scale, axis=y_axis),
            color=alt.Color("condition:N", scale=alt.Scale(domain=["Baseline", "WireGuard"], range=[*PINKS.values()]), title="Kondisi"),
            tooltip=["target_rate", "condition", alt.Tooltip("Nilai:Q", format=f".{decimals}f")],
        )
        .properties(height=390)
    )
    labels = chart.mark_text(dy=-7, color="#59434D", fontSize=11).encode(text="Label:N")
    return (
        (chart + labels)
        .configure(background="transparent")
        .configure_axis(gridColor="#F0E7EB", labelFont="Inter, Aptos, Segoe UI, sans-serif", titleFont="Inter, Aptos, Segoe UI, sans-serif")
        .configure_legend(labelColor="#705A65", titleColor="#59434D", orient="top")
    )


def trend_chart(
    data: pd.DataFrame,
    metric: str,
    label: str,
    unit: str,
    decimals: int,
    factor: str,
    condition: str,
):
    chart_data = data[data["condition"] == condition].dropna(subset=[metric]).copy()
    chart_data["Nilai"] = chart_data[metric]
    chart_data["Label"] = chart_data["Nilai"].map(lambda value: _label(value, decimals))
    chart_data["Target Bitrate (Mbps)"] = chart_data["target_rate"].map({"10M": 10, "50M": 50, "100M": 100})
    if factor == "trafik":
        x = "Target Bitrate (Mbps)"
        series = "packet_size_bytes"
        color_title = "Ukuran Paket (byte)"
        chart_data[series] = chart_data[series].astype(str)
        category_order = ["128", "512", "1024"]
    else:
        x = "packet_size_bytes"
        series = "target_rate"
        color_title = "Target Bitrate"
        category_order = ["10M", "50M", "100M"]

    if PLOTLY_AVAILABLE:
        fig = px.line(
            chart_data,
            x=x,
            y="Nilai",
            color=series,
            markers=True,
            text="Label",
            category_orders={series: category_order},
            color_discrete_sequence=SERIES_PALETTE,
            labels={x: "Target Bitrate (Mbps)" if factor == "trafik" else "Ukuran Paket (byte)", "Nilai": f"{label} ({unit})", series: color_title},
        )
        label_positions = ["top center", "bottom center", "middle right"]
        for series_index, trace in enumerate(fig.data):
            trace.textposition = [
                label_positions[(series_index + point_index) % len(label_positions)]
                for point_index in range(len(trace.x))
            ]
            trace.cliponaxis = False
            trace.textfont = dict(size=9, color="#59434D")
        fig.update_layout(
            template="plotly_white",
            height=440,
            margin=dict(t=42, b=35, l=25, r=25),
            font=dict(family="Inter, Aptos, Segoe UI, sans-serif", size=12, color="#59434D"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title_text=color_title),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        fig.update_xaxes(showgrid=False, linecolor="#EADDE2", tickfont=dict(color="#806C76"))
        fig.update_yaxes(showgrid=True, gridcolor="#F0E7EB", zeroline=False, tickfont=dict(color="#806C76"))
        if factor == "trafik":
            fig.update_xaxes(tickmode="array", tickvals=[10, 50, 100])
        else:
            fig.update_xaxes(tickmode="array", tickvals=[128, 512, 1024])
        if metric == "packet_loss_percent":
            fig.update_yaxes(range=_loss_range(chart_data["Nilai"]), tickformat=".6f")
        return fig

    x_encoding = alt.X(f"{x}:Q", title="Target Bitrate (Mbps)" if factor == "trafik" else "Ukuran Paket (byte)")
    y_scale = (
        alt.Scale(domain=_loss_range(chart_data["Nilai"]))
        if metric == "packet_loss_percent"
        else alt.Scale(zero=False)
    )
    y_axis = alt.Axis(
        gridColor="#F0E7EB",
        domainColor="#EADDE2",
        labelColor="#806C76",
        titleColor="#59434D",
        format=".6f" if metric == "packet_loss_percent" else "~g",
    )
    chart = (
        alt.Chart(chart_data)
        .mark_line(point=alt.OverlayMarkDef(filled=True, size=70))
        .encode(
            x=x_encoding,
            y=alt.Y("Nilai:Q", title=f"{label} ({unit})", scale=y_scale, axis=y_axis),
            color=alt.Color(f"{series}:N", sort=category_order, scale=alt.Scale(range=SERIES_PALETTE), title=color_title),
            tooltip=[x, series, alt.Tooltip("Nilai:Q", format=f".{decimals}f")],
        )
        .properties(height=400)
    )
    labels = chart.mark_text(dy=-10, fontSize=10).encode(text="Label:N")
    return (
        (chart + labels)
        .configure(background="transparent")
        .configure_axis(gridColor="#F0E7EB", labelFont="Inter, Aptos, Segoe UI, sans-serif", titleFont="Inter, Aptos, Segoe UI, sans-serif")
        .configure_legend(labelColor="#705A65", titleColor="#59434D", orient="top")
    )
