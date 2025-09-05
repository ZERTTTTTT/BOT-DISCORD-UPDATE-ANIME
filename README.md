# AnimeUpdate by ZertScript (Versi Sederhana)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Discord.py](https://img.shields.io/badge/Discord.py-5865F2?style=for-the-badge&logo=discord&logoColor=white)

Bot Discord sederhana yang fokus pada satu tujuan: mengirimkan jadwal rilis anime harian secara otomatis ke server Anda. Versi ini dirancang agar ringan, stabil, dan sangat mudah untuk diatur tanpa memerlukan database.

**Sumber Data API**: [AniList.co](https://anilist.co)

---
### ❤️ Dukung Saya
Jika Anda menyukai bot ini dan ingin memberikan apresiasi, Anda bisa mendukung saya melalui link di bawah ini. Terima kasih banyak!

* **[Support Saya di Sociabuzz](https://sociabuzz.com/zerty_/support)**

---
## ✨ Fitur Utama

Bot ini memiliki set perintah yang fokus untuk kemudahan penggunaan:

* `/update`: Meminta update jadwal anime untuk hari ini atau tanggal tertentu secara manual (Admin Only).
* `/updateautoset`: Pusat kendali untuk jadwal otomatis (Admin Only).
    * `set`: Mengatur jam update harian (WIB).
    * `on`: Mengaktifkan update harian.
    * `off`: Menonaktifkan update harian.
* `/info`: Menampilkan informasi dasar tentang bot.
* `/info-panel`: Menampilkan status teknis bot seperti penggunaan CPU, RAM, dan waktu berjalan (uptime).

---
## 🚀 Instalasi & Pengaturan

#### 1. Siapkan File
Pastikan Anda memiliki 4 file berikut di direktori Anda: `app.py`, `.env`, `requirements.txt`, dan `schedule_settings.json`.

#### 2. Isi File `.env`
Buat file bernama `.env` dan isi dengan informasi berikut:
```env
# Ganti dengan informasi bot Anda
DISCORD_TOKEN=TOKEN_BOT_ANDA
CLIENT_ID=CLIENT_ID_BOT_ANDA
TARGET_CHANNEL_ID=ID_CHANNEL_UNTUK_UPDATE_ANIME
