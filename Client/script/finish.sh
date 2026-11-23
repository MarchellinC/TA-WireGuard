#!/bin/bash

echo ""
echo "===================================="
echo "PENGAMBILAN DATA SELESAI"
echo "ID Eksperimen : $EXPERIMENT_ID"
echo "Total kondisi : $TOTAL"
echo "Kondisi gagal : $FAILED"
echo "Kondisi sukses: $((TOTAL - FAILED))"
echo "Lokasi hasil  : $RUN_DIR"
echo "===================================="

if [[ "$FAILED" -gt 0 ]]; then
    echo "PERINGATAN: Ada kondisi yang perlu diperiksa."
else
    echo "Semua kondisi dilaporkan berhasil."
fi
