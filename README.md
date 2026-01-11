# ParagonCorp Scraper Specialist Hub

## 🚀 Overview
Platform ini adalah solusi ekstraksi data modular untuk Instagram, Shopee, dan TikTok yang dikembangkan sesuai spesifikasi tes ParagonCorp.

## 🛠️ Tech Stack
- **Engine:** Python 3.9+
- **Frontend:** Streamlit (Professional UI)
- **Backend:** Flask API (Scalable)
- **Deployment:** Docker & Hugging Face Spaces

## 📦 Installation
1. Clone repository
2. Jalankan `pip install -r requirements.txt`
3. Jalankan aplikasi: `streamlit run app.py`

## [cite_start]🛡️ Anti-Bot Strategy [cite: 18-24]
- **Session Simulation:** Menggunakan user-agent mobile untuk meniru perangkat asli.
- **Rate Limiting:** Jeda acak antar request untuk menghindari blokir IP.
- **Fingerprinting:** Rotasi header HTTP pada setiap sesi baru.