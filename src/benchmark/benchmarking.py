import pandas as pd
import Levenshtein as lev

#verite_terrain_path = 'verite_terrain.ods'
#acquisition_google_path = "04122023_1451.ods"

# Function to generate column names like Excel (A, B, ..., Z, AA, AB, ...)
def generate_excel_column_names(n):
    names = []
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        names.append(chr(65 + remainder))
    return ''.join(reversed(names))

def read_sheet(file, sheet_name):
    # Read the sheet with no header to get the label row separately
    df = pd.read_excel(file, sheet_name=sheet_name, header=None)
    
    # Separate label row and data
    label_row = df.iloc[1]  # Second row as labels
    data = df.iloc[2:]  # Data starting from the third row

    # Generate column names and concatenate with label names
    column_names = [generate_excel_column_names(i + 1) + ' (' + str(label) + ')' 
                    for i, label in enumerate(label_row)]

    data.columns = column_names
    return data

# # Read each sheet into a DataFrame
# df_2042K = read_sheet(verite_terrain_path, '2042K')
# df_2042KAUTO = read_sheet(verite_terrain_path, '2042KAUTO')
# df_2042 = read_sheet(verite_terrain_path, '2042')

# # Read each sheet into a DataFrame
# df_2042K_google = read_sheet(acquisition_google_path, '2042K')
# df_2042KAUTO_google = read_sheet(acquisition_google_path, '2042KAUTO')
# df_2042_google = read_sheet(acquisition_google_path, '2042')

import pandas as pd
import unicodedata

def normalize_string(s):
    if pd.isna(s):
        return ''
    s = str(s)
    # Remove accents
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    # Remove special characters and whitespaces, and lowercase
    return s.replace(' ', '').replace('/', '').replace('-', '').lower()

def compare_values(ground_truth, acquisition):
    
    # Apply normalization
    ground_truth = normalize_string(ground_truth)
    acquisition = normalize_string(acquisition)

    # Check for empty match
    if ground_truth == "" and acquisition == "":
        return 'Empty Match'

    # Check for empty no match
    if ground_truth == "" and acquisition != "":
        return 'Empty No Match'

    # Check for full match
    if ground_truth == acquisition:
        return 'Full Match'
    
    # Calculate Levenshtein distance and similarity
    if ground_truth and acquisition:
        similarity = lev.ratio(ground_truth, acquisition)
        if similarity >= 0.7:
            return 'Almost Match'

    # Check if acquisition is contained in ground truth and is at least 5 characters
    if len(acquisition) >= 5 and acquisition in ground_truth:
        return 'Contains Match'

    # Otherwise, it's a no match
    return 'No Match'


def compare_sheets(df_truth, df_google, id_col):
    comparison_rows = []
    for index, google_row in df_google.iterrows():
        identifier = google_row[id_col]
        match = df_truth[df_truth[id_col] == identifier]
        if not match.empty:
            ground_truth_row = match.iloc[0]
            comparison_row = {col: compare_values(google_row[col], ground_truth_row[col])
                              for col in df_google.columns}
        else:
            comparison_row = {col: '#' for col in df_google.columns}
        comparison_rows.append(comparison_row)
    return pd.DataFrame(comparison_rows)

def export_to_csv(df, filename):
    df.to_csv(filename, index=False)

def run_bench(verite_terrain_path, acquisition_google_path):
    # Reading sheets into DataFrames
    df_2042K = read_sheet(verite_terrain_path, '2042K')
    df_2042KAUTO = read_sheet(verite_terrain_path, '2042KAUTO')
    df_2042 = read_sheet(verite_terrain_path, '2042')
    df_2042K_google = read_sheet(acquisition_google_path, '2042K')
    df_2042KAUTO_google = read_sheet(acquisition_google_path, '2042KAUTO')
    df_2042_google = read_sheet(acquisition_google_path, '2042')

    # Comparing sheets and generating results
    df_2042K_google_results = compare_sheets(df_2042K, df_2042K_google, 'C (SPI 1)')
    df_2042KAUTO_google_results = compare_sheets(df_2042KAUTO, df_2042KAUTO_google, 'C (SPI 1)')
    df_2042_google_results = compare_sheets(df_2042, df_2042_google, 'D (N° SPI 1)')

    # Filtering and exporting results
    df_2042K_google_results = df_2042K_google_results[df_2042K_google_results.iloc[:, 0] != '#']
    export_to_csv(df_2042K_google_results, 'results/2042K_google_results_f.csv')
    export_to_csv(df_2042KAUTO_google_results, 'results/2042KAUTO_google_results_f.csv')
    export_to_csv(df_2042_google_results, 'results/2042_google_results_f.csv')

    export_to_csv(df_2042K_google_results, 'results/2042K_trocr_results_f.csv')
    export_to_csv(df_2042_google_results, 'results/2042KAUTO_trocr_results_f.csv')
    export_to_csv(df_2042_google_results, 'results/2042_trocr_results_f.csv')

# Example usage
#main('verite_terrain.ods', '04122023_1451.ods')