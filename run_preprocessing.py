import pandas as pd
import numpy as np

# 1. Loading Data in chunks and filtering crops
chunk_size = 500000
chunks = []
target_crops = ['Wheat', 'Maize', 'Rice']
pattern = '|'.join(target_crops)

print("Starting to read and filter 1.7GB Dataset... this may take a moment.")
for chunk in pd.read_csv('Trade_DetailedTradeMatrix_E_All_Data_NOFLAG.csv', chunksize=chunk_size, encoding='latin1'):
    mask = chunk['Item'].str.contains(pattern, case=False, na=False)
    chunks.append(chunk[mask])

df_raw = pd.concat(chunks, ignore_index=True)
print("Filtering complete. Rows retrieved:", df_raw.shape[0])

# 2. Filtering Irrelevant Columns
print("Cleaning Data...")
cols_to_drop = ['Reporter Country Code', 'Reporter Country Code (M49)', 
                'Partner Country Code', 'Partner Country Code (M49)', 
                'Item Code', 'Item Code (CPC)', 'Element Code']
df_clean = df_raw.drop(columns=[col for col in cols_to_drop if col in df_raw.columns])

# 3. Reshaping Data
year_cols = [col for col in df_clean.columns if col.startswith('Y') and col[1:].isdigit()]
id_cols = [col for col in df_clean.columns if col not in year_cols]

df_melted = pd.melt(df_clean, id_vars=id_cols, value_vars=year_cols, var_name='Year', value_name='Value')

# 4. Final Processing
df_melted['Year'] = df_melted['Year'].str.replace('Y', '').astype(int)
df_melted = df_melted.dropna(subset=['Value'])
df_melted = df_melted.drop_duplicates()
df_melted = df_melted[df_melted['Value'] >= 0]

# 5. Save Preprocessed dataset
output_file = 'Preprocessed_Trade_Data.csv'
df_melted.to_csv(output_file, index=False)
print(f"Preprocessed dataset saved successfully to {output_file}!")
