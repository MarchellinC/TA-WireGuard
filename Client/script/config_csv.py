from pathlib import Path

# Folder sumber data mentah
BASE_DIR = Path(
    "/media/sf_Client/raw_data/ta/all_skenario3"
)

# Folder hasil ekstraksi
OUTPUT_DIR = Path(
    "/media/sf_Client/processed_data/all_skenario3"
)

OUTPUT_CSV = OUTPUT_DIR / "raw_dataset.csv"

# Kolom csv raw dataset
COLUMNS = [
    "experiment_id",
    "packet_size_bytes",
    "target_rate",
    "condition",
    "repeat",
    "source",
    "iperf_status",
    "receiver_status",
    "throughput_mbps",
    "jitter_ms",
    "packet_loss_percent",
    "latency_ms",
    "cpu_client_percent",
    "cpu_server_percent",
    "cpu_client_samples",
    "cpu_server_samples",
    "notes",
]
