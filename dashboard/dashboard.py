import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Set up Streamlit page layout
st.set_page_config(page_title="Customer Satisfaction Dashboard", layout="wide")
# Memastikan seaborn menggunakan style yang tepat
sns.set(style="darkgrid")

# Fungsi untuk memuat data
@st.cache_data
def load_data():
    orders_ollist = pd.read_csv('/data/orders_dataset.csv')
    customers_ollist = pd.read_csv('/data/customers_dataset.csv')
    order_reviews_ollist = pd.read_csv('/data/order_reviews_dataset.csv')
    order_items_ollist = pd.read_csv('/data/order_items_dataset.csv')
    products_ollist = pd.read_csv('/data/products_dataset.csv')

    return orders_ollist, customers_ollist, order_reviews_ollist, order_items_ollist, products_ollist

# Memuat data
orders_ollist, customers_ollist, order_reviews_ollist, order_items_ollist, products_ollist = load_data()

# Header
st.title("E-Commerce Customer Satisfaction and Sales Analysis")

# Bagian 1: Analisis Jumlah Pesanan per Negara Bagian
st.subheader("Total Orders by Customer State")

# Menggabungkan data
merged_data = orders_ollist.merge(customers_ollist, on='customer_id', how='inner')
merged_data = merged_data.merge(order_items_ollist, on='order_id', how='inner')
merged_data = merged_data.merge(products_ollist, on='product_id', how='inner')

# Menghitung jumlah pesanan per negara bagian
state_analysis = merged_data.groupby('customer_state')['order_id'].count().reset_index()
state_analysis.columns = ['customer_state', 'total_orders']

# Menampilkan hasil analisis jumlah pesanan per negara bagian
st.write(state_analysis)

# Visualisasi: Jumlah pesanan per negara bagian
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(data=state_analysis, x='customer_state', y='total_orders', palette='viridis', ax=ax)
ax.set_title('Total Orders by Customer State', fontsize=16)
ax.set_xlabel('Customer State', fontsize=14)
ax.set_ylabel('Total Orders', fontsize=14)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

# Tampilkan grafik di Streamlit
st.pyplot(fig)

# Bagian 2: Kategori Produk Terlaris per Negara Bagian
st.subheader("Top Product Categories by Customer State")

# Menghitung jumlah pesanan per kategori produk per negara bagian
category_analysis = merged_data.groupby(['customer_state', 'product_category_name'])['order_id'].count().reset_index()
category_analysis.columns = ['customer_state', 'product_category_name', 'total_orders']

# Ambil kategori terlaris (jumlah tertinggi) per negara bagian
top_category_per_state = category_analysis.loc[category_analysis.groupby('customer_state')['total_orders'].idxmax()]

# Menampilkan hasil analisis kategori produk terlaris per negara bagian
st.write(top_category_per_state)

# Visualisasi: Kategori Produk Terlaris per Negara Bagian
fig, ax = plt.subplots(figsize=(14, 8))
sns.barplot(data=top_category_per_state,
            x='customer_state',
            y='total_orders',
            hue='product_category_name',
            palette='Set2',
            ci=None,
            ax=ax)

# Judul dan label
ax.set_title('Top Product Categories by Customer State', fontsize=16)
ax.set_xlabel('Customer State', fontsize=14)
ax.set_ylabel('Number of Orders', fontsize=14)

# Menyesuaikan sumbu x
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=12)

# Menampilkan legenda dengan format yang lebih jelas
ax.legend(title='Product Category', fontsize=12, title_fontsize='13')

# Menambahkan anotasi jumlah pesanan di atas batang
for p in ax.patches:
    ax.annotate(f'{int(p.get_height())}',
                (p.get_x() + p.get_width() / 2.,
                 p.get_height()),
                ha='center',
                va='bottom',
                fontsize=10,
                color='black')

# Menyesuaikan layout
plt.tight_layout()
st.pyplot(fig)

# Bagian 3: Hubungan antara Waktu Pengiriman dan Skor Ulasan
st.subheader("Relationship Between Delivery Time and Review Score")

# Menghitung waktu penerimaan paket dalam hari
orders_ollist['delivery_time'] = (pd.to_datetime(orders_ollist['order_delivered_customer_date']) -
                                   pd.to_datetime(orders_ollist['order_purchase_timestamp'])).dt.days

# Menggabungkan dengan tabel ulasan
merged_data_reviews = orders_ollist.merge(order_reviews_ollist, on='order_id', how='inner')

# Visualisasi hubungan antara waktu penerimaan paket dan skor ulasan
fig, ax = plt.subplots(figsize=(12, 6))
sns.scatterplot(data=merged_data_reviews, x='delivery_time', y='review_score', alpha=0.6, ax=ax)

ax.set_title('Relationship Between Delivery Time and Review Score', fontsize=16)
ax.set_xlabel('Delivery Time (days)', fontsize=14)
ax.set_ylabel('Review Score', fontsize=14)
ax.grid(True)

# Tampilkan grafik di Streamlit
plt.tight_layout()
st.pyplot(fig)

# Bagian 4: Review Produk per Kategori Produk
st.subheader("Average Review Score by Product Category")

# Menggabungkan data untuk mendapatkan informasi produk
merged_data_products = order_reviews_ollist.merge(orders_ollist, on='order_id', how='inner')
merged_data_products = merged_data_products.merge(order_items_ollist, on='order_id', how='inner')
merged_data_products = merged_data_products.merge(products_ollist, on='product_id', how='inner')

# Hitung jumlah item terjual dan rata-rata skor ulasan per produk
product_analysis = merged_data_products.groupby('product_category_name')['order_item_id'].count().reset_index()
product_analysis.columns = ['product_category_name', 'total_items_sold']

average_scores = merged_data_products.groupby('product_category_name')['review_score'].mean().reset_index()
average_scores.columns = ['product_category_name', 'average_review_score']

# Gabungkan hasil analisis
product_analysis = product_analysis.merge(average_scores, on='product_category_name', how='left')

# Visualisasi: Rata-rata skor ulasan per kategori produk
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(data=product_analysis, x='product_category_name', y='average_review_score', ax=ax)

ax.set_title('Average Review Score by Product Category', fontsize=16)
ax.set_xlabel('Product Category Name', fontsize=14)
ax.set_ylabel('Average Review Score', fontsize=14)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

# Menambahkan jumlah item terjual di atas batang
for index, row in product_analysis.iterrows():
    ax.text(index, row['average_review_score'], row['total_items_sold'], color='black', ha='center')

# Tampilkan grafik di Streamlit
plt.tight_layout()
st.pyplot(fig)

# Informasi tambahan dan kesimpulan
st.subheader("Key Insights")
st.write("""
- Analisis menunjukkan negara bagian mana yang memiliki jumlah pesanan tertinggi.
- Kategori produk yang paling banyak dipesan dapat bervariasi antar negara bagian.
- Visualisasi hubungan antara waktu pengiriman dan skor ulasan menunjukkan bagaimana waktu pengiriman mempengaruhi kepuasan pelanggan.
- Analisis skor ulasan per kategori produk memberikan gambaran produk mana yang memiliki kepuasan pelanggan tertinggi.
""")
