# Step 1: Data Loading and Preprocessing
import pandas as pd
import dash
from dash import html, dcc, Input, Output



# Dictionary mapping form types to their checkbox columns
checkbox_columns_dict = {
    "2042K": ["MI (6QR cochez)", "MV (6QW cochez)", "NG (7DQ cochez)", "NH (7DG cochez)", "OK (8FV cochez)", "OL (8TT cochez)", "OM (8UU cochez)", "FR (1AV : cochez)", "GY (1BV : cochez)", "IF (1CV : cochez)", "JD (1DV : cochez)", "LM (2OP cochez)", "LV (4BN cochez)", "LW (4BZ cochez)"],
    "2042KAUTO": ["FS (1AV Cochez)", "FT (1BV Cochez)", "FU (1CV Cochez)", "FV (1DV Cochez)", "KS (2OP Cochez)", "LB (4BN Cochez)", "LC (4BZ Cochez)", "LU (6QR Cochez)", "LV (6QW Cochez)", "MK (7DQ Cochez)", "ML (7DG Cochez)"],
    "2042": ["FR (1AV : cochez)", "GY (1BV : cochez)", "IF (1CV : cochez)", "JD (1DV : cochez)", "LM (2OP cochez)", "LV (4BN cochez)", "LW (4BZ cochez)", "MI (6QR cochez)", "MV (6QW cochez)", "NG (7DQ cochez)", "NH (7DG cochez)", "OK (8FV cochez)", "OL (8TT cochez)", "OM (8UU cochez)"]
}

# Define a color map for match types
color_map = {
    'Empty Match': 'green',
    'Empty No Match': 'red',
    'Full Match': 'green',
    'Almost Match': 'yellow',
    'Contains Match': 'orange',
    'No Match': 'red'
}

def load_data():
    dfs = {}
    forms = ['2042', '2042K', '2042KAUTO']
    engines = ['google', 'trocr', 'tesseract']
    for form in forms:
        for engine in engines:
            file_name = f"results/{form}_{engine}_results_f.csv"  # Adjusted file name format
            dfs[(form, engine)] = pd.read_csv(file_name)
    return dfs

data = load_data()

# Step 2: Dash App Setup
app = dash.Dash(__name__)

# Step 3: Layout Design - Initialize Dropdown Options
app.layout = html.Div([
    dcc.Dropdown(
        id='engine-dropdown',
        options=[{'label': engine, 'value': engine} for engine in ['google', 'trocr']],
        value='google'  # Default value
    ),
    dcc.Dropdown(
        id='form-dropdown',
        options=[{'label': form, 'value': form} for form in ['2042', '2042K', '2042KAUTO']],
        value='2042'  # Default value
    ),
    dcc.Dropdown(
        id='filter-type-dropdown',
        options=[
            {'label': 'All', 'value': 'all'},
            {'label': 'Checkboxes', 'value': 'checkboxes'}
        ],
        value='all',
        clearable=False
    ),
    dcc.Dropdown(
        id='column-dropdown',  # Ensure this ID matches exactly
        options=[],  # Can be empty initially
        clearable=True,
        placeholder="Select a column or leave blank for all"
    ),
    html.Div(id='display-area')
])

# Step 4: Callbacks for Interactivity
@app.callback(
    Output('column-dropdown', 'options'),
    [Input('form-dropdown', 'value'),
     Input('filter-type-dropdown', 'value')] 
)
def set_column_options(selected_form, selected_filter):
    try:
        columns = data[(selected_form, 'google')].columns  # Assuming columns are the same for both engines
        if selected_filter == 'checkboxes':
            # Provide only the checkbox columns for the selected form
            options = [{'label': col, 'value': col} for col in checkbox_columns_dict.get(selected_form, [])]
        else:  # 'all' or individual columns
            # Provide all columns
            options = [{'label': col, 'value': col} for col in columns]

        # Debugging: Print options being returned
        return options
    except Exception as e:
        # Log the exception
        return []  # Return an empty list in case of error

@app.callback(
    Output('display-area', 'children'),
    [Input('engine-dropdown', 'value'),
     Input('form-dropdown', 'value'),
     Input('filter-type-dropdown', 'value'),
     Input('column-dropdown', 'value')]
)
def update_display(selected_engine, selected_form, selected_filter, selected_column):
    df = data[(selected_form, selected_engine)]

    # Calculate the number of processed forms
    total_forms_processed = df.shape[0]

    if selected_filter == 'checkboxes' and not selected_column:
        checkbox_columns = checkbox_columns_dict.get(selected_form, [])
        match_counts = pd.Series(dtype='int')
        for col in checkbox_columns:
            if col in df.columns:
                match_counts = match_counts.add(df[col].value_counts(), fill_value=0)
    elif selected_column:
        match_counts = df[selected_column].value_counts()
    else:
        match_counts = pd.Series(dtype='int')
        for col in df.columns:
            match_counts = match_counts.add(df[col].value_counts(), fill_value=0)

    empty_counts = match_counts.loc[match_counts.index.isin(['Empty Match', 'Empty No Match'])]
    other_counts = match_counts.loc[~match_counts.index.isin(['Empty Match', 'Empty No Match'])]

    empty_colors = [color_map.get(mt, '#000000') for mt in empty_counts.index]
    other_colors = [color_map.get(mt, '#000000') for mt in other_counts.index]

    fig1 = {
        'data': [{
            'values': empty_counts.values,
            'labels': empty_counts.index,
            'type': 'pie',
            'marker': {'colors': empty_colors}
        }],
        'layout': {'title': 'Empty Match vs Empty No Match'}
    }

    fig2 = {
        'data': [{
            'values': other_counts.values,
            'labels': other_counts.index,
            'type': 'pie',
            'marker': {'colors': other_colors}
        }],
        'layout': {'title': 'Other Match Types'}
    }

    # Container for the first two charts
    top_row = html.Div([
        html.Div(dcc.Graph(figure=fig1), style={'display': 'inline-block', 'width': '50%'}),
        html.Div(dcc.Graph(figure=fig2), style={'display': 'inline-block', 'width': '50%'})
    ], style={'display': 'flex'})

    figures = [top_row]

    # Create a new HTML element to display the count of processed forms
    forms_processed_display = html.Div([
        html.H4(f"Total Forms Processed: {total_forms_processed}"),
    ], style={'margin-top': '20px', 'margin-bottom': '20px'})

    # Insert the forms_processed_display at the beginning of the figures list
    figures.insert(0, forms_processed_display)

    try:
        combined_counts = pd.Series(dtype='int')
        no_match_categories = ['Empty No Match', 'No Match']
        match_categories = set(match_counts.index) - set(no_match_categories)
        match_categories_list = list(match_categories)

        combined_counts['No Match'] = match_counts[no_match_categories].sum()
        combined_counts['Match'] = match_counts[match_categories_list].sum()

        combined_colors = ['red' if category == 'No Match' else 'green' for category in combined_counts.index]

        fig_combined = {
            'data': [{
                'values': combined_counts.values,
                'labels': combined_counts.index,
                'type': 'pie',
                'marker': {'colors': combined_colors}
            }],
            'layout': {'title': 'Combined Match Types'}
        }

        figures.append(html.Div(dcc.Graph(figure=fig_combined), style={'width': '100%'}))

    except Exception as e:
        print(f"Error occurred while creating the third chart: {e}")

    return html.Div(figures, style={'display': 'flex', 'flex-direction': 'column'})

# Step 5: Running the App
if __name__ == '__main__':
    app.run_server(port=8080, debug=True)
