import streamlit as st
import pandas as pd
from ui.components import render_header, render_terminal_logs, render_documentation
from ui.sidebar import render_sidebar
# IMPORT DASHBOARD BARU
from ui.dashboards.instagram_dash import render_instagram_dashboard
from ui.dashboards.tiktok_dash import render_tiktok_dashboard
from ui.dashboards.shopee_dash import render_shopee_dashboard


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
        # 1. Identifikasi Platform
        current_platform = st.session_state.all_results[0].get('platform', 'Instagram')
        
        # 2. Siapkan Dataframe Universal
        df_profiles = pd.DataFrame([r['profile_info'] for r in st.session_state.all_results if 'error' not in r])
        all_posts = []
        for r in st.session_state.all_results:
            if 'posts' in r:
                for p in r['posts']:
                    p_copy = p.copy()
                    p_copy['username'] = r['profile_info']['username']
                    all_posts.append(p_copy)
        df_posts = pd.DataFrame(all_posts)
        # Di app.py Anda, sebelum pd.to_datetime
        if not df_posts.empty and 'date' in df_posts.columns:
            df_posts['date'] = pd.to_datetime(df_posts['date'], errors='coerce')
        else:
            # Buat kolom date kosong agar baris kode selanjutnya tidak error
            df_posts['date'] = pd.Series(dtype='datetime64[ns]')

        # 3. Routing Dashboard Berdasarkan Platform
        if current_platform == "Instagram":
            render_instagram_dashboard(df_profiles, df_posts)
        elif current_platform == "TikTok":
            render_tiktok_dashboard(df_profiles, df_posts)
        elif current_platform == "Shopee":
            render_shopee_dashboard(df_profiles, df_posts)
        
        # 4. Bagian Result Details (Tetap di app.py karena format tabelnya universal)
        # with st.expander("📋 View Raw Data & Tables"):
        #     st.dataframe(df_profiles, use_container_width=True)

with tab_logs:
    render_terminal_logs(st.session_state.logs)