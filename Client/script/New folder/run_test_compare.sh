#!/bin/bash

# ==========================================
# PERBANDINGAN BASELINE vs WIREGUARD
# Satu pengujian untuk setiap kondisi
# ==========================================

PHYSICAL_IP="192.168.56.101"
WG_IP="10.10.0.1"

PACKET_SIZE=128
TRAFFIC_RATE="10M"
DURATION=10

BASE_DIR="/media/sf_Client/raw_data/testing"
TEST_DIR="$BASE_DIR/COMPARE_004"

if [ -e "$TEST_DIR" ]; then
    echo "ERROR: Folder $TEST_DIR sudah ada."
    echo "Ganti COMPARE_003 menjadi COMPARE_004 jika ingin tes baru."
    exit 1
fi

mkdir -p "$TEST_DIR"

# Pastikan tools tersedia
if ! command -v iperf3 >/dev/null 2>&1; then
    echo "ERROR: iperf3 belum terpasang."
    exit 1
fi

if ! command -v ping >/dev/null 2>&1; then
    echo "ERROR: ping tidak tersedia."
    exit 1
fi

if ! ip link show wg0 >/dev/null 2>&1; then
    echo "ERROR: Interface wg0 tidak ditemukan."
    exit 1
fi

# Minta autentikasi sudo sebelum pengujian
if ! sudo -v; then
    echo "ERROR: Autentikasi sudo gagal."
    exit 1
fi

# Pulihkan WireGuard jika script terhenti ketika tunnel mati
restore_wg() {
    if ! ip link show wg0 >/dev/null 2>&1; then
        echo "Memulihkan interface WireGuard..."
        sudo wg-quick up wg0
    fi
}

trap restore_wg EXIT


# Fungsi menjalankan satu kondisi pengujian
run_condition() {
    LABEL="$1"
    SERVER_IP="$2"
    CONDITION_DIR="$TEST_DIR/$LABEL"
    REMOTE_TEST_ID="$(basename "$TEST_DIR")_${LABEL}"
    SERVER_CPU_PATH="/media/sf_Server/raw_data/testing/$REMOTE_TEST_ID/cpu_server.log"

    mkdir -p "$CONDITION_DIR"

    {
        echo "ID Pengujian : $LABEL"
        echo "Tanggal      : $(date)"
        echo "Client       : $(hostname)"
        echo "Server IP    : $SERVER_IP"
        echo "Protokol     : UDP"
        echo "Ukuran       : $PACKET_SIZE byte"
        echo "Target       : $TRAFFIC_RATE"
        echo "Durasi       : $DURATION detik"
    } > "$CONDITION_DIR/metadata.txt"

    # Pastikan server dapat dijangkau
    if ! ping -c 1 -W 3 "$SERVER_IP" \
        > "$CONDITION_DIR/connectivity.log" 2>&1; then
        echo "ERROR: Server tidak dapat dijangkau: $SERVER_IP"
        echo "Status: GAGAL - konektivitas" >> "$CONDITION_DIR/metadata.txt"
        return 1
    fi

    # Pastikan script monitor CPU Server tersedia
    if ! ssh -o BatchMode=yes "marchellinc@${PHYSICAL_IP}" \
        "test -f /media/sf_Server/script/monitor_cpu_test.sh"; then
        echo "ERROR: Script monitor CPU Server tidak ditemukan."
        return 1
    fi

    # Mulai merekam CPU Server melalui SSH
    ssh -o BatchMode=yes "marchellinc@${PHYSICAL_IP}" \
        "bash /media/sf_Server/script/monitor_cpu_test.sh '$REMOTE_TEST_ID' '$((DURATION + 2))'" \
        > "$CONDITION_DIR/ssh_cpu_monitor.log" 2>&1 &
    SERVER_MONITOR_PID=$!

    # Catat CPU Client
    top -b -d 1 -n "$((DURATION + 2))" \
        > "$CONDITION_DIR/cpu.log" 2>&1 &
    TOP_PID=$!

    # Catat RTT selama pengujian
    ping -n -i 0.2 "$SERVER_IP" \
        > "$CONDITION_DIR/ping.log" 2>&1 &
    PING_PID=$!

    echo "Menjalankan iperf3: $LABEL"

    iperf3 -c "$SERVER_IP" \
        -u \
        -b "$TRAFFIC_RATE" \
        -l "$PACKET_SIZE" \
        -t "$DURATION" \
        > "$CONDITION_DIR/iperf3.log" 2>&1

    IPERF_STATUS=$?

    kill "$PING_PID" 2>/dev/null
    wait "$PING_PID" 2>/dev/null
    wait "$TOP_PID" 2>/dev/null

    # Tunggu pemantauan CPU Server selesai
    wait "$SERVER_MONITOR_PID"
    SERVER_MONITOR_STATUS=$?

    # Salin log CPU Server ke folder hasil Client
    if [ "$SERVER_MONITOR_STATUS" -eq 0 ]; then
        if ! scp -o BatchMode=yes \
            "marchellinc@${PHYSICAL_IP}:${SERVER_CPU_PATH}" \
            "$CONDITION_DIR/cpu_server.log"; then
            echo "ERROR: Gagal mengambil log CPU Server."
            SERVER_MONITOR_STATUS=1
        fi
    else
        echo "ERROR: Pemantauan CPU Server gagal."
    fi

    {
        echo "Waktu selesai: $(date)"
        echo "Status iperf3: $IPERF_STATUS"
        echo "Status monitor CPU Server: $SERVER_MONITOR_STATUS"
    } >> "$CONDITION_DIR/metadata.txt"

    if [ "$IPERF_STATUS" -ne 0 ] || [ "$SERVER_MONITOR_STATUS" -ne 0 ]; then
        echo "ERROR: Pengujian $LABEL belum lengkap. Periksa log."
        return 1
    fi

    echo "Selesai: $LABEL"
    return 0
}

# ==========================================
# KONDISI 1: BASELINE TANPA TUNNEL WIREGUARD
# ==========================================

echo
echo "=== KONDISI 1: BASELINE ==="

if ! sudo wg-quick down wg0; then
    echo "ERROR: Gagal menonaktifkan WireGuard pada Client."
    exit 1
fi

if ! run_condition "BASELINE" "$PHYSICAL_IP"; then
    echo "Pengujian baseline gagal. Periksa log."
    exit 1
fi

# ==========================================
# AKTIFKAN KEMBALI WIREGUARD
# ==========================================

echo
echo "Mengaktifkan kembali WireGuard..."

if ! sudo wg-quick up wg0; then
    echo "ERROR: Gagal mengaktifkan WireGuard."
    exit 1
fi

if ! ping -c 1 -W 3 "$WG_IP"; then
    echo "ERROR: Tunnel belum dapat menjangkau server."
    exit 1
fi

# ==========================================
# KONDISI 2: MELALUI WIREGUARD
# ==========================================

echo
echo "=== KONDISI 2: WIREGUARD ==="

if ! run_condition "WIREGUARD" "$WG_IP"; then
    echo "Pengujian WireGuard gagal. Periksa log."
    exit 1
fi

echo
echo "=== PERBANDINGAN SELESAI ==="
echo "Lokasi hasil: $TEST_DIR"
ls -lh "$TEST_DIR/BASELINE"
ls -lh "$TEST_DIR/WIREGUARD"
