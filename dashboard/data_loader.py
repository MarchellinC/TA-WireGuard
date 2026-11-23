"""Load and validate the experiment dataset using the notebook's rules."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV_PATH = (
    PROJECT_ROOT / "Client" / "processed_data" / "all_skenario3" / "raw_dataset.csv"
)

METRICS = [
    "throughput_mbps",
    "latency_ms",
    "jitter_ms",
    "packet_loss_percent",
    "cpu_client_percent",
    "cpu_server_percent",
]
GROUP_COLUMNS = ["packet_size_bytes", "target_rate", "condition"]
REQUIRED_COLUMNS = [
    "experiment_id",
    "packet_size_bytes",
    "target_rate",
    "condition",
    "iperf_status",
    "receiver_status",
    *METRICS,
]


class DatasetError(ValueError):
    """Raised when the dashboard's source CSV is missing or incompatible."""


@st.cache_data(show_spinner=False)
def load_dataset(csv_path: str | Path = DEFAULT_CSV_PATH) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return raw and notebook-valid rows from the experiment CSV."""
    path = Path(csv_path).expanduser().resolve()
    if not path.is_file():
        raise DatasetError(f"CSV tidak ditemukan: {path}")

    try:
        raw = pd.read_csv(path)
    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        raise DatasetError(f"CSV tidak dapat dibaca: {exc}") from exc

    missing = sorted(set(REQUIRED_COLUMNS) - set(raw.columns))
    if missing:
        raise DatasetError("Kolom wajib tidak tersedia: " + ", ".join(missing))

    # Match the source notebook: success status 0 and all six metrics present.
    for column in ["iperf_status", "receiver_status", *METRICS, "packet_size_bytes"]:
        raw[column] = pd.to_numeric(raw[column], errors="coerce")

    valid_mask = (
        raw["iperf_status"].eq(0)
        & raw["receiver_status"].eq(0)
        & raw[METRICS].notna().all(axis=1)
    )
    valid = raw.loc[valid_mask].copy()
    if valid.empty:
        raise DatasetError(
            "Tidak ada baris valid. Baris valid harus memiliki status iperf3 dan receiver 0 "
            "serta seluruh metrik terisi."
        )
    return raw, valid


def aggregate_dataset(valid: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return mean aggregates and descriptive statistics grouped like the notebook."""
    means = valid.groupby(GROUP_COLUMNS)[METRICS].mean().reset_index()
    stats = (
        valid.groupby(GROUP_COLUMNS)[METRICS]
        .agg(["count", "mean", "std", "min", "max"])
        .reset_index()
    )
    return means, stats
