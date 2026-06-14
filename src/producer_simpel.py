import os
import time
from datetime import datetime
import pandas as pd

# 1. Folder tujuan untuk menampung aliran data (berada di dalam stream_data)
output_folder = "stream_input"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 2. Baca file csv utama
csv_file = "stream_order_sample.csv"
df = pd.read_csv(csv_file)

# Bersihkan spasi gaib di nama kolom jika ada
df.columns = df.columns.str.strip()

print(f"Memulai simulasi streaming Velocity untuk {len(df)} data...\n")

# 3. Looping untuk memecah data satu per satu
for index, row in df.iterrows():
    single_row_df = pd.DataFrame([row])

    # Perbarui order_time menjadi waktu sekarang agar real-time
    single_row_df["order_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Ambil kolom pertama secara otomatis sebagai ID (Biar aman dari KeyError)
    kolom_pertama = df.columns[0]
    order_id = row[kolom_pertama]
    
    file_name = f"order_{order_id}.csv"
    file_path = os.path.join(output_folder, file_name)

    # Simpan sebagai CSV kecil di folder stream_input
    single_row_df.to_csv(file_path, index=False)

    # Menampilkan log streaming di terminal
    print(f"[STREAM IN] Drop file: {file_name} | {row['restaurant_name']} ({row['cuisine']})")

    # Jeda 2 detik per data (Simulasi karakteristik Velocity Big Data)
    time.sleep(2)

print("\nSemua data telah selesai dialirkan.")