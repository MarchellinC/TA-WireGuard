#!/bin/bash

SCRIPT_DIR="/media/sf_Client/script"

source "$SCRIPT_DIR/config.sh"
source "$SCRIPT_DIR/test_condition.sh"

# Persiapan
source "$SCRIPT_DIR/setup.sh" || exit 1

# Pastikan WireGuard dipulihkan ketika script selesai
restore_wireguard() {
    if ! ip link show wg0 >/dev/null 2>&1; then
        sudo wg-quick up wg0
    fi
}

trap restore_wireguard EXIT

# Jalankan semua skenario
source "$SCRIPT_DIR/run_scenarios.sh"

# Ringkasan
source "$SCRIPT_DIR/finish.sh"
