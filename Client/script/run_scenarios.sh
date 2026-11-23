#!/bin/bash

# Semua kombinasi ukuran paket dan bitrate
for SIZE in "${PACKET_SIZES[@]}"; do
    for RATE in "${TRAFFIC_RATES[@]}"; do

        echo ""
        echo "===================================="
        echo "SKENARIO: ${SIZE} bytes / ${RATE}"
        echo "===================================="

        # Sesi 1: Baseline 5 kali
        echo "--- BASELINE: ${SIZE} bytes / ${RATE} ---"

        if ip link show wg0 >/dev/null 2>&1; then
            sudo wg-quick down wg0 || return 1
        fi

        for ((REPEAT_NO=1; REPEAT_NO<=REPEATS; REPEAT_NO++)); do
            echo ""
            echo "=== BASELINE: ${SIZE} bytes / ${RATE} / Repeat ${REPEAT_NO}/${REPEATS} ==="

            if run_condition "$SIZE" "$RATE" \
                "BASELINE" "$PHYSICAL_IP" "$REPEAT_NO"; then
                :
            else
                FAILED=$((FAILED + 1))
            fi

            TOTAL=$((TOTAL + 1))
            sleep "$COOLDOWN"
        done

        # Sesi 2: WireGuard 5 kali untuk skenario yang sama
        echo ""
        echo "--- WIREGUARD: ${SIZE} bytes / ${RATE} ---"

        if ! ip link show wg0 >/dev/null 2>&1; then
            sudo wg-quick up wg0 || return 1
        fi

        sleep "$WG_START_DELAY"

        for ((REPEAT_NO=1; REPEAT_NO<=REPEATS; REPEAT_NO++)); do
            echo ""
            echo "=== WIREGUARD: ${SIZE} bytes / ${RATE} / Repeat ${REPEAT_NO}/${REPEATS} ==="

            if run_condition "$SIZE" "$RATE" \
                "WIREGUARD" "$WG_IP" "$REPEAT_NO"; then
                :
            else
                FAILED=$((FAILED + 1))
            fi

            TOTAL=$((TOTAL + 1))
            sleep "$COOLDOWN"
        done

        # Matikan WireGuard sebelum berpindah skenario
        if ip link show wg0 >/dev/null 2>&1; then
            sudo wg-quick down wg0 || return 1
        fi

    done
done
