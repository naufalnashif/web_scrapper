import httpx
from bs4 import BeautifulSoup
import json

def test_tiktok_profile(username):
    # Menghapus @ jika ada
    clean_username = username.replace('@', '')
    url = f"https://www.tiktok.com/@{clean_username}"
    
    # Header minimal agar tidak dianggap bot standar
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    }

    print(f"🧐 Mencoba mengambil data untuk: {url}...")

    with httpx.Client(headers=headers, follow_redirects=True, timeout=15.0) as client:
        try:
            response = client.get(url)
            
            if response.status_code != 200:
                print(f"❌ Gagal! Status Code: {response.status_code}")
                return

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Mencari script data rehydration
            script_tag = soup.find('script', id='__UNIVERSAL_DATA_FOR_REHYDRATION__')
            
            if script_tag:
                raw_json = json.loads(script_tag.string)
                
                # Path data TikTok (Struktur terbaru 2024/2025)
                # Catatan: Path ini bisa berubah, kita gunakan try-except untuk navigasi
                try:
                    user_info = raw_json['__DEFAULT_SCOPE__']['webapp.user-detail']['userInfo']
                    user = user_info['user']
                    stats = user_info['stats']

                    print("\n✅ DATA BERHASIL DIAMBIL:")
                    print("-" * 30)
                    print(f"Nama Lengkap : {user.get('nickname')}")
                    print(f"Username     : {user.get('uniqueId')}")
                    print(f"Bio          : {user.get('signature')}")
                    print(f"Followers    : {stats.get('followerCount')}")
                    print(f"Following    : {stats.get('followingCount')}")
                    print(f"Total Likes  : {stats.get('heartCount')}")
                    print(f"Verified     : {user.get('verified')}")
                    print("-" * 30)
                    
                except KeyError as e:
                    print(f"⚠️ Struktur JSON berubah atau data tidak lengkap: {e}")
                    # Tampilkan kunci utama untuk debugging
                    print("Available Keys:", raw_json['__DEFAULT_SCOPE__'].keys())
            else:
                print("❌ Gagal: Script tag '__UNIVERSAL_DATA_FOR_REHYDRATION__' tidak ditemukan.")
                print("Tip: TikTok mungkin mendeteksi koneksi Anda sebagai bot atau butuh captcha.")

        except Exception as e:
            print(f"💥 Error: {e}")

# TEST DISINI
test_tiktok_profile("paragon.id")