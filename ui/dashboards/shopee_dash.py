import streamlit as st
import pandas as pd
import plotly.express as px

def render_shopee_dashboard(df_profiles, df_posts):
    st.subheader("🛍️ Shopee Product Monitoring")
    
    # Metrik Khusus Shopee
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 📦 Stock Availability")
        fig_stock = px.bar(df_profiles, x='username', y='following', 
                           title="Product Stock Level",
                           labels={'following': 'Stock Quantity', 'username': 'Product Name'},
                           color='following', color_continuous_scale='Viridis',
                           template="plotly_dark")
        st.plotly_chart(fig_stock, use_container_width=True)
        
    with col2:
        st.markdown("#### ❤️ Wishlist/Likes")
        fig_likes = px.funnel(df_profiles.sort_values('followers'), 
                              y='username', x='followers',
                              title="Customer Interest (Likes)")
        st.plotly_chart(fig_likes, use_container_width=True)