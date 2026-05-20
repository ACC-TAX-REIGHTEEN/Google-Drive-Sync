# Google-Drive-Sync
Google Drive Auto Sync with local folders, can config with windows  or cronjob

Skrip Python ini berfungsi untuk melakukan sinkronisasi satu arah secara otomatis dari folder lokal di komputer Anda ke Google Drive. Skrip ini dilengkapi dengan pengecekan berbasis **MD5 Checksum** untuk memastikan file hanya akan diunggah atau diperbarui jika terjadi perubahan konten, sehingga menghemat kuota internet dan waktu proses.

Dapat dikombinasikan dengan **Windows Task Scheduler** atau **Cronjob** di Linux/macOS untuk penjadwalan otomatis.

---

## Fitur Utama

* **Sinkronisasi Multi-Folder**: Mendukung pencadangan beberapa folder lokal sekaligus ke satu folder induk di Google Drive.
* **Smart Sync (MD5 Verification)**: Membandingkan *hash* MD5 file lokal dengan file di Google Drive. Jika sama, file akan dilewati (*skip*). Jika berbeda, file di Google Drive akan diperbarui (*update*).
* **Struktur Folder Terjaga**: Mendukung pencadangan folder bersarang (*nested folders* / rekursif) dengan otomatis membuat sub-folder yang sama di Drive.
* **Resumable Uploads**: Menggunakan metode unggah *resumable* yang lebih stabil untuk menangani file berukuran besar.
* **Otentikasi Aman**: Menggunakan OAuth 2.0 resmi dari Google API.

---

## Prasyarat & Persiapan Google Cloud

Sebelum menjalankan skrip, Anda perlu membuat proyek di Google Cloud Console untuk mendapatkan kredensial API.

### 1. Mengaktifkan Google Drive API
1. Buka [Google Cloud Console](https://console.cloud.google.com/).
2. Buat proyek baru atau pilih proyek yang sudah ada.
3. Buka menu **API & Services** > **Library**.
4. Cari **Google Drive API**, lalu klik **Enable**.

### 2. Mengonfigurasi OAuth Consent Screen
1. Buka **API & Services** > **OAuth consent screen**.
2. Pilih User Type **External** (jika menggunakan akun Gmail pribadi) dan klik **Create**.
3. Isi data wajib seperti *App name* dan *User support email*.
4. Pada bagian **Test users**, tambahkan alamat email Google Anda yang akan digunakan sebagai tempat penyimpanan Drive target.

### 3. Mengunduh Kredensial (`credentials.json`)
1. Buka **API & Services** > **Credentials**.
2. Klik **+ Create Credentials** dan pilih **OAuth client ID**.
3. Pilih Application type: **Desktop App**.
4. Beri nama bebas, lalu klik **Create**.
5. Unduh file JSON yang dihasilkan, ubah namanya menjadi `credentials.json`, lalu letakkan di folder yang sama dengan skrip Python ini.

---

## Instalasi Dependensi Lokal

Pastikan Anda sudah menginstal Python 3 di komputer Anda. Kemudian, instal pustaka (*library*) yang dibutuhkan melalui terminal atau Command Prompt (cmd):

```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
