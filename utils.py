# utils.py
import pandas as pd
import csv
import os
from PyQt5.QtWidgets import QMessageBox

def read_numeric_data(file_path, parent=None, delimiter='\t', max_lines=100):
    """
    Reads a CSV or text file, skips metadata, detects headers and numeric data dynamically.
    Tries multiple delimiters if necessary.

    Parameters:
        file_path (str): Path to the CSV file.
        parent (QWidget): Parent widget for QMessageBox.
        delimiter (str): Delimiter used in the file (default is tab).
        max_lines (int): Maximum number of lines to search for numeric data.

    Returns:
        tuple: (df, x, y) where df is the cleaned DataFrame, and x, y are numpy arrays.
               Returns (None, None, None) if reading fails.
    """
    # List of delimiters to try
    delimiters = [delimiter, ',', ';'] if delimiter == '\t' else [delimiter]

    for delim in delimiters:
        header_row_index = None
        data_row_index = None

        try:
            # Read all lines from the file
            with open(file_path, 'r') as f:
                lines = f.readlines()

            # Iterate through the lines to find the header and data rows
            for i, line in enumerate(lines):
                if i >= max_lines:
                    break

                # Split the line using the current delimiter
                row = line.strip().split(delim)
                # Remove empty strings
                row = [cell.strip() for cell in row if cell.strip()]

                if not row:
                    continue

                if is_numeric_row(row):
                    data_row_index = i
                    break
                else:
                    header_row_index = i  # Potential header row

            if data_row_index is None:
                continue  # Try the next delimiter

            # Prepare the list of rows to skip
            skiprows = [i for i in range(data_row_index) if i != header_row_index]

            # Read the data
            df = pd.read_csv(
                file_path,
                delimiter=delim,
                skiprows=skiprows,
                header=None,
                engine='python'
            )

            if header_row_index is not None:
                # Read the header line to get the column names
                header_line = lines[header_row_index].strip()
                columns = [cell.strip() for cell in header_line.split(delim) if cell.strip()]

                # Ensure the number of columns matches
                if len(columns) != df.shape[1]:
                    columns = [f"Column {i+1}" for i in range(df.shape[1])]

                # Ensure columns are strings
                columns = [str(col) for col in columns]

                # Assign the columns
                df.columns = columns
            else:
                # No header detected, assign default column names
                df.columns = [f"Column {i+1}" for i in range(df.shape[1])]

            # Convert all columns to numeric where possible
            df = df.apply(pd.to_numeric, errors='coerce')

            # Drop rows where all values are NaN
            df.dropna(how='all', inplace=True)

            # Ensure there are at least two columns for X and Y
            if df.shape[1] < 2:
                continue  # Try the next delimiter

            # Extract X and Y columns
            x = df.iloc[:, 0].values
            y = df.iloc[:, 1].values

            return df, x, y  # Successfully read the data

        except Exception as e:
            continue  # Try the next delimiter

    # If all delimiters failed
    error_msg = "Could not detect numeric data with any of the specified delimiters."
    if parent:
        QMessageBox.warning(parent, "Data Read Error", error_msg)
    else:
        print(f"Data Read Error: {error_msg}")
    return None, None, None

def is_numeric_row(row):
    """
    Determines if a row contains at least two numeric values.
    """
    numeric_count = sum(1 for cell in row if is_float(cell))
    return numeric_count >= max(2, len(row) // 2)

def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
