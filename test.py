import httpx
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

def get_job_deep_details(client, job_url):
    """
    Mengunjungi halaman detail pekerjaan secara anonim 
    untuk mengambil metadata yang tidak muncul di hasil pencarian.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        # Mengambil halaman publik detail lowongan
        resp = client.get(job_url, headers=headers, timeout=15.0)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 1. Deskripsi Lengkap (Full Text)
            desc_section = soup.find('div', class_='description__text')
            full_description = desc_section.get_text(separator="\n").strip() if desc_section else "N/A"
            
            # 2. Kriteria Pekerjaan (Seniority, Employment Type, Industries)
            # LinkedIn menampilkan ini dalam list kriteria
            criteria_map = {}
            criteria_items = soup.find_all('li', class_='description__job-criteria-item')
            for item in criteria_items:
                header = item.find('h3').text.strip() if item.find('h3') else "Other"
                value = item.find('span').text.strip() if item.find('span') else "N/A"
                criteria_map[header] = value

            # 3. Jumlah Pelamar
            applicant_tag = soup.find('span', class_='num-applicants__caption')
            applicants = applicant_tag.text.strip() if applicant_tag else "N/A"

            # 4. Nama Perusahaan & Link (Verifikasi ulang)
            comp_link_tag = soup.find('a', class_='topcard__org-name-link')
            company_link = comp_link_tag['href'].split('?')[0] if comp_link_tag else "N/A"

            return {
                "description": full_description,
                "seniority_level": criteria_map.get("Seniority level", "N/A"),
                "employment_type": criteria_map.get("Employment type", "N/A"),
                "job_function": criteria_map.get("Job function", "N/A"),
                "industries": criteria_map.get("Industries", "N/A"),
                "applicants_count": applicants,
                "company_link": company_link
            }
    except Exception as e:
        print(f"      [!] Gagal mengambil detail untuk {job_url}: {str(e)}")
    
    return {}

def run_rich_test(keyword="Data Analyst", location="Indonesia", limit=1):
    print(f"[*] Menjalankan LinkedIn Rich Scraper (Anonim)...")
    print(f"[*] Target: {keyword} di {location} (Limit: {limit} data)\n")

    # API Guest LinkedIn untuk list awal
    api_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    params = {
        "keywords": keyword,
        "location": location,
        "start": 0
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.linkedin.com/jobs/search"
    }

    results = []
    
    with httpx.Client(headers=headers, timeout=30.0, follow_redirects=True) as client:
        # Step 1: Ambil list lowongan
        response = client.get(api_url, params=params)
        if response.status_code != 200:
            print(f"[ERROR] Gagal akses list. Status: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        job_cards = soup.find_all('li')
        
        print(f"[+] Menemukan {len(job_cards)} lowongan di halaman pertama.")
        
        # Step 2: Loop dan ambil detail mendalam
        for i, job in enumerate(job_cards[:limit]):
            try:
                title = job.find('h3', class_='base-search-card__title').text.strip()
                company = job.find('h4', class_='base-search-card__subtitle').text.strip()
                loc = job.find('span', class_='job-search-card__location').text.strip()
                job_url = job.find('a', class_='base-card__full-link')['href'].split('?')[0]
                
                print(f"    [{i+1}/{limit}] Mengambil detail: {title} @ {company}...")
                
                # Panggil fungsi detail
                deep_data = get_job_deep_details(client, job_url)
                
                # Gabungkan data awal dan data detail
                full_item = {
                    "name": title,
                    "publisher": company,
                    "location": loc,
                    "url": job_url,
                    "date": job.find('time')['datetime'] if job.find('time') else "N/A",
                    "caption": f"[{company}] {title} in {loc}",
                    "scraped_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "platform": "LinkedIn",
                    # Data Tambahan Hasil Deep Scraping
                    "description": deep_data.get("description", "N/A"),
                    "seniority_level": deep_data.get("seniority_level", "N/A"),
                    "employment_type": deep_data.get("employment_type", "N/A"),
                    "job_function": deep_data.get("job_function", "N/A"),
                    "industries": deep_data.get("industries", "N/A"),
                    "applicants_count": deep_data.get("applicants_count", "N/A"),
                    "company_link": deep_data.get("company_link", "N/A")
                }
                results.append(full_item)
                
                # JEDA PENTING: Jangan hapus agar tidak diblokir LinkedIn
                time.sleep(2) 
                
            except Exception as e:
                print(f"    [!] Error pada item ke-{i+1}: {str(e)}")
                continue

    # Tampilkan Hasil
    if results:
        df = pd.DataFrame(results)
        print("\n" + "="*50)
        print("[SUCCESS] Data yang berhasil ditarik:")
        print(df[['name', 'publisher', 'seniority_level', 'applicants_count']].to_string(index=False))
        print("="*50)
        
        # Simpan ke CSV untuk pengecekan detail
        df.to_csv("test_linkedin_rich_results.csv", index=False)
        print(f"[*] Hasil lengkap (termasuk deskripsi) disimpan ke: test_linkedin_rich_results.csv")
    else:
        print("[!] Tidak ada data yang berhasil ditarik.")

if __name__ == "__main__":
    # Jalankan test
    run_rich_test(keyword="Digital Marketing", location="Jakarta", limit=5)