from sys import platform
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from scrapers.instagram import InstagramScraper
from scrapers.tiktok import TikTokScraper
from scrapers.shopee import ShopeeScraper
from utils.logger import log_activity
import time

def render_sidebar():
    # st.sidebar.title("⚙️ Scraper Configuration")
    with st.sidebar.expander("⚙️ Scraper Configuration", expanded=False):
    
        # 1. Platform Selection
        platform_choice = st.selectbox("Platform", ["Instagram", "Shopee", "TikTok"])

        # 2. Input Section
        with st.expander("📥 Input Configuration", expanded=True):
        # st.subheader("📥 Input Configuration")
            input_method = st.radio("Metode Input", ["Manual Text", "Upload File (TXT/CSV/XLSX)"], horizontal=True)
            
            targets = []

            # Dinamis berdasarkan platform (menggunakan kode asli Anda)
            if platform_choice == "Shopee":
                instruction, placeholder, default_val = "Masukkan SKU (shopid:itemid)", "Contoh: 110546114:21843232230", "110546114:21843232230"
            elif platform_choice == "TikTok":
                instruction, placeholder, default_val = "Masukkan username", "Contoh: novanov1_", "novanov1_, fanes.aaaa"
            else:
                instruction, placeholder, default_val = "Masukkan Username Instagram", "user1, user2", "naufal.nashif, _self.daily"

            if input_method == "Manual Text":
                raw_input = st.text_area(instruction, value=default_val, placeholder=placeholder, help="Gunakan koma atau baris baru untuk memisahkan antar target.")
                targets = [t.strip() for t in raw_input.replace("\n", ",").split(",") if t.strip()]
            else:
                uploaded_file = st.file_uploader("Pilih file", type=['csv', 'xlsx', 'txt'])
                if uploaded_file:
                    try:
                        if uploaded_file.name.endswith('.csv'):
                            df = pd.read_csv(uploaded_file)
                            targets = df.iloc[:, 0].dropna().tolist()
                        elif uploaded_file.name.endswith('.xlsx'):
                            df = pd.read_excel(uploaded_file)
                            targets = df.iloc[:, 0].dropna().tolist()
                        elif uploaded_file.name.endswith('.txt'):
                            stringio = uploaded_file.read().decode("utf-8")
                            targets = [t.strip() for t in stringio.replace("\n", ",").split(",") if t.strip()]
                    except Exception as e:
                        st.error(f"Error baca file: {e}")

        # --- EXTRACTION FILTERS (ATAS BAWAH) ---
        with st.expander("⏲️ Extraction Filters", expanded=True):
        # st.subheader("⏲️ Extraction Limits")
        
            # max_posts = st.sidebar.number_input(
            #     "Max Posts per Account", 
            #     min_value=1, 
            #     max_value=200, 
            #     value=10, 
            #     help="Batasi jumlah postingan yang diambil untuk setiap target."
            # )
            # Filter Jumlah Postingan
            use_count_limit = st.checkbox("Limit Post Count", value=True, help="Centang untuk membatasi jumlah postingan yang diambil.")
            max_posts = 9999 # Default jika tidak dilimit
            if use_count_limit:
                max_posts = st.number_input("Max Posts per Account", min_value=1, max_value=500, value=10)
            
            use_date_filter = st.checkbox("Filter by Date", help="Hanya ambil postingan sejak tanggal tertentu.")
            since_date = None
            if use_date_filter:
                since_date = st.date_input("Get posts since:", datetime.now() - timedelta(days=30))

            # 3. Mode Toggle
        mode = st.toggle("Gunakan Flask API", value=False)

        # 4. Action Button & Logic
        if st.button("🚀 Start Scraping", use_container_width=True):
            if not targets:
                st.error("Masukkan target terlebih dahulu!")
            else:
                st.session_state.all_results = [] 
                
                if platform_choice == "Instagram":
                    scraper = InstagramScraper()
                elif platform_choice == "TikTok":
                    scraper = TikTokScraper()
                else:
                    scraper = ShopeeScraper()
                
                progress_text = st.empty()
                progress_bar = st.progress(0)
                
                for idx, t in enumerate(targets):
                    progress_text.text(f"Processing: {t}")
                    log_activity(f"Scraping {t} via {platform_choice}...")
                    
                    # Eksekusi scraping dengan filter baru
                    if platform_choice == "TikTok":
                        res = scraper.get_data(t, max_posts=max_posts, since_date=since_date)
                    elif platform_choice == "Instagram":
                        res = scraper.get_detailed_data(t, max_posts=max_posts, since_date=since_date)
                    else:
                        res = scraper.get_data(t)
                    
                    st.session_state.all_results.append(res)
                    
                    progress_bar.progress((idx + 1) / len(targets))
                    time.sleep(1)
                
                progress_text.text("✅ Scraping Selesai!")
                st.success(f"Berhasil mengambil {len(st.session_state.all_results)} data.")
                st.rerun()