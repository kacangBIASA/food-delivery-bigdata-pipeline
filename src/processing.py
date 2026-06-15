from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg, to_timestamp, year, month, hour

# Membuat Spark session
spark = SparkSession.builder \
    .appName("Food Delivery Processing") \
    .master("local[*]") \
    .config("spark.sql.shuffle.partitions", "4") \
    .config("spark.local.dir", "spark-temp") \
    .getOrCreate()

# Load dataset
restaurants = spark.read.option("header", True) \
    .option("inferSchema", False) \
    .option("multiLine", True) \
    .option("quote", '"') \
    .option("escape", '"') \
    .csv("data/processed/restaurant_master.csv")

orders = spark.read.option("header", True) \
    .option("inferSchema", False) \
    .option("multiLine", True) \
    .option("quote", '"') \
    .option("escape", '"') \
    .csv("data/processed/simulated_food_orders.csv")

print("Jumlah data restaurant:", restaurants.count())
print("Jumlah data orders:", orders.count())

# Cleaning data
restaurants_clean = restaurants.dropDuplicates(["restaurant_id"]) \
    .withColumn("rating", col("rating").cast("double")) \
    .withColumn("rating_count", col("rating_count").cast("double"))

orders_clean = orders.dropDuplicates(["order_id"]) \
    .withColumn("order_time", to_timestamp(col("order_time"))) \
    .withColumn("quantity", col("quantity").cast("double")) \
    .withColumn("delivery_duration_minutes", col("delivery_duration_minutes").cast("double"))

# Pilih kolom penting
restaurants_selected = restaurants_clean.select(
    "restaurant_id",
    "restaurant_name",
    "city",
    "rating",
    "rating_count",
    "cuisine",
    "address"
)

orders_selected = orders_clean.select(
    "order_id",
    "customer_id",
    "driver_id",
    "restaurant_id",
    "quantity",
    "payment_method",
    "order_status",
    "order_time",
    "delivery_duration_minutes"
)

# Join data berdasarkan restaurant_id
joined_data = orders_selected.join(
    restaurants_selected,
    on="restaurant_id",
    how="left"
)

# Tambahkan kolom waktu
joined_data = joined_data \
    .withColumn("order_year", year(col("order_time"))) \
    .withColumn("order_month", month(col("order_time"))) \
    .withColumn("order_hour", hour(col("order_time")))

# Simpan data hasil join
joined_data.write.mode("overwrite").csv(
    "output/joined_food_orders",
    header=True
)

# Analisis 1: Total order per kota
orders_by_city = joined_data.groupBy("city") \
    .agg(count("order_id").alias("total_orders")) \
    .orderBy(col("total_orders").desc())

orders_by_city.coalesce(1).write.mode("overwrite").csv(
    "output/orders_by_city",
    header=True
)

# Analisis 2: Cuisine paling banyak dipesan
orders_by_cuisine = joined_data.groupBy("cuisine") \
    .agg(count("order_id").alias("total_orders")) \
    .orderBy(col("total_orders").desc())

orders_by_cuisine.coalesce(1).write.mode("overwrite").csv(
    "output/orders_by_cuisine",
    header=True
)

# Analisis 3: Status pesanan
orders_by_status = joined_data.groupBy("order_status") \
    .agg(count("order_id").alias("total_orders")) \
    .orderBy(col("total_orders").desc())

orders_by_status.coalesce(1).write.mode("overwrite").csv(
    "output/orders_by_status",
    header=True
)

# Analisis 4: Metode pembayaran
payment_method_summary = joined_data.groupBy("payment_method") \
    .agg(count("order_id").alias("total_orders")) \
    .orderBy(col("total_orders").desc())

payment_method_summary.coalesce(1).write.mode("overwrite").csv(
    "output/payment_method_summary",
    header=True
)

# Analisis 5: Rata-rata durasi pengiriman per kota
avg_delivery_by_city = joined_data.groupBy("city") \
    .agg(avg("delivery_duration_minutes").alias("avg_delivery_duration")) \
    .orderBy(col("avg_delivery_duration").desc())

avg_delivery_by_city.coalesce(1).write.mode("overwrite").csv(
    "output/avg_delivery_by_city",
    header=True
)

# Analisis 6: Restoran dengan order terbanyak
top_restaurants = joined_data.groupBy(
    "restaurant_name",
    "city",
    "cuisine",
    "rating"
).agg(
    count("order_id").alias("total_orders")
).orderBy(
    col("total_orders").desc()
)

top_restaurants.coalesce(1).write.mode("overwrite").csv(
    "output/top_restaurants",
    header=True
)

# Analisis 7: Order berdasarkan bulan
orders_by_month = joined_data.groupBy("order_year", "order_month") \
    .agg(count("order_id").alias("total_orders")) \
    .orderBy("order_year", "order_month")

orders_by_month.coalesce(1).write.mode("overwrite").csv(
    "output/orders_by_month",
    header=True
)

# Analisis 8: Order berdasarkan jam
orders_by_hour = joined_data.groupBy("order_hour") \
    .agg(count("order_id").alias("total_orders")) \
    .orderBy("order_hour")

orders_by_hour.coalesce(1).write.mode("overwrite").csv(
    "output/orders_by_hour",
    header=True
)

print("Processing dan analisis selesai.")
spark.stop()