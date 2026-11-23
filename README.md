# TA-WireGuard

Dashboard Streamlit untuk menganalisis hasil eksperimen kinerja transfer data pada kondisi Baseline dan WireGuard.

## Identitas Peneliti

- **Nama:** Marchellin Chenika
- **NPM:** 140810230002

## Menjalankan dashboard

Gunakan Python 3.10 atau yang lebih baru. Dari folder `TA-WireGuard`, jalankan:

```bash
python -m pip install -r requirements.txt
streamlit run dashboard/app.py
```

Dashboard membaca dataset dari `Client/processed_data/all_skenario3/raw_dataset.csv`. Path ini ditentukan relatif terhadap lokasi kode sehingga aplikasi dapat dijalankan dari folder kerja lain.

## Aturan data

Aturan validasi dan agregasi mengikuti notebook `Client/processed_data/all_skenario3/analisis_wireguard_bersih.ipynb`:

- `iperf_status` dan `receiver_status` harus bernilai `0`.
- Keenam metrik utama harus terisi.
- Nilai grafik merupakan rata-rata yang dikelompokkan menurut `packet_size_bytes`, `target_rate`, dan `condition`.

Target bitrate menunjukkan intensitas trafik yang diminta pada skenario, bukan throughput aktual.

## Isi dashboard

- **Dashboard:** ringkasan pengujian dan definisi parameter.
- **Analisis Grafik:** perbandingan Baseline/WireGuard, tren berdasarkan target bitrate, dan tren berdasarkan ukuran paket untuk seluruh parameter.
- **Tentang Proyek:** latar belakang, tujuan, lingkungan, dan alur penelitian.

Grafik menggunakan Plotly jika terpasang. Jika Plotly belum tersedia, aplikasi menggunakan fallback Altair yang tersedia bersama Streamlit.
