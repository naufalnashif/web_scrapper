from curl_cffi import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os

def test_tokopedia_scrape(keyword):
    print(f"🚀 Memulai Scrape Tokopedia: {keyword}...")
    scraped_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    url = f"https://www.tokopedia.com/search?st=product&q={keyword.replace(' ', '%20')}"

    headers = {
        "authority": "www.tokopedia.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,chrome/120",
        "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, impersonate="chrome120", timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Gagal. Status Code: {response.status_code}")
            return

        html_content = response.text
        print(f"✅ Berhasil mengambil {len(html_content)} karakter HTML.")

        # --- FASE EKSTRAKSI DATA (PARSING) ---
        soup = BeautifulSoup(html_content, 'html.parser')
        script_tag = soup.find('script', id='__NEXT_DATA__')
        
        extracted_posts = []
        
        if script_tag:
            json_data = json.loads(script_tag.string)
            try:
                # Navigasi ke path produk di dalam JSON Tokopedia
                products = json_data['props']['pageProps']['initialState']['searchProduct']['data']['products']
                
                for p in products:
                    extracted_posts.append({
                        "product_name": p.get('name'),
                        "price": p.get('priceInt'),
                        "merchant_name": p.get('shop', {}).get('name'),
                        "city": p.get('shop', {}).get('city'),
                        "rating": p.get('ratingAverage'),
                        "sold_count": p.get('labelGroups', [{}])[0].get('title', '0'),
                        "url": p.get('url'),
                        "scraped_at": scraped_at
                    })
            except KeyError:
                print("⚠️ Struktur JSON __NEXT_DATA__ berubah atau tidak ditemukan.")

        # --- FASE PENYIMPANAN ---
        folder_name = "scraped_data"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        data = {
            "platform": "Tokopedia",
            "profile_info": {
                "search_keyword": keyword,
                "scraped_at": scraped_at,
                "status": "Success",
                "total_found": len(extracted_posts)
            },
            "posts": extracted_posts 
        }

        # Simpan hasil akhir ke JSON
        json_filename = f"{folder_name}/result_{keyword.replace(' ', '_')}_{timestamp}.json"
        with open(json_filename, "w") as f:
            json.dump(data, f, indent=4)

        print(f"🎯 Berhasil mengekstrak {len(extracted_posts)} produk.")
        print(f"💾 Data disimpan di: {json_filename}")
        
        return data

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    res = test_tokopedia_scrape("Laptop Asus")