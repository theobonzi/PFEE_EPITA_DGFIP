# Step 1: Data Loading and Preprocessing
import pandas as pd
import dash
from dash import html, dcc, Input, Output



# Dictionary mapping form types to their checkbox columns
checkbox_columns_dict = {
    "2042K": ["MI (6QR cochez)", "MV (6QW cochez)", "NG (7DQ cochez)", "NH (7DG cochez)", "OK (8FV cochez)", "OL (8TT cochez)", "OM (8UU cochez)", "FR (1AV : cochez)", "GY (1BV : cochez)", "IF (1CV : cochez)", "JD (1DV : cochez)", "LM (2OP cochez)", "LV (4BN cochez)", "LW (4BZ cochez)"],
    "2042KAUTO": ["FS", "FT", "FU", "FV", "KS", "LB", "LC", "LU", "LV", "MK", "ML"],
    "2042": ["FH", "FI", "FJ", "FK", "IQ", "IZ", "JA", "JP", "JQ", "KD", "KE", "LE", "LF", "LG"]
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
    engines = ['google', 'tesseract']
    for form in forms:
        for engine in engines:
            file_name = f"{form}_{engine}_results_f.csv"  # Adjusted file name format
            dfs[(form, engine)] = pd.read_csv(file_name)
    return dfs

data = load_data()

# Step 2: Dash App Setup
app = dash.Dash(__name__)

# Step 3: Layout Design - Initialize Dropdown Options
app.layout = html.Div([
    dcc.Dropdown(
        id='engine-dropdown',
        options=[{'label': engine, 'value': engine} for engine in ['google', 'tesseract']],
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
     Input('filter-type-dropdown', 'value'),  # Added this input
     Input('column-dropdown', 'value')]
)
def update_display(selected_engine, selected_form, selected_filter, selected_column):
    df = data[(selected_form, selected_engine)]

    # Check if 'Checkboxes' is selected and no specific column is chosen
    if selected_filter == 'checkboxes' and not selected_column:
        checkbox_columns = checkbox_columns_dict.get(selected_form, [])
        match_counts = pd.Series(dtype='int')
        for col in checkbox_columns:
            if col in df.columns:
                match_counts = match_counts.add(df[col].value_counts(), fill_value=0)
    elif selected_column:
        match_counts = df[selected_column].value_counts()
    else:
        # Handle different columns across forms for aggregation
        match_counts = pd.Series(dtype='int')
        for col in df.columns:
            match_counts = match_counts.add(df[col].value_counts(), fill_value=0)

    # Separating "Empty Match" and "Empty No Match" from the rest
    empty_counts = match_counts.loc[match_counts.index.isin(['Empty Match', 'Empty No Match'])]
    other_counts = match_counts.loc[~match_counts.index.isin(['Empty Match', 'Empty No Match'])]

    # Apply colors
    empty_colors = [color_map.get(mt, '#000000') for mt in empty_counts.index]  # Default to black if not found
    other_colors = [color_map.get(mt, '#000000') for mt in other_counts.index]

    # Create two pie charts with specified colors
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
    return html.Div([
        html.Div(dcc.Graph(figure=fig1), style={'display': 'inline-block', 'width': '50%'}),
        html.Div(dcc.Graph(figure=fig2), style={'display': 'inline-block', 'width': '50%'})
    ], style={'display': 'flex', 'flex-direction': 'row'})




# Step 5: Running the App
if __name__ == '__main__':
    app.run_server(debug=True)
