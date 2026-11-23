#!/bin/bash

SCRIPT_DIR="/media/sf_Client/script"

source "$SCRIPT_DIR/config.sh"
source "$SCRIPT_DIR/test_condition.sh"

# Gunakan ID eksperimen khusus untuk retest
RETEST_ID="${EXPERIMENT_ID}_retest"
RETEST_DIR="$BASE_DIR/all_skenario3/1024bytes/10mbps/BASELINE/repeat5_retest"

# Parameter pengujian
SIZE=1024
RATE="10M"
LABEL="BASELINE"
TARGET_IP="$PHYSICAL_IP"
REPEAT_NO=5

# Pastikan folder output belum ada
if [[ -e "$RETEST_DIR" ]]; then
    echo "ERROR: Folder retest sudah ada: $RETEST_DIR"
    echo "Simpan hasil lama atau gunakan folder baru."
    exit 1
fi

# Arahkan output run_condition ke folder retest
RUN_DIR="$BASE_DIR/all_skenario3"
EXPERIMENT_ID="$RETEST_ID"

# Pastikan WireGuard mati untuk Baseline
if ip link show wg0 >/dev/null 2>&1; then
    sudo wg-quick down wg0 || exit 1
fi

# Pastikan Server dapat dijangkau
if ! ping -c 4 "$TARGET_IP"; then
    echo "ERROR: Server tidak dapat dijangkau."
    exit 1
fi

echo ""
echo "Mengulang skenario:"
echo "1024 bytes / 10M / BASELINE / Repeat 5"
echo ""

if run_condition "$SIZE" "$RATE" "$LABEL" "$TARGET_IP" "$REPEAT_NO" "$RETEST_DIR"; then
    echo "Retest berhasil."
else
    echo "Retest gagal. Periksa log pengujian."
    exit 1
fi
