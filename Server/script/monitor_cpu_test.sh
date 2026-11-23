#!/bin/bash

# Pemantauan CPU Ubuntu-Server
# Penggunaan: bash monitor_cpu.sh NAMA_PENGUJIAN DURASI

TEST_ID="$1"
DURATION="$2"
BASE_DIR="/media/sf_Server/raw_data/ta/$TEST_ID"

if [ -z "$TEST_ID" ] || [ -z "$DURATION" ]; then
    echo "Penggunaan: bash monitor_cpu.sh NAMA_PENGUJIAN DURASI"
    exit 1
fi

if ! [[ "$DURATION" =~ ^[0-9]+$ ]] || [ "$DURATION" -lt 1 ]; then
    echo "Durasi harus berupa bilangan bulat positif."
    exit 1
fi

mkdir -p "$BASE_DIR"

LOG_FILE="$BASE_DIR/cpu_server.log"

echo "Mulai pemantauan CPU Server"
echo "Hostname : $(hostname)"
echo "Pengujian: $TEST_ID"
echo "Durasi   : $DURATION detik"
echo "Log      : $LOG_FILE"

{
    echo "ID Pengujian : $TEST_ID"
    echo "Hostname     : $(hostname)"
    echo "Waktu mulai  : $(date --iso-8601=seconds)"
    echo "Durasi       : $DURATION detik"
    echo "Format       : top batch mode, interval 1 detik"
    echo
} > "$LOG_FILE"

top -b -d 1 -n "$DURATION" >> "$LOG_FILE" 2>&1

{
    echo
    echo "Waktu selesai: $(date --iso-8601=seconds)"
} >> "$LOG_FILE"

echo "Pemantauan selesai."
echo "Hasil tersimpan di: $LOG_FILE"
