"""
Dash Web Application for Schema Construction
Interactive web interface using Dash framework to create schemas from SHACL bricks
"""

import sys
import os
from typing import Dict, List, Any

# Add core modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core'))

try:
    import dash
    from dash import dcc, html, Input, Output, State, callback, dash_table
    import plotly.express as px
    import pandas as pd
    DASH_AVAILABLE = True
except ImportError:
    DASH_AVAILABLE = False
    print("Warning: Dash/Plotly not available. Install with: pip install dash plotly pandas")

from schema_core import SchemaCore, Schema
from flow_engine import FlowEngine, FlowType
from brick_integration import BrickIntegration


def create_dash_app(schema_repository_path: str = "schema_repositories",
                   brick_repository_path: str = "brick_repositories"):
    """Create Dash application for schema construction"""
    
    if not DASH_AVAILABLE:
        raise ImportError("Dash not available. Install with: pip install dash plotly pandas")
    
    app = dash.Dash(__name__)
    
    # Initialize core components
    schema_core = SchemaCore(schema_repository_path)
    flow_engine = FlowEngine()
    brick_integration = BrickIntegration(brick_repository_path)
    
    # Get initial data
    bricks = brick_integration.get_available_bricks()
    schemas = schema_core.get_all_schemas()
    
    # Create layout
    app.layout = html.Div([
        html.H1("Schema Construction - DASH Web Interface", 
                 style={'textAlign': 'center', 'marginBottom': 30}),
        
        # Brick Selection Section
        html.Div([
            html.H2("Available Bricks"),
            html.Div(id='brick-selection-container')
        ], style={'marginBottom': 30}),
        
        # Schema Construction Area
        html.Div([
            html.H2("Schema Construction"),
            html.Div([
                html.Div([
                    html.Label("Schema Name:"),
                    dcc.Input(id='schema-name-input', type='text', placeholder='Enter schema name')
                ], style={'marginBottom': 10}),
                
                html.Div([
                    html.Label("Description:"),
                    dcc.Textarea(id='schema-description-input', 
                               placeholder='Enter schema description', rows=3)
                ], style={'marginBottom': 10}),
                
                html.Div([
                    html.Label("Root Brick:"),
                    dcc.Dropdown(
                        id='root-brick-dropdown',
                        options=[
                            {'label': f"{b.name} ({b.object_type})", 'value': b.brick_id}
                            for b in bricks if b.object_type == 'NodeShape'
                        ],
                        placeholder='Select root brick'
                    )
                ], style={'marginBottom': 10}),
                
                html.Button('Create Schema', id='create-schema-btn', 
                          n_clicks=0, style={'marginRight': 10}),
                html.Button('Save Schema', id='save-schema-btn', 
                          n_clicks=0),
                html.Div(id='schema-status', style={'marginTop': 10})
            ])
        ], style={'marginBottom': 30}),
        
        # Current Schemas
        html.Div([
            html.H2("Existing Schemas"),
            html.Div(id='schemas-list-container')
        ]),
        
        # Store data in dcc.Store
        dcc.Store(id='bricks-store', data=[
            {'id': b.brick_id, 'name': b.name, 'type': b.object_type, 
             'description': b.description, 'target_class': b.target_class}
            for b in bricks
        ]),
        dcc.Store(id='schemas-store', data=[
            {'id': s.schema_id, 'name': s.name, 'description': s.description,
             'root_brick': s.root_brick_id, 'components': s.component_brick_ids}
            for s in schemas
        ])
    ])
    
    # Callbacks
    @app.callback(
        Output('brick-selection-container', 'children'),
        Input('bricks-store', 'data')
    )
    def update_brick_selection(bricks_data):
        """Update brick selection display"""
        if not bricks_data:
            return html.P("No bricks available")
        
        # Create brick cards
        node_bricks = [b for b in bricks_data if b['type'] == 'NodeShape']
        prop_bricks = [b for b in bricks_data if b['type'] == 'PropertyShape']
        
        return html.Div([
            html.H3("NodeShape Bricks (Root Bricks)"),
            html.Div([
                html.Div([
                    html.H4(b['name']),
                    html.P(b['description']),
                    html.Small(f"Target: {b['target_class']}")
                ], style={'border': '1px solid #ddd', 'padding': '10px', 
                         'margin': '5px', 'width': '250px'})
                for b in node_bricks
            ], style={'display': 'flex', 'flexWrap': 'wrap'}),
            
            html.H3("PropertyShape Bricks (Components)"),
            html.Div([
                html.Div([
                    html.H4(b['name']),
                    html.P(b['description'])
                ], style={'border': '1px solid #ddd', 'padding': '10px', 
                         'margin': '5px', 'width': '250px'})
                for b in prop_bricks
            ], style={'display': 'flex', 'flexWrap': 'wrap'})
        ])
    
    @app.callback(
        [Output('schema-status', 'children'),
         Output('schemas-store', 'data')],
        [Input('create-schema-btn', 'n_clicks'),
         Input('save-schema-btn', 'n_clicks')],
        [State('schema-name-input', 'value'),
         State('schema-description-input', 'value'),
         State('root-brick-dropdown', 'value'),
         State('schemas-store', 'data')]
    )
    def handle_schema_actions(create_clicks, save_clicks, name, description, 
                         root_brick_id, schemas_data):
        """Handle schema creation and saving"""
        ctx = dash.callback_context
        if not ctx.triggered:
            return "", schemas_data
        
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if button_id == 'create-schema-btn' and create_clicks > 0:
            if not name or not root_brick_id:
                return "❌ Please enter schema name and select root brick", schemas_data
            
            # Create new schema
            try:
                schema = schema_core.create_schema(name, description, root_brick_id)
                new_schema_data = {
                    'id': schema.schema_id, 'name': schema.name, 
                    'description': schema.description, 'root_brick': schema.root_brick_id,
                    'components': schema.component_brick_ids
                }
                return f"✅ Created schema: {name}", schemas_data + [new_schema_data]
            except Exception as e:
                return f"❌ Error creating schema: {e}", schemas_data
        
        elif button_id == 'save-schema-btn' and save_clicks > 0:
            return "💾 Save functionality would save current schema", schemas_data
        
        return "", schemas_data
    
    @app.callback(
        Output('schemas-list-container', 'children'),
        Input('schemas-store', 'data')
    )
    def update_schemas_list(schemas_data):
        """Update existing schemas display"""
        if not schemas_data:
            return html.P("No schemas created yet")
        
        return html.Div([
            html.Div([
                html.H4(s['name']),
                html.P(s['description']),
                html.Small(f"Root: {s['root_brick']} | Components: {len(s['components'])}")
            ], style={'border': '1px solid #ddd', 'padding': '10px', 
                     'margin': '5px', 'backgroundColor': '#f9f9f9'})
            for s in schemas_data
        ])
    
    return app


if __name__ == "__main__":
    if DASH_AVAILABLE:
        app = create_dash_app()
        app.run_server(debug=True, host='0.0.0.0', port=8050)
    else:
        print("Dash not available. Install with: pip install dash plotly pandas")
