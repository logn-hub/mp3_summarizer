import pandas as pd
import sys
import os

def append_to_excel(file_path, excel_path='요약본.xlsx'):
    # Read the temporary DataFrame
    new_df = pd.read_excel(file_path)

    # Check if the existing Excel file exists
    if os.path.exists(excel_path):
        # Read the existing Excel file
        existing_df = pd.read_excel(excel_path)
        # Append the new data
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        # If the file doesn't exist, just use the new DataFrame
        combined_df = new_df

    # Save the combined DataFrame back to the Excel file
    combined_df.to_excel(excel_path, index=False)
    print(f"Data appended to '{excel_path}'")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python file_save.py <file_path>")
        sys.exit(1)

    temp_file_path = sys.argv[1]
    append_to_excel(temp_file_path)
# <-----------------------------------------------------------------------> #
