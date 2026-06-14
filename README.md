# Food Delivery Big Data Pipeline

Proyek ini merupakan Tugas Besar Big Data dengan topik Food Delivery. Proyek ini bertujuan membangun end-to-end data pipeline mulai dari data collection, ingestion, processing, analytics, hingga presentation/dashboard.

## Dataset

Dataset yang digunakan terdiri dari:

1. `swiggy.csv`  
   Data mentah awal food delivery.

2. `restaurant_master.csv`  
   Data master restoran/merchant yang sudah dirapikan.

3. `simulated_food_orders.csv`  
   Data transaksi food delivery hasil simulasi yang sudah diperbesar.

4. `stream_order_sample.csv`  
   Data sampel transaksi food delivery untuk simulasi streaming atau Velocity.

## Struktur Folder

```text
TUBES_BIGDATA/
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── raw/
│   │   └── swiggy.csv
│   │
│   ├── processed/
│   │   ├── restaurant_master.csv
│   │   └── simulated_food_orders.csv
│   │
│   └── stream/
│       ├── stream_order_sample.csv
│       └── stream_input/
│
├── src/
│   ├── producer_simple.py
│   └── anggota3_processing.py
│
├── output/
│   └── summary_dataset.csv
│
└── docs/