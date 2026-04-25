import csv
import re

input_file = 'Trade_DetailedTradeMatrix_E_All_Data_NOFLAG.csv'
output_file = 'Preprocessed_Trade_Data.csv'

# Drops
cols_to_drop = {'Reporter Country Code', 'Reporter Country Code (M49)', 
                'Partner Country Code', 'Partner Country Code (M49)', 
                'Item Code', 'Item Code (CPC)', 'Element Code'}

target_crops = ['Wheat', 'Maize', 'Rice']

def contains_target(item_str):
    item_lower = item_str.lower()
    for crop in target_crops:
        if crop.lower() in item_lower:
            return True
    return False

print("Processing massively large CSV row by row. This uses almost NO Memory (Pure Python).")

with open(input_file, mode='r', encoding='latin1') as infile, \
     open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
    
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    
    # Read Header
    header = next(reader)
    
    # Analyze Header
    year_indices = []
    keep_indices = []
    item_idx = -1
    
    out_header = []
    
    for i, col in enumerate(header):
        if col == 'Item':
            item_idx = i
            
        if col.startswith('Y') and col[1:].isdigit():
            year_indices.append((i, col[1:])) # Ex: 'Y1986' -> '1986'
        elif col not in cols_to_drop:
            keep_indices.append(i)
            out_header.append(col)
            
    out_header.extend(['Year', 'Value'])
    writer.writerow(out_header)
    
    # Stream rows
    rows_processed = 0
    rows_written = 0
    seen = set() # To handle drop_duplicates
    
    for row in reader:
        rows_processed += 1
        if rows_processed % 1000000 == 0:
            print(f"Processed {rows_processed} rows...")
            
        # If pattern matches
        if len(row) > item_idx and contains_target(row[item_idx]):
            # Base info
            base_data = tuple(row[i] for i in keep_indices)
            
            # Melt Years
            for y_idx, year_val in year_indices:
                if y_idx < len(row):
                    val = row[y_idx]
                    # Drop Missing values and keep >= 0
                    if val.strip() != '':
                        try:
                            # Parse numeric
                            numeric_val = float(val)
                            if numeric_val >= 0:
                                # Create row fingerprint
                                out_row = base_data + (year_val, numeric_val)
                                if out_row not in seen:
                                    seen.add(out_row)
                                    writer.writerow(out_row)
                                    rows_written += 1
                        except ValueError:
                            pass # Ignored invalid values

print(f"Finished! Total Rows Scanned: {rows_processed}")
print(f"Total Rows Saved to Preprocessed Dataset: {rows_written}")
print(f"Saved directly to -> '{output_file}'")
