import streamlit as st
import pandas as pd
import plotly.express as px
import os

# data
@st.cache_data
def load_data():
    # combined data
    return pd.read_excel('./output/combined_data.xlsx')

data = load_data()


def slugify(value):
    """Format file paths to avoid issues with spaces or special characters."""
    return value.replace(" ", "_").replace("/", "_")

# Sidebar navigation
st.sidebar.title("Navigasi Halaman")
page = st.sidebar.radio("Pilih Halaman:", ["Jelajah Data", "Analisis"])

# Header and banner
st.image("./assets/banner.jpg", use_container_width=True)
st.markdown("### Dashboard Analisis Perdagangan Produk Petrokimia")
st.markdown("**Visualisasi dan eksplorasi data perdagangan global berdasarkan negara, produk, dan tipe perdagangan.**")

# Jelajah Data Page
if page == "Jelajah Data":
    st.title("📊 Jelajah Data Perdagangan")
    st.write("**Gunakan filter di sidebar untuk menjelajahi data.**")

    # Filter options
    st.sidebar.header("Filter Data")
    countries = ["Semua"] + sorted(data['Country'].unique())
    products = ["Semua"] + sorted(data['Product'].unique())
    trade_types = ["Export", "Import"]

    selected_country = st.sidebar.selectbox("Pilih Negara:", countries)
    selected_product = st.sidebar.selectbox("Pilih Produk:", products)
    selected_trade_type = st.sidebar.radio("Pilih Tipe Perdagangan:", trade_types)
    year_range = st.sidebar.slider(
        "Pilih Rentang Tahun:",
        int(data['Year'].min()),  # Minimum year
        int(data['Year'].max()),  # Maximum year
        (int(data['Year'].min()), int(data['Year'].max()))  
    )

    # Filter data
    filtered_data = data[
        (data['Year'] >= year_range[0]) &
        (data['Year'] <= year_range[1]) &
        (data['Trade_Type'] == selected_trade_type)
    ]

    if selected_country != "Semua":
        filtered_data = filtered_data[filtered_data['Country'] == selected_country]

    if selected_product != "Semua":
        filtered_data = filtered_data[filtered_data['Product'] == selected_product]

    # menghilangkan koma
    filtered_data['Year'] = filtered_data['Year'].astype(int)

    
    filtered_data = filtered_data.reset_index(drop=True)

    # Display data and statistics
    st.subheader(f"Data Perdagangan ({selected_trade_type})")
    st.markdown(f"**Negara: {selected_country} | Produk: {selected_product} | Tahun: {year_range[0]} - {year_range[1]}**")
    st.dataframe(filtered_data.style.format({"Year": "{:.0f}"}), use_container_width=True)

    if not filtered_data.empty:
        st.markdown("#### Statistik")
        total_quantity = filtered_data["Quantity (Tons)"].sum()
        total_years = filtered_data["Year"].nunique()
        st.metric("Total Perdagangan (Tons)", f"{total_quantity:,.0f}")
        st.metric("Rentang Tahun", f"{year_range[0]} - {year_range[1]} ({total_years} Tahun)")

        # Plot distribution of Quantity
        fig = px.histogram(filtered_data, x="Year", y="Quantity (Tons)", color="Country", barmode="group",
                           title="Distribusi Perdagangan per Tahun")
        st.plotly_chart(fig, use_container_width=True)

# Analisis Page
elif page == "Analisis":
    st.title("📈 Analisis Perdagangan")
    st.write("**Visualisasi hasil analisis berdasarkan data yang tersedia.**")

    # Filter
    st.sidebar.header("Filter Analisis")
    analysis_type = st.sidebar.radio("Pilih Analisis:", ["Global", "Country", "Product"])

    if analysis_type == "Global":
        st.subheader("🌍 Analisis Global")
        global_gap_path = "./output/analysis/global/global_trade_gap.png"
        global_trends_path = "./output/analysis/global/global_trade_trends.png"

        if os.path.exists(global_gap_path):
            st.image(global_gap_path, caption="Global Trade Gap", use_container_width=True)
        else:
            st.error("File grafik 'Global Trade Gap' tidak ditemukan.")

        if os.path.exists(global_trends_path):
            st.image(global_trends_path, caption="Global Trade Trends", use_container_width=True)
        else:
            st.error("File grafik 'Global Trade Trends' tidak ditemukan.")

    elif analysis_type == "Country":
        st.subheader("📍 Analisis per Negara")
        countries = sorted(data['Country'].unique())
        selected_country = st.sidebar.selectbox("Pilih Negara:", countries)

        country_slug = slugify(selected_country)
        country_dir = f"./output/analysis/countries/{country_slug}"
        if os.path.exists(country_dir):
            total_trade_path = f"{country_dir}/{country_slug}_total_trade.png"
            export_path = f"{country_dir}/{country_slug}_top_export_products.png"
            import_path = f"{country_dir}/{country_slug}_top_import_products.png"

            if os.path.exists(total_trade_path):
                st.image(total_trade_path, caption="Total Trade", use_container_width=True)
            else:
                st.warning("Grafik Total Trade tidak ditemukan.")

            if os.path.exists(export_path):
                st.image(export_path, caption="Top Export Products", use_container_width=True)
            else:
                st.warning("Grafik Top Export Products tidak ditemukan.")

            if os.path.exists(import_path):
                st.image(import_path, caption="Top Import Products", use_container_width=True)
            else:
                st.warning("Grafik Top Import Products tidak ditemukan.")

            # Produk spesifik per negara
            st.subheader(f"Analisis Produk untuk {selected_country}")
            product_dir = f"{country_dir}/{country_slug}_products"
            if os.path.exists(product_dir):
                product_files = os.listdir(product_dir)
                for product_file in sorted(product_files):
                    if product_file.endswith(".png"):
                        product_name = product_file.replace("_trade.png", "").replace("_", " ")
                        st.image(f"{product_dir}/{product_file}", caption=f"{product_name} Trade Trends")
            else:
                st.warning("Grafik produk untuk negara ini tidak ditemukan.")
        else:
            st.error(f"Data untuk {selected_country} tidak ditemukan.")

    elif analysis_type == "Product":
        st.subheader("🛠️ Analisis per Produk")
        products = sorted(data['Product'].unique())
        selected_product = st.sidebar.selectbox("Pilih Produk:", products)

        product_slug = slugify(selected_product)
        product_path = f"./output/analysis/products/{product_slug}_trade.png"

        if os.path.exists(product_path):
            st.image(product_path, caption=f"Trade Analysis for {selected_product}", use_container_width=True)
        else:
            st.error(f"Data untuk produk {selected_product} tidak ditemukan.")
