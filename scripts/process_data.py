import pandas as pd
import os

def load_and_combine_data(folder_path):
    combined_data = []  
    print(f"Processing files in folder: {folder_path}")
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".xlsx"): 
            file_path = os.path.join(folder_path, filename)
            print(f"Processing file: {filename}...")

            # file Excel
            try:
                
                df = pd.read_excel(file_path, skiprows=4, header=0)
                print(f"Columns found in {filename}: {list(df.columns)}")
                
                # Country
                if "Exporters" in df.columns:
                    df = df.rename(columns={"Exporters": "Country"})
                elif "Importers" in df.columns:
                    df = df.rename(columns={"Importers": "Country"})
                else:
                   
                    first_column = df.columns[0]
                    print(f"Assuming '{first_column}' is 'Country' column.")
                    df = df.rename(columns={first_column: "Country"})

                # nama produk berdasarkan nama file
                try:
                    
                    product_name = filename.split("_", 1)[1].replace(".xlsx", "").replace("_", " ")
                    df["Product"] = product_name
                except IndexError:
                    print(f"Error: Could not extract product name from file {filename}. Skipping this file.")
                    continue

                # kolom Trade_Type (Export/Import)
                if "export" in filename.lower():
                    trade_type = "Export"
                elif "import" in filename.lower():
                    trade_type = "Import"
                else:
                    trade_type = "Unknown"
                df["Trade_Type"] = trade_type

                # kolom tahun
                year_columns = {}
                for col in df.columns:
                    if "Exported quantity" in col or "Imported quantity" in col:
                        
                        if "." in col:
                            parts = col.split(".")
                            if len(parts) > 1 and parts[1].isdigit():
                                year = 2014 + int(parts[1])  
                                year_columns[col] = str(year)
                            else:
                                year_columns[col] = "2014"  
                        else:
                            year_columns[col] = "2014"

                
                df = df.rename(columns=year_columns)

                # kolom tahun dan Quantity
                df_long = df.melt(
                    id_vars=["Country", "Product", "Trade_Type"],
                    var_name="Year",
                    value_name="Quantity (Tons)"
                )

               
                df_long = df_long[df_long["Year"].str.isdigit()]

                # data kosong atau "No Quantity" = 0
                df_long["Quantity (Tons)"] = df_long["Quantity (Tons)"].replace(["No Quantity", None, "nan"], 0)
                df_long["Quantity (Tons)"] = pd.to_numeric(df_long["Quantity (Tons)"], errors="coerce").fillna(0)

                # combined_data
                combined_data.append(df_long)
            except Exception as e:
                print(f"Error processing file {filename}: {e}")
    
    # DataFrame
    if combined_data:
        combined_data = pd.concat(combined_data, ignore_index=True)
    else:
        print("No valid data found.")
        combined_data = pd.DataFrame()  
    
    return combined_data


# Main script
if __name__ == "__main__":
    
    folder_path = "data/"  
    
    # Load dan gabungkan data
    combined_data = load_and_combine_data(folder_path)
    
    # Jika data berhasil digabungkan
    if not combined_data.empty:
        # Atur urutan kolom
        combined_data = combined_data[["Country", "Year", "Quantity (Tons)", "Product", "Trade_Type"]]
        
        # Simpan ke file output
        output_path = "output/combined_data.xlsx"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)  # Buat folder output jika belum ada
        combined_data.to_excel(output_path, index=False)
        print(f"Data successfully saved to {output_path}")
    else:
        print("No data processed.")
