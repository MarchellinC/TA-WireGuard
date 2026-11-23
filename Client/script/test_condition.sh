#!/bin/bash

# PID proses yang sedang berjalan
ACTIVE_PIDS=()

cleanup_active_processes() {
    echo ""
    echo "Cleanup: menghentikan proses pengujian yang masih aktif..."

    for PID in "${ACTIVE_PIDS[@]}"; do
        if [[ -n "$PID" ]] && kill -0 "$PID" 2>/dev/null; then
            kill -TERM "$PID" 2>/dev/null || true
        fi
    done

    # Tunggu sebentar agar proses berhenti secara normal
    sleep 1

    for PID in "${ACTIVE_PIDS[@]}"; do
        if [[ -n "$PID" ]] && kill -0 "$PID" 2>/dev/null; then
            kill -KILL "$PID" 2>/dev/null || true
        fi
    done

    ACTIVE_PIDS=()
}

run_condition() {
    local SIZE="$1"
    local RATE="$2"
    local LABEL="$3"
    local TARGET_IP="$4"
    local REPEAT_NO="$5"

    local RATE_LABEL="${RATE%M}mbps"
    local COND_DIR="${6:-$RUN_DIR/${SIZE}bytes/$RATE_LABEL/$LABEL/repeat${REPEAT_NO}}"
    local REMOTE_TEST_ID="${EXPERIMENT_ID}_${SIZE}bytes_${RATE_LABEL}_${LABEL}_repeat${REPEAT_NO}"

    local MONITOR_PID=""
    local CPU_PID=""
    local PING_PID=""

    mkdir -p "$COND_DIR" || return 1

    echo "Menjalankan $LABEL: ${SIZE} bytes / $RATE / Repeat $REPEAT_NO"

    {
        echo "ID Pengujian : $REMOTE_TEST_ID"
        echo "Tanggal      : $(date)"
        echo "Client       : $(hostname)"
        echo "Server IP    : $TARGET_IP"
        echo "Protokol     : UDP"
        echo "Ukuran       : $SIZE byte"
        echo "Target       : $RATE"
        echo "Durasi       : $DURATION detik"
        echo "Kondisi      : $LABEL"
        echo "Repeat       : $REPEAT_NO"
    } > "$COND_DIR/metadata.txt"

    if ! ping -c 2 -W 2 "$TARGET_IP" \
        > "$COND_DIR/connectivity.log" 2>&1; then
        echo "Status iperf3: SKIPPED (koneksi gagal)" \
            >> "$COND_DIR/metadata.txt"
        echo "ERROR: Target tidak dapat dijangkau."
        return 1
    fi

    # Memulai monitor CPU server
    ssh "$SERVER_USER@$PHYSICAL_IP" \
        "bash '$SERVER_MONITOR' '$REMOTE_TEST_ID' '$MONITOR_DURATION'" \
        > "$COND_DIR/ssh_cpu_monitor.log" 2>&1 &
    MONITOR_PID=$!
    ACTIVE_PIDS+=("$MONITOR_PID")

    # Monitor CPU client
    top -b -d 1 -n "$((DURATION + 3))" \
        > "$COND_DIR/cpu.log" 2>&1 &
    CPU_PID=$!
    ACTIVE_PIDS+=("$CPU_PID")

    # Monitor RTT/ping
    ping -i 0.2 "$TARGET_IP" \
        > "$COND_DIR/ping.log" 2>&1 &
    PING_PID=$!
    ACTIVE_PIDS+=("$PING_PID")

    # Jeda proses monitoring mulai
    sleep 2

    # Menjalankan pengukuran UDP
    iperf3 -c "$TARGET_IP" \
        -u -b "$RATE" -l "$SIZE" -t "$DURATION" \
        > "$COND_DIR/iperf3.log" 2>&1
    local IPERF_STATUS=$?

    # Menghentikan monitor client
    kill "$PING_PID" 2>/dev/null || true
    wait "$PING_PID" 2>/dev/null || true
    PING_PID=""

    wait "$CPU_PID" 2>/dev/null
    local CPU_STATUS=$?
    CPU_PID=""

    # Menunggu monitor server selesai
    wait "$MONITOR_PID"
    local MONITOR_STATUS=$?
    MONITOR_PID=""

    # Salin log CPU server
    scp "$SERVER_USER@$PHYSICAL_IP:$SERVER_LOG_ROOT/$REMOTE_TEST_ID/cpu_server.log" \
        "$COND_DIR/cpu_server.log" \
        > "$COND_DIR/scp_cpu.log" 2>&1
    local SCP_STATUS=$?

    # Validasi dasar hasil iperf3
    local RECEIVER_STATUS=0

    if [[ ! -s "$COND_DIR/iperf3.log" ]] ||
       ! grep -qi "receiver" "$COND_DIR/iperf3.log"; then
        RECEIVER_STATUS=1
    fi

    {
        echo "Waktu selesai          : $(date)"
        echo "Status iperf3           : $IPERF_STATUS"
        echo "Status receiver         : $RECEIVER_STATUS"
        echo "Status CPU client       : $CPU_STATUS"
        echo "Status monitor CPU server: $MONITOR_STATUS"
        echo "Status salin CPU server : $SCP_STATUS"
    } >> "$COND_DIR/metadata.txt"

    if [[ $IPERF_STATUS -eq 0 &&
          $RECEIVER_STATUS -eq 0 &&
          $CPU_STATUS -eq 0 &&
          $MONITOR_STATUS -eq 0 &&
          $SCP_STATUS -eq 0 ]]; then
        echo "Selesai: $LABEL / Repeat $REPEAT_NO"
        return 0
    fi

    echo "PERINGATAN: Pengujian perlu diperiksa: $LABEL / Repeat $REPEAT_NO"
    return 1
}
