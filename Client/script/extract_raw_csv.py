import csv
import re

from config_csv import BASE_DIR, OUTPUT_DIR, OUTPUT_CSV, COLUMNS
from parse_logs import (
    read_metadata,
    parse_iperf,
    parse_ping,
    parse_cpu,
    fmt,
)


def main():
    if not BASE_DIR.is_dir():
        raise SystemExit(f"Folder tidak ditemukan: {BASE_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []

    for repeat_dir in sorted(
        BASE_DIR.glob("*bytes/*mbps/*/repeat[0-9]*")
    ):
        if not repeat_dir.is_dir():
            continue

        repeat_match = re.fullmatch(r"repeat(\d+)(_retest)?",repeat_dir.name)
        size_match = re.fullmatch(
            r"(\d+)bytes",
            repeat_dir.parent.parent.parent.name,
        )

        if not repeat_match or not size_match:
            continue

        condition = repeat_dir.parent.name.upper()

        if condition not in ("BASELINE", "WIREGUARD"):
            continue

        size = int(size_match.group(1))
        repeat_no = int(repeat_match.group(1))
        rate = repeat_dir.parent.parent.name.replace("mbps", "M")

        metadata = read_metadata(repeat_dir / "metadata.txt")
        iperf = parse_iperf(repeat_dir / "iperf3.log")
        latency = parse_ping(repeat_dir / "ping.log")

        cpu_client, client_samples = parse_cpu(
            repeat_dir / "cpu.log"
        )
        cpu_server, server_samples = parse_cpu(
            repeat_dir / "cpu_server.log"
        )

        iperf_status = metadata.get("Status iperf3", "")
        receiver_status = metadata.get(
            "Status receiver",
            str(iperf["receiver_status"]),
        )

        experiment_id = metadata.get("ID Pengujian", "")

        source = (
            "retest"
            if repeat_match.group(2) == "_retest"
            or "retest" in experiment_id.lower()
            else "original"
        )

        notes = []

        if iperf_status != "0":
            notes.append("iperf3 status missing/failed")
        if receiver_status != "0":
            notes.append("receiver missing/failed")
        if iperf["throughput_mbps"] is None:
            notes.append("throughput not parsed")
        if iperf["jitter_ms"] is None:
            notes.append("jitter not parsed")
        if iperf["packet_loss_percent"] is None:
            notes.append("packet loss not parsed")
        if latency is None:
            notes.append("latency not parsed")
        if cpu_client is None:
            notes.append("client CPU not parsed")
        if cpu_server is None:
            notes.append("server CPU not parsed")

        rows.append({
            "experiment_id": experiment_id,
            "packet_size_bytes": size,
            "target_rate": rate,
            "condition": condition,
            "repeat": repeat_no,
            "source": source,
            "iperf_status": iperf_status,
            "receiver_status": receiver_status,
            "throughput_mbps": fmt(iperf["throughput_mbps"]),
            "jitter_ms": fmt(iperf["jitter_ms"]),
            "packet_loss_percent": fmt(
                iperf["packet_loss_percent"]
            ),
            "latency_ms": fmt(latency),
            "cpu_client_percent": fmt(cpu_client),
            "cpu_server_percent": fmt(cpu_server),
            "cpu_client_samples": client_samples,
            "cpu_server_samples": server_samples,
            "notes": "; ".join(notes),
        })

    rows.sort(key=lambda row: (
        int(row["packet_size_bytes"]),
        int(row["target_rate"].replace("M", "")),
        {"BASELINE": 0, "WIREGUARD": 1}[row["condition"]],
        row["repeat"],
        {"original": 0, "retest": 1}[row["source"]],
    ))

    with OUTPUT_CSV.open(
        "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print("=== EKSTRAKSI CSV SELESAI ===")
    print(f"Jumlah baris data : {len(rows)}")
    print(f"Lokasi output     : {OUTPUT_CSV}")

    flagged = sum(bool(row["notes"]) for row in rows)
    print(f"Baris perlu dicek : {flagged}")

    if len(rows) != 90:
        print("PERINGATAN: Jumlah data bukan 90. Periksa struktur folder.")


if __name__ == "__main__":
    main()
