#!/bin/bash

SCRIPT_DIR="/media/sf_Client/script"

# Muat konfigurasi dan fungsi pengujian
source "$SCRIPT_DIR/config.sh"
source "$SCRIPT_DIR/test_condition.sh"

# Cleanup jika eksperimen dihentikan
handle_interrupt() {
    echo ""
    echo "Eksperimen dihentikan. Membersihkan proses..."

    cleanup_active_processes

    exit 130
}

trap handle_interrupt INT TERM HUP

# Persiapan sebelum eksperimen
source "$SCRIPT_DIR/setup.sh" || exit 1

# Pulihkan WireGuard ketika script selesai
restore_wireguard() {
    if ! ip link show wg0 >/dev/null 2>&1; then
        echo "Memulihkan koneksi WireGuard..."
        sudo wg-quick up wg0 || \
            echo "PERINGATAN: WireGuard gagal dipulihkan."
    fi
}

trap restore_wireguard EXIT

# Jalankan semua skenario pengujian
source "$SCRIPT_DIR/run_scenarios.sh"

# Tampilkan ringkasan hasil
source "$SCRIPT_DIR/finish.sh"
