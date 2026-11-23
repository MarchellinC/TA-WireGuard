#!/bin/bash

SERVER_USER="marchellinc"
PHYSICAL_IP="192.168.56.101"
WG_IP="10.10.0.1"

BASE_DIR="/media/sf_Client/raw_data/ta"

# ID eksperimen otomatis berdasarkan folder yang sudah ada
LAST_ID=0

for DIR in "$BASE_DIR"/all_skenario*; do
    [[ -d "$DIR" ]] || continue

    NAME="${DIR##*/}"

    if [[ "$NAME" =~ ^all_skenario([0-9]+)$ ]]; then
        NUM="${BASH_REMATCH[1]}"
        if (( NUM > LAST_ID )); then
            LAST_ID=$NUM
        fi
    fi
done

EXPERIMENT_ID=$((LAST_ID + 1))
RUN_DIR="$BASE_DIR/all_skenario$EXPERIMENT_ID"

REPEATS=5
COOLDOWN=20
WG_START_DELAY=10

DURATION=30
MONITOR_DURATION=35

PACKET_SIZES=(128 512 1024)
TRAFFIC_RATES=("10M" "50M" "100M")

SERVER_MONITOR="/media/sf_Server/script/monitor_cpu_test.sh"
SERVER_LOG_ROOT="/media/sf_Server/raw_data/ta"

TOTAL=0
FAILED=0
