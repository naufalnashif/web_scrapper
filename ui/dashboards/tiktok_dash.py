import streamlit as st
import pandas as pd
import plotly.express as px

def render_tiktok_dashboard(df_profiles, df_posts):
    st.subheader("🎵 TikTok Creator Performance")

    # --- KPI METRICS ---
    if not df_profiles.empty:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Avg. ER", f"{df_profiles['engagement_rate'].mean():.2f}%")
        m2.metric("Total Views", f"{df_posts['views'].sum():,}" if 'views' in df_posts.columns else "0")
        m3.metric("Total Followers", f"{df_profiles['followers'].sum():,}")
        m4.metric("Avg. Likes/Post", f"{df_posts['likes'].mean():.0f}" if not df_posts.empty else "0")
        st.divider()

    res_tab_ov, res_tab_det = st.tabs(["🏠 Analysis Overview", "📋 Detailed Data"])

    with res_tab_ov:
        c1, col_pie = st.columns(2)
        
        with c1:
            st.markdown("#### 🚀 Video Engagement (Views vs Likes)")
            if not df_posts.empty and 'views' in df_posts.columns:
                fig_scatter = px.scatter(
                    df_posts, x='views', y='likes', 
                    size='comments_count', color='username',
                    template="plotly_dark", hover_name='caption'
                )
                st.plotly_chart(fig_scatter, use_container_width=True)

        with col_pie:
            st.markdown("#### 📊 Followers Share")
            fig_pie = px.pie(df_profiles, values='followers', names='username', template="plotly_dark", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

    with res_tab_det:
        with st.expander("👤 Profile Insights", expanded=True):
            st.dataframe(df_profiles, use_container_width=True)
        with st.expander("🎬 Post Metadata", expanded=True):
            st.dataframe(df_posts, use_container_width=True)