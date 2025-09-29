# -*- coding: utf-8 -*-
"""
Created on Tue Sep 30 01:08:41 2025

@author: HP
"""

import pandas as pd
import os

# --- Configuration ---
input_file = 'Final Distribution 2025.xlsx'
column_to_split_by = 'Assigned Project'
output_folder = 'Split_Files_Output' 

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 1. Read the Excel file
df = pd.read_excel(input_file)

# 2. Group the DataFrame by the specific column
# The 'groupby' method is the key to this solution
grouped = df.groupby(column_to_split_by)

# 3. and 4. Iterate through the groups and save each to a new file
for value, group_df in grouped:
    # Construct a clean, safe filename from the unique value
    # You may want more robust cleaning for special characters if your values are messy
    safe_filename = str(value).replace('/', '_').replace('\\', '_').replace(':', '_')  
    
    # Create the full path for the new Excel file
    output_path = os.path.join(output_folder, f'{safe_filename}.xlsx')
    
    # Save the group DataFrame to a new Excel file
    # index=False prevents writing the DataFrame's index as a column
    group_df.to_excel(output_path, index=False)
    print(f'Saved file: {output_path}')