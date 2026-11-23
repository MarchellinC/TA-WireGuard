#!/bin/bash

if [[ $EUID -eq 0 ]]; then
    echo "Jalankan script sebagai user biasa, bukan root."
    return 1
fi

for cmd in iperf3 ping ssh scp top; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "ERROR: Perintah $cmd belum tersedia."
        return 1
    fi
done

if [[ -e "$RUN_DIR" ]]; then
    echo "ERROR: Folder hasil sudah ada: $RUN_DIR"
    echo "Ganti RUN_DIR di config.sh agar hasil lama tidak tertimpa."
    return 1
fi

sudo -v || return 1

ssh -o BatchMode=yes -o ConnectTimeout=5 \
    "$SERVER_USER@$PHYSICAL_IP" "hostname" || return 1

ssh "$SERVER_USER@$PHYSICAL_IP" \
    "ss -ltn | grep -q ':5201'" || {
        echo "ERROR: iperf3 server belum aktif."
        return 1
    }

ssh "$SERVER_USER@$PHYSICAL_IP" \
    "test -f '$SERVER_MONITOR'" || {
        echo "ERROR: Script monitor CPU server tidak ditemukan."
        return 1
    }

ssh "$SERVER_USER@$PHYSICAL_IP" \
    "test -d '/media/sf_Server/raw_data/ta' && test -w '/media/sf_Server/raw_data/ta'" || {
        echo "ERROR: Direktori ta di Server belum tersedia atau tidak bisa ditulis."
        return 1
    }

mkdir -p "$RUN_DIR"

echo "Persiapan selesai."
