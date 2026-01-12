import pandas as pd
import json
from google_play_scraper import app, reviews_all, Sort
from datetime import datetime

class PlayStoreScraper:
    def get_detailed_data(self, app_id: str, lang='id', country='id'):
        try:
            # 1. Ambil Metadata Aplikasi
            info = app(app_id, lang=lang, country=country)
            
            # 2. Ambil Ulasan
            result_reviews = reviews_all(
                app_id,
                sleep_milliseconds=0,
                lang=lang,
                country=country,
                sort=Sort.NEWEST,
                count=100 
            )

            scraped_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            data = {
                "platform": "PlayStore",
                "profile_info": {
                    "app_id": app_id,
                    "title": info['title'],
                    "developer": info['developer'],
                    "category": info['genre'],
                    "rating": round(info['score'], 2),
                    "reviews_count": info['reviews'],
                    "installs": info['installs'],
                    "price": info['price'],
                    "icon": info['icon'],
                    "url": info['url']
                },
                "posts": [] 
            }

            for r in result_reviews:
                data["posts"].append({
                    "user": r['userName'],
                    "rating": r['score'],
                    "content": r['content'],
                    "date": r['at'].strftime('%Y-%m-%d %H:%M:%S'),
                    "reply": r['replyContent'],
                    "thumbs_up": r['thumbsUpCount']
                })

            return data
        except Exception as e:
            # Menggunakan raise agar traceback terlihat saat development
            raise e

# --- SCRIPT PENGUJIAN (TESTING) ---
if __name__ == "__main__":
    scraper = PlayStoreScraper()
    
    # Ganti dengan app_id yang ingin dites
    target_app = "com.shopee.id" 
    
    print(f"--- Memulai Scraping Play Store: {target_app} ---")
    
    try:
        results = scraper.get_detailed_data(target_app)
        
        # 1. Tampilkan Info Profil
        print("\n✅ METADATA APLIKASI:")
        print(json.dumps(results['profile_info'], indent=4))
        
        # 2. Tampilkan Statistik Ulasan
        posts = results['posts']
        print(f"\n✅ BERHASIL MENGAMBIL {len(posts)} ULASAN.")
        
        # 3. Konversi ke DataFrame untuk melihat tabel (5 teratas)
        if posts:
            df = pd.DataFrame(posts)
            print("\n✅ PREVIEW DATA ULASAN (5 TERATAS):")
            print(df.head())
            
            # Simpan hasil ke CSV untuk dicek manual
            filename = f"test_result_{target_app}.csv"
            df.to_csv(filename, index=False)
            print(f"\n💾 Data disimpan ke: {filename}")

    except Exception as error:
        print("\n❌ TERJADI ERROR LENGKAP (DEV MODE):")
        import traceback
        traceback.print_exc()