import streamlit as st
import pandas as pd
import glob
import os
import numpy as np
import altair as alt

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Food Delivery Analytics", layout="wide")

# --- KUSTOM CSS (GLASSMORPHISM & VUESAX ICONS) ---
st.markdown("""
    <link rel="stylesheet" href="https://iconsax.gitlab.io/i/icons.css">
    
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
    
    /* Global Font & Layout */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .main { padding: 1rem 2rem; }
    
    /* Header Styling */
    .dashboard-title {
        font-size: 38px;
        font-weight: 700;
        margin-bottom: 5px;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .dashboard-subtitle {
        font-size: 16px;
        color: #94A3B8;
        margin-bottom: 40px;
    }

    /* Glassmorphism Metric Cards */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.05);
    }
    [data-testid="stMetricLabel"] {
        font-size: 14px;
        color: #94A3B8;
        font-weight: 600;
    }
    [data-testid="stMetricValue"] { 
        font-size: 32px; 
        color: #38BDF8; 
        font-weight: 700;
    }
    
    /* Divider Custom */
    hr { border-color: rgba(255,255,255,0.05); margin: 3rem 0; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER CUSTOM DENGAN ICON ---
st.markdown("""
    <div class="dashboard-title">
        <i class="isax isax-box-1"></i> Food Delivery Big Data
    </div>
    <div class="dashboard-subtitle">Visualisasi deskriptif dan prediktif dari end-to-end data pipeline.</div>
""", unsafe_allow_html=True)

# --- FUNGSI LOAD DATA ---
@st.cache_data
def load_spark_data(folder_path):
    try:
        file_list = glob.glob(os.path.join(folder_path, "part-*"))
        if not file_list:
            return pd.DataFrame()
        df = pd.read_csv(file_list[0]) 
        return df
    except Exception as e:
        return pd.DataFrame()

# --- PROSES LOAD DATA ---
df_city = load_spark_data('output/orders_by_city')
df_cuisine = load_spark_data('output/orders_by_cuisine')
df_top_resto = load_spark_data('output/top_restaurants')
df_hour = load_spark_data('output/orders_by_hour') 

# --- 1. KEY METRICS (SCORECARD) ---
st.markdown('### <i class="isax isax-data"></i> Ringkasan Bisnis', unsafe_allow_html=True)
col_m1, col_m2, col_m3 = st.columns(3)

if not df_city.empty:
    total_orders = df_city.iloc[:, 1].sum()
    col_m1.metric("Total Keseluruhan Pesanan", f"{total_orders:,.0f}")
if not df_top_resto.empty:
    avg_rating = df_top_resto['rating'].mean()
    col_m2.metric("Rata-rata Rating Restoran", f"{avg_rating:.2f}")
if not df_cuisine.empty:
    total_cuisines = len(df_cuisine)
    col_m3.metric("Varian Jenis Masakan", f"{total_cuisines}")

st.divider()

# --- Konfigurasi Sumbu (Axis) Umum untuk Grid ---
grid_axis = alt.Axis(grid=True, gridColor='rgba(255, 255, 255, 0.08)', gridDash=[4, 4])

# --- 2. ANALISIS DESKRIPTIF (GRAFIK ALTAIR) ---
col1, col2 = st.columns(2)

with col1:
    st.markdown('#### <i class="isax isax-map-1"></i> Top 15 Kota Teratas', unsafe_allow_html=True)
    if not df_city.empty:
        df_city_sorted = df_city.sort_values(by=df_city.columns[1], ascending=False).head(15)
        
        df_city_sorted = df_city_sorted.reset_index(drop=True)
        df_city_sorted.index = df_city_sorted.index + 1
        df_city_sorted.index.name = 'Rank' 
        
        chart_city = alt.Chart(df_city_sorted).mark_bar(color='#38BDF8', cornerRadiusEnd=6).encode(
            x=alt.X(f"{df_city.columns[0]}:N", sort='-y', title="Kota", axis=alt.Axis(labelAngle=-45, grid=True, gridColor='rgba(255, 255, 255, 0.08)', gridDash=[4, 4])), 
            y=alt.Y(f"{df_city.columns[1]}:Q", title="Total Pesanan", axis=grid_axis),
            tooltip=[df_city.columns[0], df_city.columns[1]]
        ).properties(height=380)
        st.altair_chart(chart_city, use_container_width=True)

with col2:
    st.markdown('#### <i class="isax isax-reserve"></i> Top 15 Jenis Masakan', unsafe_allow_html=True)
    if not df_cuisine.empty:
        df_cuisine_sorted = df_cuisine.sort_values(by=df_cuisine.columns[1], ascending=False).head(15)
        
        df_cuisine_sorted = df_cuisine_sorted.reset_index(drop=True)
        df_cuisine_sorted.index = df_cuisine_sorted.index + 1
        df_cuisine_sorted.index.name = 'Rank'
        
        chart_cuisine = alt.Chart(df_cuisine_sorted).mark_bar(color='#818CF8', cornerRadiusEnd=6).encode(
            x=alt.X(f"{df_cuisine.columns[0]}:N", sort='-y', title="Jenis Masakan", axis=alt.Axis(labelAngle=-45, grid=True, gridColor='rgba(255, 255, 255, 0.08)', gridDash=[4, 4])),
            y=alt.Y(f"{df_cuisine.columns[1]}:Q", title="Total Pesanan", axis=grid_axis),
            tooltip=[df_cuisine.columns[0], df_cuisine.columns[1]]
        ).properties(height=380)
        st.altair_chart(chart_cuisine, use_container_width=True)

st.divider()

# --- 3. TABEL PERFORMA RESTORAN ---
st.markdown('### <i class="isax isax-shop"></i> Performa Restoran Unggulan', unsafe_allow_html=True)
if not df_top_resto.empty:
    df_resto_clean = df_top_resto[df_top_resto['restaurant_name'] != 'Unknown Restaurant']
    
    df_resto_clean = df_resto_clean.reset_index(drop=True)
    df_resto_clean.index = df_resto_clean.index + 1
    df_resto_clean.index.name = 'No'
    
    st.dataframe(df_resto_clean.head(20), use_container_width=True)

st.divider()

# --- 4. ANALISIS PREDIKTIF: Tren Jam Sibuk ---
st.markdown('### <i class="isax isax-chart-21"></i> Analisis Prediktif: Tren Jam Sibuk', unsafe_allow_html=True)
st.markdown("<span style='color:#94A3B8;'>Memprediksi pola pesanan menggunakan regresi polinomial derajat 4.</span>", unsafe_allow_html=True)

if not df_hour.empty:
    df_hour = df_hour.sort_values(by=df_hour.columns[0]).reset_index(drop=True)
    df_hour.index = df_hour.index + 1
    df_hour.index.name = 'No'
    
    df_hour.columns = ['Jam', 'Total_Pesanan']
    
    x = df_hour['Jam'].values
    y = df_hour['Total_Pesanan'].values
    
    z = np.polyfit(x, y, 4)
    p = np.poly1d(z)
    df_hour['Garis Tren Prediksi'] = p(x)

    base = alt.Chart(df_hour).encode(
        x=alt.X('Jam:Q', title='Jam Operasional (0 - 23)', axis=alt.Axis(tickCount=12, labelAngle=0, grid=True, gridColor='rgba(255, 255, 255, 0.08)', gridDash=[4, 4]))
    )

    line_actual = base.mark_line(color='#38BDF8', opacity=0.3, strokeDash=[5,5]).encode(
        y=alt.Y('Total_Pesanan:Q', scale=alt.Scale(zero=False), title='Jumlah Pesanan', axis=grid_axis)
    )
    
    points_actual = base.mark_point(color='#38BDF8', size=60, filled=True).encode(
        y='Total_Pesanan:Q',
        tooltip=['Jam', 'Total_Pesanan']
    )
    
    line_pred = base.mark_line(color='#F8FAFC', size=4).encode(
        y='Garis Tren Prediksi:Q'
    )

    final_chart = alt.layer(line_actual, points_actual, line_pred).properties(height=450)
    
    st.altair_chart(final_chart, use_container_width=True)
    
    # Legend Kustom
    st.markdown("""
        <div style="display: flex; gap: 20px; justify-content: center; margin-top: -10px; color: #94A3B8; font-size: 14px;">
            <div><span style="color: #F8FAFC; font-weight: bold;">—</span> Garis Tren Prediksi</div>
            <div><span style="color: #38BDF8; font-weight: bold;">- -</span> Data Aktual</div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.info("Data orders_by_hour tidak ditemukan.")