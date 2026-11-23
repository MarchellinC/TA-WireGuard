
#!/bin/bash

# ==========================================
# SCRIPT TESTING AWAL WIREGUARD
# 1 skenario, 1 pengulangan
# ==========================================

SERVER_IP="10.10.0.1"
PACKET_SIZE=128
TRAFFIC_RATE="10M"
DURATION=10

BASE_DIR="/media/sf_Client/raw_data/testing"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
TEST_DIR="$BASE_DIR/TEST_${TIMESTAMP}"

mkdir -p "$TEST_DIR"

# Memeriksa interface WireGuard
if ! ip link show wg0 >/dev/null 2>&1; then
    echo "ERROR: Interface wg0 tidak ditemukan."
    exit 1
fi

# Memeriksa koneksi ke Server
if ! ping -c 1 -W 3 "$SERVER_IP" >/dev/null 2>&1; then
    echo "ERROR: Server WireGuard tidak dapat dijangkau."
    exit 1
fi

# Memeriksa iperf3
if ! command -v iperf3 >/dev/null 2>&1; then
    echo "ERROR: iperf3 belum terpasang."
    exit 1
fi

# Menyimpan metadata
{
    echo "======================================"
    echo "METADATA TESTING WIREGUARD"
    echo "======================================"
    echo "ID Pengujian    : TEST"
    echo "Tanggal         : $(date)"
    echo "Client          : $(hostname)"
    echo "Server IP       : $SERVER_IP"
    echo "Kondisi         : WireGuard aktif"
    echo "Protokol        : UDP"
    echo "Ukuran Datagram : $PACKET_SIZE byte"
    echo "Target Trafik   : $TRAFFIC_RATE"
    echo "Durasi          : $DURATION detik"
    echo "======================================"
} > "$TEST_DIR/metadata.txt"

echo "Folder hasil: $TEST_DIR"

# Mencatat log CPU
top -b -d 1 -n "$((DURATION + 2))" \
    > "$TEST_DIR/cpu.log" &
TOP_PID=$!

# Menjalankan ping selama pengujian berlangsung
ping -n -i 0.2 "$SERVER_IP" \
    > "$TEST_DIR/ping.log" 2>&1 &
PING_PID=$!

# Menjalankan pengujian UDP
echo "Menjalankan iperf3..."
iperf3 -c "$SERVER_IP" \
    -u \
    -b "$TRAFFIC_RATE" \
    -l "$PACKET_SIZE" \
    -t "$DURATION" \
    > "$TEST_DIR/iperf3.log" 2>&1

IPERF_STATUS=$?

# Menghentikan ping dan CPU setelah iperf3 selesai
kill "$PING_PID" 2>/dev/null
wait "$PING_PID" 2>/dev/null
wait "$TOP_PID" 2>/dev/null

# Menyimpan status pengujian
{
    echo
    echo "Waktu selesai : $(date)"
    echo "Status iperf3 : $IPERF_STATUS"
} >> "$TEST_DIR/metadata.txt"

echo
echo "=== TESTING SELESAI ==="
echo "Lokasi hasil: $TEST_DIR"
echo
ls -lh "$TEST_DIR"

if [ "$IPERF_STATUS" -ne 0 ]; then
    echo "PERINGATAN: Pengujian iperf3 gagal."
    exit 1
fi
