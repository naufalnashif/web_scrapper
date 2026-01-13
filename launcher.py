import os
import subprocess
import platform
import sys
import webbrowser
import time

# === KONFIGURASI OTOMATIS ===
# Mengambil lokasi folder tempat script ini berada agar bisa jalan di komputer mana saja
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_PATH = os.path.join(BASE_DIR, "app.py")
IMAGE_NAME = "web-scrapper-gemini"
PORT = "7860"  # Sesuai dengan EXPOSE di Dockerfile Anda 

def find_venv():
    for name in ['venv', '.venv', 'env']:
        path = os.path.join(BASE_DIR, name)
        if os.path.isdir(path): return path
    return None

def get_execs(venv_path):
    is_win = platform.system() == "Windows"
    bin_f = "Scripts" if is_win else "bin"
    ext = ".exe" if is_win else ""
    return os.path.join(venv_path, bin_f, f"python{ext}"), os.path.join(venv_path, bin_f, f"streamlit{ext}")

def run_docker():
    print(f"\n[!] Membangun Docker Image...")
    os.chdir(BASE_DIR)
    try:
        # Build image
        subprocess.run(["docker", "build", "-t", IMAGE_NAME, "."], check=True)
        print(f"[*] Menjalankan Container di port {PORT}...")
        
        # Buka browser otomatis setelah jeda singkat
        time.sleep(2)
        webbrowser.open(f"http://localhost:{PORT}")
        
        # Jalankan container (menggunakan port 7860 sesuai Dockerfile) 
        subprocess.run([
            "docker", "run", "--name", IMAGE_NAME, 
            "-p", f"{PORT}:{PORT}", "--rm", IMAGE_NAME
        ], check=True)
    except Exception as e:
        print(f"\n[ERROR] Pastikan Docker Desktop sudah aktif!\nDetail: {e}")

def run_local(setup=False):
    os.chdir(BASE_DIR)
    venv_path = find_venv() or os.path.join(BASE_DIR, "venv")
    
    if not os.path.exists(venv_path):
        print("[!] Membuat Virtual Environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        venv_path = os.path.join(BASE_DIR, "venv")
        setup = True

    py, st = get_execs(venv_path)

    if setup:
        print("[!] Menginstall/Update Dependencies...")
        subprocess.run([py, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        # Menginstall library dari requirements.txt 
        subprocess.run([py, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

    if os.path.exists(st):
        print(f"[*] Menjalankan Streamlit...")
        subprocess.run([st, "run", "app.py"], check=True)
    else:
        print("[ERROR] Streamlit tidak ditemukan. Gunakan opsi nomor 2.")

def cleanup():
    print("[!] Membersihkan sisa Docker...")
    subprocess.run(["docker", "stop", IMAGE_NAME], stderr=subprocess.DEVNULL)
    subprocess.run(["docker", "rmi", "-f", IMAGE_NAME], stderr=subprocess.DEVNULL)
    print("[*] Selesai.")

if __name__ == "__main__":
    while True:
        print(f"\n{'='*40}\n  STREAMLIT MULTI-OS LAUNCHER\n{'='*40}")
        print("1. Jalankan via Docker (Paling Bersih)")
        print("2. Setup Baru & Jalankan Lokal (Venv)")
        print("3. Langsung Jalankan Lokal (Cepat)")
        print("4. Hapus Docker Image & Stop (Reset)")
        print("5. Keluar")
        
        choice = input("\nPilih menu (1-5): ")
        if choice == "1": run_docker()
        elif choice == "2": run_local(setup=True)
        elif choice == "3": run_local(setup=False)
        elif choice == "4": cleanup()
        elif choice == "5": break
        else: print("Pilihan tidak valid.")