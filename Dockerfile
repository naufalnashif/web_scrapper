# Menggunakan image Python resmi yang ringan
FROM python:3.11-slim

# Mengatur environment variables agar Python tidak membuat file .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Mengatur direktori kerja di dalam container
WORKDIR /app

# Menginstal dependensi sistem yang dibutuhkan (untuk library Excel/Pandas)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Menyalin file requirements terlebih dahulu (optimasi cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin seluruh kode aplikasi ke dalam container
COPY . .

# Mengekspos port 8501 (Port default Streamlit)
EXPOSE 8501

# Perintah untuk menjalankan aplikasi saat container dimulai
# Menggunakan alamat 0.0.0.0 agar bisa diakses dari luar container
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]