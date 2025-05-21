# ETS Project: Server Stress Testing with Multithreading and Multiprocessing Pools

## 📋 Deskripsi
Proyek ini merupakan implementasi **Stress Test** berbasis TCP socket yang berjalan pada port `6667`. Program ini dirancang untuk menguji ketahanan dan performa server file protocol dalam menangani banyak koneksi secara bersamaan (**concurrent**) menggunakan konsep **multithreading** dan/atau **multiprocessing**. Dalam pengujian ini, setiap client secara paralel dapat melakukan download file dan upload file untuk mensimulasikan beban tinggi pada server.

## 🧩 Fitur
- Server membuka port `6667` menggunakan protokol **TCP**.
- Setiap client yang terhubung akan dilayani dalam thread tersendiri.
- Perintah yang dikenali oleh server:
  - `GET`: Melakukan aksi download file pada server.
  - `ADD`: Melakukan aksi uploads file ke server.

## 🚀 Cara Menjalankan Program

### 1. Generate File Dummy

Buka terminal dan jalankan file `gen_dummy_file.py` untuk mengenerate file dummy untuk stress test:
```bash
python3 gen_dummy_file.py
```

### 2. Jalankan Server

Buka terminal dan jalankan file `file_server_pp.py` untuk multiprocessing pools dan `file_server_tp.py` untuk multithread pools:

```bash
python3 file_server_pp.py -m <jumlah-worker>
```
```bash
python3 file_server_tp.py -m <jumlah-worker>
```

Output akan menampilkan log setiap kali ada client yang terhubung dan permintaan yang diterima.

### 3. Jalankan Client

Buka terminal baru dan jalankan `auto_stress_test.py`:

```bash
python3 auto_stress_test.py
```
Program akan menampilkan detail hasil stress test setiap kombinasi stress test telah dilakukan.
