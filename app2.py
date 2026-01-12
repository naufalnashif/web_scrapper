import streamlit as st
import pandas as pd
from ui.components import render_header, render_terminal_logs, render_documentation
from ui.sidebar import render_sidebar
# IMPORT DASHBOARD BARU
from ui.dashboards.instagram_dash import render_instagram_dashboard
from ui.dashboards.tiktok_dash import render_tiktok_dashboard
from ui.dashboards.shopee_dash import render_shopee_dashboard
from ui.dashboards.playstore_dash import render_playstore_dashboard


st.set_page_config(page_title="Paragon Scraper Specialist", layout="wide")

render_header()
render_sidebar() # Memanggil sidebar yang sudah diperbaiki

if 'all_results' not in st.session_state: st.session_state.all_results = []
if 'logs' not in st.session_state: st.session_state.logs = []

# --- NAVIGATION TABS ---
tab_doc, tab_dash, tab_logs = st.tabs(["📖 Documentation", "📊 Dashboard", "⚙️ Logs"])

with tab_doc:
    render_documentation()

with tab_dash:
    if not st.session_state.all_results:
        st.info("Silahkan konfigurasi target...")
    else:
        # 1. Filter hasil yang benar-benar berhasil (punya profile_info)
        valid_results = [r for r in st.session_state.all_results if 'error' not in r and 'profile_info' in r]
        
        # 2. Penanganan jika GAGAL (valid_results kosong)
        if not valid_results:
            # Ambil info platform dan error dari hasil pertama agar tidak NameError
            first_res = st.session_state.all_results[0]
            # Gunakan .get() untuk menghindari KeyError
            error_platform = first_res.get('platform', 'Platform')
            raw_error_msg = first_res.get('error', 'Tidak ada detail error teknis.')

            st.error(f"### ⚠️ Ups, Data {error_platform} Tidak Dapat Ditampilkan")
            
            st.markdown(f"""
            Kami mencoba menghubungkan ke platform, namun tidak ada data yang bisa diproses.
            
            **Saran Langkah Selanjutnya:**
            * Cek kembali apakah **ID/Username** yang dimasukkan sudah benar.
            * Periksa koneksi internet atau tab **⚙️ Logs** untuk status Rate Limit.
            * Tunggu 1-2 menit jika terkena pembatasan frekuensi (Rate Limit).
            """)

            # Menampilkan Error Asli (Technical Traceback) secara rapi
            with st.expander("🔍 Lihat Detail Error Teknis (Original Error)"):
                st.code(raw_error_msg, language="python")
            
            if st.button("🔄 Reset & Coba Lagi", use_container_width=True):
                st.session_state.all_results = []
                st.rerun()
        
        # 3. Penanganan jika BERHASIL
        else:
            # Ambil platform dari data yang valid
            current_platform = valid_results[0].get('platform')
            
            # Buat df_profiles secara aman
            df_profiles = pd.DataFrame([r['profile_info'] for r in valid_results])
            
            # Buat df_posts secara aman
            all_posts = []
            for r in valid_results:
                if 'posts' in r and isinstance(r['posts'], list):
                    for p in r['posts']:
                        p_copy = p.copy()
                        # Playstore menggunakan 'app_id', yang lain menggunakan 'username'
                        u_name = r.get('profile_info', {}).get('username') or r.get('profile_info', {}).get('app_id', 'Unknown')
                        p_copy['username'] = u_name
                        all_posts.append(p_copy)
            
            df_posts = pd.DataFrame(all_posts)

            # Proteksi kolom date untuk visualisasi timeline
            if 'date' in df_posts.columns and not df_posts.empty:
                df_posts['date'] = pd.to_datetime(df_posts['date'], errors='coerce')

            # 4. Routing Dashboard Berdasarkan Platform
            if current_platform == "Instagram":
                render_instagram_dashboard(df_profiles, df_posts)
            elif current_platform == "TikTok":
                if 'views' not in df_posts.columns: df_posts['views'] = 0
                render_tiktok_dashboard(df_profiles, df_posts)
            elif current_platform == "Shopee":
                render_shopee_dashboard(df_profiles, df_posts)
            elif current_platform == "PlayStore":
                render_playstore_dashboard(df_profiles, df_posts)

with tab_logs:
    render_terminal_logs(st.session_state.logs)