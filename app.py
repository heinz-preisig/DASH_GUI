from dash import Dash, html, dcc, callback, Input, Output
import plotly.express as px
import pandas as pd

app = Dash(__name__)

app.layout = html.Div([
    html.H1(children='My First Dash GUI', style={'textAlign': 'center'}),
    dcc.Dropdown(['NYC', 'MTL', 'SF'], 'NYC', id='dropdown-selection'),
    dcc.Graph(id='graph-content')
])

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    # Sample data logic
    df = pd.DataFrame({'x': [1, 2, 3], 'y': [1, 2, 3]})
    return px.line(df, x='x', y='y', title=f'Data for {value}')

if __name__ == '__main__':
    app.run(debug=True)
