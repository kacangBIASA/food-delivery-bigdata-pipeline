import streamlit as st
import pandas as pd
import glob
import os
import numpy as np
import altair as alt

# Konfigurasi halaman
st.set_page_config(page_title="Food Delivery Analytics", layout="wide")

# CSS Kustom untuk tampilan yang lebih profesional
st.markdown("""
    <style>
    .main { padding: 1rem 2rem; }
    h1, h2, h3 { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    [data-testid="stMetricValue"] { font-size: 28px; color: #64B5F6; }
    </style>
""", unsafe_allow_html=True)

st.title("🍔 Food Delivery Big Data Dashboard")
st.markdown("Visualisasi deskriptif dan prediktif dari end-to-end data pipeline.")

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
st.header("Ringkasan Bisnis")
col_m1, col_m2, col_m3 = st.columns(3)

if not df_city.empty:
    total_orders = df_city.iloc[:, 1].sum()
    col_m1.metric("Total Keseluruhan Pesanan", f"{total_orders:,.0f}")
if not df_top_resto.empty:
    avg_rating = df_top_resto['rating'].mean()
    col_m2.metric("Rata-rata Rating Restoran", f"{avg_rating:.2f} ⭐")
if not df_cuisine.empty:
    total_cuisines = len(df_cuisine)
    col_m3.metric("Varian Jenis Masakan", f"{total_cuisines}")

st.divider()

# --- 2. ANALISIS DESKRIPTIF (GRAFIK ALTAIR) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 15 Kota dengan Pesanan Terbanyak")
    if not df_city.empty:
        df_city_sorted = df_city.sort_values(by=df_city.columns[1], ascending=False).head(15)
        df_city_sorted.index.name = 'Rank' 
        
        chart_city = alt.Chart(df_city_sorted.reset_index()).mark_bar(color='#64B5F6', cornerRadiusEnd=5).encode(
            x=alt.X(f"{df_city.columns[0]}:N", sort='-y', title="Kota", axis=alt.Axis(labelAngle=-45)), 
            y=alt.Y(f"{df_city.columns[1]}:Q", title="Total Pesanan"),
            tooltip=['Rank', df_city.columns[0], df_city.columns[1]]
        ).properties(height=400)
        st.altair_chart(chart_city, use_container_width=True)

with col2:
    st.subheader("Top 15 Jenis Masakan Paling Diminati")
    if not df_cuisine.empty:
        df_cuisine_sorted = df_cuisine.sort_values(by=df_cuisine.columns[1], ascending=False).head(15)
        df_cuisine_sorted.index.name = 'Rank'
        
        chart_cuisine = alt.Chart(df_cuisine_sorted.reset_index()).mark_bar(color='#81C784', cornerRadiusEnd=5).encode(
            x=alt.X(f"{df_cuisine.columns[0]}:N", sort='-y', title="Jenis Masakan", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y(f"{df_cuisine.columns[1]}:Q", title="Total Pesanan"),
            tooltip=['Rank', df_cuisine.columns[0], df_cuisine.columns[1]]
        ).properties(height=400)
        st.altair_chart(chart_cuisine, use_container_width=True)

st.divider()

# --- 3. TABEL PERFORMA RESTORAN ---
st.header("Performa Restoran Unggulan")
if not df_top_resto.empty:
    df_resto_clean = df_top_resto[df_top_resto['restaurant_name'] != 'Unknown Restaurant']
    df_resto_clean = df_resto_clean.reset_index(drop=True)
    df_resto_clean.index = df_resto_clean.index + 1
    df_resto_clean.index.name = 'No'
    st.dataframe(df_resto_clean.head(20), use_container_width=True)

st.divider()

# --- 4. ANALISIS PREDIKTIF: Tren Jam Sibuk ---
st.header("📈 Analisis Prediktif: Tren Jam Sibuk")
st.markdown("Memprediksi pola pesanan menggunakan regresi polinomial derajat 4.")

if not df_hour.empty:
    df_hour = df_hour.sort_values(by=df_hour.columns[0])
    df_hour.columns = ['Jam', 'Total_Pesanan']
    
    x = df_hour['Jam'].values
    y = df_hour['Total_Pesanan'].values
    z = np.polyfit(x, y, 4)
    p = np.poly1d(z)
    df_hour['Garis Tren Prediksi'] = p(x)

    df_chart = df_hour.copy()
    df_chart.index.name = 'Row_ID' 

    base = alt.Chart(df_chart.reset_index()).encode(
        x=alt.X('Jam:Q', title='Jam Operasional (0 - 23)', axis=alt.Axis(tickCount=12, labelAngle=0))
    )

    line_actual = base.mark_line(color='#64B5F6', opacity=0.5, strokeDash=[5,5]).encode(
        y=alt.Y('Total_Pesanan:Q', scale=alt.Scale(zero=False), title='Jumlah Pesanan')
    )
    points_actual = base.mark_point(color='#64B5F6', size=50).encode(
        y='Total_Pesanan:Q',
        tooltip=['Jam', 'Total_Pesanan']
    )
    line_pred = base.mark_line(color='#FFFFFF', size=4).encode(
        y='Garis Tren Prediksi:Q'
    )

    final_chart = alt.layer(line_actual, points_actual, line_pred).properties(height=500)
    
    st.altair_chart(final_chart, use_container_width=True)
    st.info("💡 Garis Putih: Arah tren pesanan | Titik Biru: Data aktual tiap jam.")
    
    # BAGIAN TABEL EXPANDER SUDAH DIHAPUS SEPERTI PERMINTAAN KAMU
else:
    st.info("Data orders_by_hour tidak ditemukan.")