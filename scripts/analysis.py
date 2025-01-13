import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Direktori Output
OUTPUT_DIR = './output/analysis'


def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


if os.path.exists(OUTPUT_DIR):
    import shutil
    shutil.rmtree(OUTPUT_DIR)

# Folder untuk masing-masing analisis
ensure_dir(f"{OUTPUT_DIR}/countries")
ensure_dir(f"{OUTPUT_DIR}/products")
ensure_dir(f"{OUTPUT_DIR}/global")


data_file = './output/combined_data.xlsx'
print("Memuat data...")
data = pd.read_excel(data_file)


def save_plot(fig, path):
    ensure_dir(os.path.dirname(path))
    fig.savefig(path)
    plt.close(fig)

# Global Analysis
def analyze_global(data):
    print("Analisis Global...")
    global_dir = f"{OUTPUT_DIR}/global"

    # Top 10 trade gap produk secara global
    trade_gap = data.groupby("Product").agg({"Quantity (Tons)": "sum"}).reset_index()
    trade_gap = trade_gap.sort_values(by="Quantity (Tons)", ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.barplot(data=trade_gap, x="Quantity (Tons)", y="Product", palette="coolwarm", ax=ax)
    ax.set_title("Top 10 Produk dengan Trade Gap Tertinggi (Global)")
    ax.set_xlabel("Trade Gap (Tons)")
    save_plot(fig, f"{global_dir}/global_trade_gap.png")

    # Global export vs import dalam 10 tahun terakhir
    yearly = data.groupby(["Year", "Trade_Type"]).agg({"Quantity (Tons)": "sum"}).reset_index()
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.lineplot(data=yearly, x="Year", y="Quantity (Tons)", hue="Trade_Type", marker="o", ax=ax)
    ax.set_title("Perbandingan Ekspor dan Impor Global per Tahun")
    save_plot(fig, f"{global_dir}/global_trade_trends.png")

# Per-Country Analysis
def analyze_countries(data):
    print("Analisis per Negara...")
    countries = data["Country"].unique()

    for country in countries:
        print(f"  - Analisis untuk {country}...")
        country_data = data[data["Country"] == country]
        country_dir = f"{OUTPUT_DIR}/countries/{country.replace(' ', '_')}"
        os.makedirs(country_dir, exist_ok=True)

        # Total trade tiap tahun
        yearly = country_data.groupby(["Year", "Trade_Type"]).agg({"Quantity (Tons)": "sum"}).reset_index()
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.barplot(data=yearly, x="Year", y="Quantity (Tons)", hue="Trade_Type", ax=ax)
        ax.set_title(f"Total Perdagangan untuk {country}")
        save_plot(fig, f"{country_dir}/{country}_total_trade.png")

        # Top 10 produk komoditi ekspor
        top_export = (
            country_data[country_data["Trade_Type"] == "Export"]
            .groupby("Product")
            .agg({"Quantity (Tons)": "sum"})
            .reset_index()
            .sort_values(by="Quantity (Tons)", ascending=False)
            .head(10)
        )
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.barplot(data=top_export, x="Quantity (Tons)", y="Product", ax=ax, palette="Greens_r")
        ax.set_title(f"10 Produk Ekspor Tertinggi - {country}")
        save_plot(fig, f"{country_dir}/{country}_top_export_products.png")

        # Top 10 produk komuniti import
        top_import = (
            country_data[country_data["Trade_Type"] == "Import"]
            .groupby("Product")
            .agg({"Quantity (Tons)": "sum"})
            .reset_index()
            .sort_values(by="Quantity (Tons)", ascending=False)
            .head(10)
        )
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.barplot(data=top_import, x="Quantity (Tons)", y="Product", ax=ax, palette="Reds_r")
        ax.set_title(f"10 Produk Impor Tertinggi - {country}")
        save_plot(fig, f"{country_dir}/{country}_top_import_products.png")

        # Tren perdagangan Produk untuk tiap negara
        product_dir = f"{country_dir}/{country.replace(' ', '_')}_products"
        os.makedirs(product_dir, exist_ok=True)

        for product in country_data["Product"].unique():
            product_data = country_data[country_data["Product"] == product]
            if not product_data.empty:
                fig, ax = plt.subplots(figsize=(8, 6))
                sns.lineplot(
                    data=product_data,
                    x="Year",
                    y="Quantity (Tons)",
                    hue="Trade_Type",
                    marker="o",
                    ax=ax
                )
                ax.set_title(f"Tren Perdagangan untuk {product} di {country}")
                ax.set_xlabel("Tahun")
                ax.set_ylabel("Quantity (Tons)")
                save_plot(fig, f"{product_dir}/{product.replace('/', '_')}_trade.png")

# Per-Product Analysis
def analyze_products(data):
    print("Analisis per Produk...")
    products = data["Product"].unique()

    for product in products:
        print(f"  - Analisis untuk {product}...")
        product_data = data[data["Product"] == product]
        product_dir = f"{OUTPUT_DIR}/products"

        # Perdagangan global untuk masing-masing produk
        yearly = product_data.groupby(["Year", "Trade_Type"]).agg({"Quantity (Tons)": "sum"}).reset_index()
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.lineplot(data=yearly, x="Year", y="Quantity (Tons)", hue="Trade_Type", marker="o", ax=ax)
        ax.set_title(f"Tren Perdagangan untuk {product}")
        save_plot(fig, f"{product_dir}/{product.replace('/', '_')}_trade.png")

# Analsis
analyze_global(data)
analyze_countries(data)
analyze_products(data)

print(f"Semua analisis selesai! Data telah disimpan di folder {OUTPUT_DIR}.")
