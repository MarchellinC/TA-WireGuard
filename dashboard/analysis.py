"""Metric definitions and reusable analysis helpers."""

from __future__ import annotations

import pandas as pd


RATE_ORDER = {"10M": 10, "50M": 50, "100M": 100}
CONDITIONS = ["BASELINE", "WIREGUARD"]
PACKET_SIZES = [128, 512, 1024]

METRIC_INFO = {
    "throughput_mbps": {
        "label": "Throughput",
        "unit": "Mbps",
        "description": "Kecepatan data yang diterima selama pengujian transfer.",
        "decimals": 2,
    },
    "latency_ms": {
        "label": "Latency / RTT",
        "unit": "ms",
        "description": "Waktu bolak-balik paket berdasarkan pengukuran ping.",
        "decimals": 2,
    },
    "jitter_ms": {
        "label": "Jitter",
        "unit": "ms",
        "description": "Variasi waktu kedatangan paket yang dilaporkan iperf3.",
        "decimals": 3,
    },
    "packet_loss_percent": {
        "label": "Packet Loss",
        "unit": "%",
        "description": "Persentase paket yang hilang selama pengujian trafik.",
        "decimals": 6,
    },
    "cpu_client_percent": {
        "label": "CPU Utilization Client",
        "unit": "%",
        "description": "Rata-rata penggunaan CPU pada mesin Client.",
        "decimals": 2,
    },
    "cpu_server_percent": {
        "label": "CPU Utilization Server",
        "unit": "%",
        "description": "Rata-rata penggunaan CPU pada mesin Server.",
        "decimals": 2,
    },
}


def sorted_rates(values: pd.Series) -> list[str]:
    return sorted(values.dropna().astype(str).unique(), key=lambda value: RATE_ORDER.get(value, 999))


def scenario_count(valid: pd.DataFrame) -> int:
    """Count unique packet-size × target-rate combinations represented in valid data."""
    return int(valid[["packet_size_bytes", "target_rate"]].drop_duplicates().shape[0])


def percent_change(means: pd.DataFrame, metric: str) -> pd.DataFrame:
    """Calculate WireGuard change relative to Baseline, preserving undefined zero cases."""
    pivot = means.pivot_table(
        index=["packet_size_bytes", "target_rate"],
        columns="condition",
        values=metric,
        aggfunc="mean",
    )
    if not {"BASELINE", "WIREGUARD"}.issubset(pivot.columns):
        return pd.DataFrame(columns=["packet_size_bytes", "target_rate", "change_percent"])
    base = pivot["BASELINE"].abs().replace(0, float("nan"))
    result = ((pivot["WIREGUARD"] - pivot["BASELINE"]) / base * 100).rename("change_percent")
    return result.reset_index()
