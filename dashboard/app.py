"""Streamlit dashboard for WireGuard transfer performance experiments."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Streamlit and AppTest do not always add the script directory to sys.path.
_DASHBOARD_DIR = str(Path(__file__).resolve().parent)
if _DASHBOARD_DIR not in sys.path:
    sys.path.insert(0, _DASHBOARD_DIR)

from analysis import (
    CONDITIONS,
    METRIC_INFO,
    PACKET_SIZES,
    percent_change,
    scenario_count,
)
from charts import PLOTLY_AVAILABLE, comparison_chart, trend_chart
from data_loader import DatasetError, aggregate_dataset, load_dataset
from styles import apply_styles


st.set_page_config(
    page_title="Analisis Kinerja WireGuard",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_styles()


def hero(kicker: str, title: str, copy: str) -> None:
    st.markdown(
        f'<section class="hero"><div class="hero-kicker">{kicker}</div>'
        f'<div class="hero-title">{title}</div><p class="hero-copy">{copy}</p></section>',
        unsafe_allow_html=True,
    )


def info_card(title: str, body: str, tone: str = "rose") -> None:
    tone_class = {"rose": "parameter-item--rose", "mauve": "parameter-item--mauve", "lavender": "parameter-item--lavender"}.get(tone, "parameter-item--rose")
    st.markdown(
        f'<div class="parameter-item {tone_class}"><h4>{title}</h4><p>{body}</p></div>',
        unsafe_allow_html=True,
    )


def show_chart(chart, key: str) -> None:
    if PLOTLY_AVAILABLE:
        st.plotly_chart(
            chart,
            key=key,
            use_container_width=True,
            config={
                "displaylogo": False,
                "responsive": True,
                "modeBarButtonsToRemove": ["select2d", "lasso2d", "zoom2d", "autoScale2d"],
            },
        )
    else:
        st.altair_chart(chart, key=key, use_container_width=True)


def sidebar_navigation() -> str:
    with st.sidebar:
        st.markdown(
            "<div class='brand-lockup'><div class='brand-name'>WIREGUARD RESEARCH</div>"
            "<div class='brand-subtitle'>Dashboard penelitian tugas akhir</div></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='researcher-card'><div class='researcher-label'>Peneliti</div>"
            "<div class='researcher-name'>Marchellin Chenika</div>"
            "<div class='researcher-meta'><strong>NPM</strong> &nbsp;140810230002</div>"
            "<div class='researcher-meta'><strong>Program Studi</strong><br>Teknik Informatika</div>"
            "<div class='researcher-meta'><strong>Fakultas</strong><br>Matematika dan Ilmu Pengetahuan Alam</div>"
            "<div class='researcher-meta'><strong>Universitas</strong><br>Universitas Padjadjaran</div></div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div class='sidebar-section-title'>Ruang Lingkup</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='research-fact'><div class='research-fact-label'>Objek</div>"
            "<div class='research-fact-value'>WireGuard VPN</div></div>"
            "<div class='research-fact'><div class='research-fact-label'>Lingkungan</div>"
            "<div class='research-fact-value'>Linux Virtual Machine · VirtualBox</div></div>"
            "<div class='research-fact'><div class='research-fact-label'>Metode</div>"
            "<div class='research-fact-value'>Eksperimen komparatif Baseline dan WireGuard</div></div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div class='sidebar-section-title'>Navigasi</div>", unsafe_allow_html=True)
        return st.radio(
            "Navigasi",
            ["Dashboard", "Analisis Grafik", "Tentang Proyek"],
            label_visibility="collapsed",
        )


def render_dashboard(raw, valid) -> None:
    hero(
        "WireGuard Research Dashboard",
        "Analisis Kinerja Transfer Data dengan WireGuard",
        "Perbandingan kondisi Baseline dan WireGuard pada variasi ukuran paket dan target bitrate di lingkungan Linux virtual.",
    )
    excluded = len(raw) - len(valid)
    scenario_total = scenario_count(valid)
    condition_total = int(valid["condition"].nunique())

    a, b, c, d = st.columns([1, 1, 1, 0.72])
    a.metric("Data valid", f"{len(valid):,}", help="Status iperf3 dan receiver berhasil, dengan semua metrik utama terisi.")
    b.metric("Skenario", f"{scenario_total}", help="Kombinasi unik ukuran paket dan target bitrate pada data valid.")
    c.metric("Kondisi", f"{condition_total}", help="Kondisi eksperimen yang tercatat pada data valid.")
    d.metric("Data dikecualikan", f"{excluded:,}", help="Baris yang tidak lolos aturan validasi notebook.")

    st.markdown("### Rancangan Pengujian")
    x, y = st.columns(2, gap="large")
    with x:
        st.metric("Variasi ukuran paket", "128 · 512 · 1024 byte")
    with y:
        st.metric("Target intensitas trafik", "10 · 50 · 100 Mbps")

    st.markdown("### Parameter yang diamati")
    items = list(METRIC_INFO.values())
    tones = ["rose", "mauve", "lavender"]
    for start in range(0, len(items), 3):
        columns = st.columns(3, gap="large")
        for offset, (column, item) in enumerate(zip(columns, items[start : start + 3])):
            with column:
                info_card(item["label"], f'{item["description"]} Satuan: {item["unit"]}.', tones[offset])
def render_analysis(means) -> None:
    hero(
        "WireGuard Research Dashboard",
        "Analisis Grafik",
        "Pilih parameter untuk membandingkan nilai rata-rata dan melihat pengaruh target trafik maupun ukuran paket. Semua agregat mengikuti pengelompokan notebook.",
    )
    if not PLOTLY_AVAILABLE:
        st.caption("Grafik memakai renderer Altair yang tersedia pada instalasi ini.")

    st.markdown("**Parameter penelitian**")
    metric_label = st.selectbox("Parameter", [item["label"] for item in METRIC_INFO.values()], label_visibility="collapsed")
    metric = next(key for key, item in METRIC_INFO.items() if item["label"] == metric_label)
    info = METRIC_INFO[metric]
    st.caption(info["description"])

    st.divider()
    comparison_tab, traffic_tab, packet_tab = st.tabs(
        ["Baseline vs WireGuard", "Berdasarkan Intensitas Trafik", "Berdasarkan Ukuran Paket"]
    )
    with comparison_tab:
        st.markdown(f"#### {info['label']} menurut ukuran paket")
        size_tabs = st.tabs([f"{size} byte" for size in PACKET_SIZES])
        for tab, size in zip(size_tabs, PACKET_SIZES):
            with tab:
                data = means[means["packet_size_bytes"] == size]
                if data.empty:
                    st.info("Belum ada pasangan data untuk ukuran paket ini.")
                else:
                    with st.container(border=True):
                        st.markdown(f"#### Baseline dan WireGuard · paket {size} byte")
                        st.caption(f"Rata-rata {info['label'].lower()} pada tiap target bitrate ({info['unit']}).")
                        show_chart(
                            comparison_chart(data, metric, info["label"], info["unit"], info["decimals"]),
                            key=f"comparison_{metric}_{size}",
                        )
        changes = percent_change(means, metric)
        if not changes.empty:
            with st.expander("Lihat perubahan WireGuard terhadap Baseline"):
                display_changes = changes.copy()
                display_changes["packet_size_bytes"] = display_changes["packet_size_bytes"].astype(str) + " byte"
                display_changes["change_percent"] = display_changes["change_percent"].map(
                    lambda value: "—" if pd_isna(value) else f"{value:.2f}%"
                )
                display_changes = display_changes.rename(
                    columns={"packet_size_bytes": "Ukuran Paket", "target_rate": "Target Bitrate", "change_percent": "Perubahan"}
                )
                st.dataframe(display_changes, hide_index=True, use_container_width=True)

    with traffic_tab:
        st.markdown(f"#### Pengaruh target bitrate terhadap {info['label'].lower()}")
        render_trend_pair(means, metric, info, factor="trafik")

    with packet_tab:
        st.markdown(f"#### Pengaruh ukuran paket terhadap {info['label'].lower()}")
        render_trend_pair(means, metric, info, factor="ukuran")


def pd_isna(value) -> bool:
    return value != value


def render_trend_pair(means, metric, info, factor: str) -> None:
    columns = st.columns(2, gap="large")
    for column, condition in zip(columns, CONDITIONS):
        with column:
            with st.container(border=True):
                condition_label = "WireGuard" if condition == "WIREGUARD" else "Baseline"
                st.markdown(f"#### {condition_label}")
                if factor == "trafik":
                    st.caption("Sumbu X menunjukkan target bitrate; setiap garis mewakili ukuran paket.")
                else:
                    st.caption("Sumbu X menunjukkan ukuran paket; setiap garis mewakili target bitrate.")
                data = means[means["condition"] == condition]
                if data.empty:
                    st.info("Data kondisi ini belum tersedia.")
                else:
                    show_chart(
                        trend_chart(data, metric, info["label"], info["unit"], info["decimals"], factor, condition),
                        key=f"trend_{factor}_{metric}_{condition.lower()}",
                    )


def render_about(raw, valid) -> None:
    hero(
        "WireGuard Research Dashboard",
        "Tentang Proyek",
        "Eksperimen komparatif untuk memahami perubahan kinerja transfer data ketika WireGuard diterapkan pada jaringan Linux virtual.",
    )
    left, right = st.columns([1.05, 1], gap="large")
    with left:
        with st.container(border=True):
            st.markdown("<div class='section-label'>Konteks</div><h3>Latar Belakang</h3>", unsafe_allow_html=True)
            st.write(
                "WireGuard merupakan VPN yang melindungi komunikasi melalui mekanisme enkripsi. "
                "Penerapannya dapat berkaitan dengan perubahan kinerja transfer data dan penggunaan sumber daya sistem. "
                "Dashboard ini menyajikan hasil eksperimen tanpa menambahkan data simulasi."
            )
        with st.container(border=True):
            st.markdown("<div class='section-label'>Fokus Studi</div><h3>Tujuan Penelitian</h3>", unsafe_allow_html=True)
            st.write(
                "Menganalisis dampak penerapan WireGuard terhadap kinerja transfer data pada berbagai ukuran paket "
                "dan intensitas trafik di lingkungan Linux virtual."
            )
    with right:
        with st.container(border=True, key="environment-card"):
            st.markdown("<div class='section-label'>Setup Eksperimen</div><h3>Lingkungan Pengujian</h3>", unsafe_allow_html=True)
            st.markdown("Dua Virtual Machine Ubuntu Linux berkomunikasi sebagai Client dan Server melalui Oracle VM VirtualBox.")
            with st.container(border=True, key="tools-card"):
                st.markdown("<div class='section-label tools-label'>Perangkat dan Tools</div>", unsafe_allow_html=True)
                st.markdown(
                    "<div class='tool-list'>"
                    "<div class='tool-item'><strong>WireGuard</strong><br>VPN</div>"
                    "<div class='tool-item'><strong>iperf3</strong><br>Pengujian trafik</div>"
                    "<div class='tool-item'><strong>ping</strong><br>Pengukuran RTT</div>"
                    "<div class='tool-item'><strong>top</strong><br>Utilisasi CPU</div>"
                    "</div>",
                    unsafe_allow_html=True,
                )
    st.markdown("### Alur Penelitian")
    st.caption("Tahapan eksperimen dari persiapan lingkungan hingga analisis hasil.")
    steps = [
        "Persiapan lingkungan pengujian",
        "Konfigurasi jaringan dan WireGuard",
        "Pengujian kondisi Baseline",
        "Pengujian kondisi WireGuard",
        "Pengumpulan data",
        "Preprocessing dan validasi data",
        "Analisis dan visualisasi hasil",
    ]
    for row_start in range(0, len(steps), 4):
        row_steps = steps[row_start : row_start + 4]
        cols = st.columns(len(row_steps), gap="large")
        for index, (column, step) in enumerate(zip(cols, row_steps), start=row_start):
            with column:
                with st.container(border=True):
                    st.markdown(
                        f"<div class='timeline-number'>TAHAP {index + 1:02d}</div>"
                        f"<div class='timeline-text'>{step}</div>",
                        unsafe_allow_html=True,
                    )
    st.caption(f"Dataset memuat {len(raw)} baris; {len(valid)} baris memenuhi aturan validasi notebook.")


def main() -> None:
    page = sidebar_navigation()
    try:
        raw, valid = load_dataset()
        means, _stats = aggregate_dataset(valid)
    except DatasetError as exc:
        st.error(str(exc))
        st.info("Pastikan file `Client/processed_data/all_skenario3/raw_dataset.csv` tersedia dan memiliki format yang sesuai.")
        st.stop()

    if page == "Dashboard":
        render_dashboard(raw, valid)
    elif page == "Analisis Grafik":
        render_analysis(means)
    else:
        render_about(raw, valid)


if __name__ == "__main__":
    main()
