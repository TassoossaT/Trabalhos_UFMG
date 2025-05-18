# import pandas as pd
import geopandas as gpd
import dash_leaflet as dl
# import dash_leaflet.express as dlx
from dash import Dash, html, dcc, Output, Input, dash_table, State, callback
from dash_extensions.javascript import assign
import json
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from shapely.geometry import Point
from matplotlib.colors import PowerNorm
from shapely import wkt  # added import
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate

# Custom CSS for the dashboard
external_stylesheets = [
    'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css'
]

class Create_Map:
    def __init__(self, urljson: str):
        with open(urljson, encoding="utf-8") as f:
            self.data = gpd.GeoDataFrame(json.load(f))
        if "GEOMETRIA" in self.data.columns:
            geometry = self.data["GEOMETRIA"].apply(wkt.loads)
            self.data = gpd.GeoDataFrame(self.data, geometry=geometry)
        elif "longitude" in self.data.columns and "latitude" in self.data.columns:
            geometry = self.data.apply(lambda row: Point(row["longitude"], row["latitude"]), axis=1)
            self.data = gpd.GeoDataFrame(self.data, geometry=geometry)
        else:
            raise AttributeError("No geometry data found. Provide 'GEOMETRIA' or 'longitude' and 'latitude' columns.")
        bounds = self.data.total_bounds
        self.center = [(bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2]
        self.bounds = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]
        
        # Extract neighborhood centroids for level 1 flows (demand → PHC)
        self.neighborhood_coords = {}
        for idx, row in self.data.iterrows():
            if 'NOME' in row and hasattr(row.geometry, 'centroid'):
                centroid = row.geometry.centroid
                self.neighborhood_coords[row['NOME']] = {
                    'latitude': centroid.y,
                    'longitude': centroid.x
                }
        
        self.facilities_data = []
        self.team_data = {}  # Store team information
        self.load_facilities_data()
        
        self.App()
    
    def load_facilities_data(self):
        for level in ["1", "2", "3"]:
            try:
                with open(f"P.O Saude/dados_json/EL_{level}.json", 'r', encoding='utf-8') as f:
                    markers_data = json.load(f)
                for m in markers_data:
                    m["level"] = level
                    m["type"] = "Existente"
                    m["level_name"] = {
                        "1": "Primário (PHC)",
                        "2": "Secundário (SHC)", 
                        "3": "Terciário (THC)"
                    }.get(level, "Desconhecido")
                    self.facilities_data.append(m)
            except Exception as e:
                print(f"Error loading EL_{level}.json: {e}")
        
        try:
            with open("P.O Saude/Resultado/new_locations.json", encoding="utf-8") as f:
                saved_names = json.load(f)
        except:
            try:
                with open("new_locations.json", encoding="utf-8") as f:
                    saved_names = json.load(f)
            except:
                saved_names = {}
        
        marker_level_map = {"1": "4", "2": "5", "3": "6"}
        for level_key, names in saved_names.items():
            if names:
                try:
                    coord_file = f"P.O Saude/dados_json/novas_unidades_nivel_{level_key}.json"
                    with open(coord_file, encoding='utf-8') as f:
                        coord_markers = json.load(f)
                    for m in [m for m in coord_markers if m["name"] in names]:
                        m["level"] = marker_level_map.get(level_key, level_key)
                        m["original_level"] = level_key
                        m["type"] = "Nova"
                        m["level_name"] = {
                            "1": "Primário (PHC)",
                            "2": "Secundário (SHC)", 
                            "3": "Terciário (THC)"
                        }.get(level_key, "Desconhecido")
                        self.facilities_data.append(m)
                except Exception as e:
                    print(f"Error loading new facilities for level {level_key}: {e}")
        
        try:
            with open("P.O Saude/Resultado/flow_results.json", encoding="utf-8") as f:
                result_data = json.load(f)
                self.costs_data = result_data.get("costs", {})
                self.facility_usage = result_data.get("facility_usage", {})
                self.flows = result_data.get("flows", {})
                self.team_info = result_data.get("team_info", {})
                
                # Extract team data per facility if available
                if "team_variations" in result_data:
                    self.team_data = result_data.get("team_variations", {})
                    print(f"Team variations loaded successfully. Found {len(self.team_data.get('phc', {}))} PHC entries")
                else:
                    # Create placeholder for team data - in a real scenario this would come from the model
                    self.team_data = {
                        "phc": {},
                        "shc": {},
                        "thc": {}
                    }
                    
                    # Add some team variation data based on existing information
                    for facility_type in ["phc", "shc", "thc"]:
                        if facility_type in self.facility_usage:
                            for facility_name, usage_data in self.facility_usage[facility_type].items():
                                if isinstance(usage_data, dict) and "usage" in usage_data:
                                    # Create sample team variation data
                                    self.team_data[facility_type][facility_name] = {
                                        "original_team": {"medico": 2, "enfermeiro": 3, "tecnico": 5},
                                        "additional_team": {"medico": 1, "enfermeiro": 1, "tecnico": 2},
                                        "total_team": {"medico": 3, "enfermeiro": 4, "tecnico": 7}
                                    }
                
                # First process usage data
                for facility in self.facilities_data:
                    level_key = facility.get("original_level", facility.get("level"))
                    facility_type = {"1": "phc", "2": "shc", "3": "thc"}.get(level_key, "phc")
                    
                    if facility_type in self.facility_usage:
                        usage_data = self.facility_usage[facility_type].get(facility["name"], {})
                        facility["capacity"] = usage_data.get("capacity", "N/A")
                        facility["usage"] = usage_data.get("usage", "N/A")
                        facility["usage_pct"] = usage_data.get("usage_percentage", "N/A")
                
                # Then in a separate step, process team data
                for facility in self.facilities_data:
                    level_key = facility.get("original_level", facility.get("level"))
                    facility_type = {"1": "phc", "2": "shc", "3": "thc"}.get(level_key, "phc")
                    
                    # Add team information to facility if available
                    if facility_type in self.team_data and facility["name"] in self.team_data[facility_type]:
                        facility["team_data"] = self.team_data[facility_type][facility["name"]]
        except Exception as e:
            print(f"Error loading data: {e}")
            self.costs_data = {}
            self.facility_usage = {}
            self.flows = {}
            self.team_data = {}
        
        # Fix the sanitization step to preserve team_data as a dictionary
        for facility in self.facilities_data:
            # Convert other nested objects to strings, but preserve team_data
            sanitized_fields = {}
            for key, value in facility.items():
                if key == "team_data":
                    # Keep team_data as is
                    sanitized_fields[key] = value
                elif isinstance(value, dict):
                    # Convert other dictionaries to strings
                    sanitized_fields[key] = str(value)
                else:
                    # Keep other values as is
                    sanitized_fields[key] = value
            
            # Update the facility with sanitized fields
            facility.clear()
            facility.update(sanitized_fields)
    
    def Color(self):
        min = self.data['QTDPESSOAS'].min()
        max = self.data['QTDPESSOAS'].max()
        norm = PowerNorm(gamma=0.1, vmin=min, vmax=max)
        color = lambda cor: mcolors.to_hex(plt.get_cmap('Blues')(norm(cor)))
        self.data['color'] = self.data['QTDPESSOAS'].apply(lambda x: color(x))
    
    def GeoJSON(self):
        self.Color()
        style_handle = assign("""
            function(feature, context) {
                return {
                    weight: 2,
                    opacity: 0,        
                    color: 'white',
                    dashArray: '1',
                    fillOpacity: 0,     
                    fillColor: feature.properties['color']
                };
            }
        """)
        return dl.GeoJSON(
            data=json.loads(self.data.to_json()),
            style=style_handle,
            zoomToBounds=True,
            zoomToBoundsOnClick=True,
            hoverStyle={"weight": 1, "color": '#666', "dashArray": ''},
            id="geojson"
        )
    
    def Info(self,feature=None):
        def get_info(feature=None):
            header = [html.H4("População por Bairro", style={'color': '#2c3e50', 'marginBottom': '8px'})]
            if not feature:
                return header + [html.P("Passe o mouse sobre um bairro", style={'fontSize': '14px'})]
            bairro = feature["properties"]["NOME"]
            qtd_pessoas = feature["properties"]["QTDPESSOAS"]
            return header + [
                html.B(bairro, style={'fontSize': '16px', 'color': '#2c3e50'}), 
                html.Br(), 
                html.Span(f"{qtd_pessoas:,} pessoas", style={'fontSize': '14px'})
            ]
        
        return html.Div(children=get_info(feature), id="info", className="info",
                         style={
                            "position": "absolute", 
                            "top": "10px", 
                            "right": "10px", 
                            "zIndex": "1000",
                            "backgroundColor": "white",
                            "padding": "10px",
                            "borderRadius": "8px",
                            "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
                            "minWidth": "200px"
                        })
    
    def App(self):
        app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=external_stylesheets)
        
        colors = {
            'primary': '#3498db',
            'secondary': '#2ecc71',
            'accent': '#9b59b6',
            'warning': '#e67e22',
            'danger': '#e74c3c',
            'light': '#f8f9fa',
            'dark': '#2c3e50',
            'white': '#ffffff',
            'background': '#f8f9fa'
        }
        
        # Sanitize the facilities dataframe to prevent object children issues
        facilities_list = []
        for facility in self.facilities_data:
            clean_facility = {}
            for key, value in facility.items():
                # Convert any non-primitive types to strings
                if isinstance(value, (str, int, float, bool)) or value is None:
                    clean_facility[key] = value
                else:
                    clean_facility[key] = str(value)
            facilities_list.append(clean_facility)
        
        facilities_df = pd.DataFrame(facilities_list)
        
        # Generate tooltip data properly before layout definition
        tooltip_data = []
        for row in facilities_df.to_dict('records'):
            row_tooltips = {}
            for column, value in row.items():
                # Make sure we only use strings in tooltips
                row_tooltips[column] = {'value': str(value) if value is not None else '', 'type': 'markdown'}
            tooltip_data.append(row_tooltips)
        
        app.layout = html.Div([
            html.Div([
                html.Div([
                    html.H1("Sistema de Saúde de Belo Horizonte", className="header-title"),
                    html.P("Visualização de Unidades de Saúde e Análise de Dados", className="header-subtitle")
                ], className="header-content")
            ], className="dashboard-header"),
            
            html.Div([
                dcc.Tabs(id="app-tabs", value='map-tab', className="custom-tabs", children=[
                    dcc.Tab(label='Mapa Interativo', value='map-tab', className='custom-tab', selected_className='custom-tab--selected', children=[
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.H3("Filtros", className="filter-heading"),
                                    
                                    html.Div([
                                        html.Label("Níveis de Atendimento:", className="filter-label"),
                                        dcc.Checklist(
                                            id='level-filter',
                                            options=[
                                                {'label': 'Primário (PHC)', 'value': '1'},
                                                {'label': 'Secundário (SHC)', 'value': '2'},
                                                {'label': 'Terciário (THC)', 'value': '3'},
                                            ],
                                            value=['1', '2', '3'],
                                            className="custom-checklist",
                                            inputClassName="custom-checkbox",
                                            labelClassName="custom-checkbox-label"
                                        ),
                                    ], className="filter-group"),
                                    
                                    html.Div([
                                        html.Label("Tipo de Unidade:", className="filter-label"),
                                        dcc.Checklist(
                                            id='type-filter',
                                            options=[
                                                {'label': 'Existentes', 'value': 'Existente'},
                                                {'label': 'Novas', 'value': 'Nova'},
                                            ],
                                            value=['Existente', 'Nova'],
                                            className="custom-checklist",
                                            inputClassName="custom-checkbox",
                                            labelClassName="custom-checkbox-label"
                                        ),
                                    ], className="filter-group"),
                                    
                                    html.Div([
                                        html.Label("Visualização:", className="filter-label"),
                                        dcc.Checklist(
                                            id='show-flows',
                                            options=[{'label': 'Exibir Fluxos', 'value': 'show'}],
                                            value=['show'],
                                            className="custom-checklist",
                                            inputClassName="custom-checkbox",
                                            labelClassName="custom-checkbox-label"
                                        ),
                                    ], className="filter-group"),
                                    
                                    html.Div([
                                        html.Button('Aplicar Filtros', id='apply-filters-btn', className="apply-btn"),
                                        html.Button('Redefinir', id='reset-filters-btn', className="reset-btn"),
                                    ], className="filter-actions")
                                ], className="filter-card")
                            ], className="filter-sidebar"),
                            
                            html.Div([
                                html.Div([
                                    dl.Map(
                                        id='map-display',
                                        children=[
                                            dl.TileLayer(url='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', 
                                                         attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'),
                                            self.GeoJSON(),
                                            self.Info(),
                                            dl.Pane(id="flowPane", name="flowPane", style={"zIndex": 610}),
                                            dl.LayerGroup(id='markers-layer'),
                                            dl.LayerGroup(id='flows-layer'),
                                        ], 
                                        center=self.center,
                                        minZoom=11.4,
                                        bounds=self.bounds,
                                        maxBounds=self.bounds,
                                        maxBoundsViscosity=0.1,
                                        worldCopyJump=False,
                                        style={'width': '100%', 'height': '70vh', 'borderRadius': '8px'}
                                    ),
                                    html.Div([
                                        html.Div([
                                            html.Span("🟢", className="legend-dot"),
                                            html.Span("Primário (Existente)", className="legend-label")
                                        ], className="legend-item"),
                                        html.Div([
                                            html.Span("🟡", className="legend-dot"),
                                            html.Span("Secundário (Existente)", className="legend-label")
                                        ], className="legend-item"),
                                        html.Div([
                                            html.Span("🔴", className="legend-dot"),
                                            html.Span("Terciário (Existente)", className="legend-label")
                                        ], className="legend-item"),
                                        html.Div([
                                            html.Span("🟠", className="legend-dot"),
                                            html.Span("Primário (Novo)", className="legend-label")
                                        ], className="legend-item"),
                                        html.Div([
                                            html.Span("🟣", className="legend-dot"),
                                            html.Span("Secundário (Novo)", className="legend-label")
                                        ], className="legend-item"),
                                        html.Div([
                                            html.Span("⚫", className="legend-dot"),
                                            html.Span("Terciário (Novo)", className="legend-label")
                                        ], className="legend-item")
                                    ], className="map-legend")
                                ], className="map-container")
                            ], className="map-wrapper")
                        ], className="map-tab-content")
                    ]),
                    
                    dcc.Tab(label='Painel de Estatísticas', value='summary-tab', className='custom-tab', selected_className='custom-tab--selected', children=[
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.Div(id='stat-card-total', className="stat-card"),
                                    html.Div(id='stat-card-existing', className="stat-card"),
                                    html.Div(id='stat-card-new', className="stat-card"),
                                ], className="stat-cards-row"),
                                
                                html.Div([
                                    html.Div(id='stat-card-total-cost', className="stat-card"),
                                    html.Div(id='stat-card-hospital-cost', className="stat-card"),
                                    html.Div(id='stat-card-logistic-cost', className="stat-card"),
                                ], className="stat-cards-row"),
                            ], className="stats-container"),
                            
                            html.Div([
                                html.Div([
                                    html.Div([
                                        html.H4("Distribuição de Custos", className="chart-title"),
                                        dcc.Graph(id='cost-pie-chart', className="chart-content",
                                                 config={'displayModeBar': False})
                                    ], className="chart-card"),
                                    
                                    html.Div([
                                        html.H4("Distribuição de Unidades", className="chart-title"),
                                        dcc.Graph(id='facilities-distribution', className="chart-content",
                                                 config={'displayModeBar': False})
                                    ], className="chart-card")
                                ], className="charts-row"),
                                
                                html.Div([
                                    html.Div([
                                        html.H4("Utilização por Nível", className="chart-title"),
                                        dcc.Graph(id='usage-bar-chart', className="chart-content", 
                                                 config={'displayModeBar': False})
                                    ], className="chart-card full-width")
                                ], className="charts-row"),
                            ], className="charts-container")
                        ], className="summary-tab-content")
                    ]),
                    
                    dcc.Tab(label='Lista de Unidades', value='facilities-tab', className='custom-tab', selected_className='custom-tab--selected', children=[
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.Div([
                                        html.Label("Busca:", className="search-label"),
                                        html.Div([
                                            html.I(className="fas fa-search search-icon"),
                                            dcc.Input(
                                                id='facility-search',
                                                type='text',
                                                placeholder='Nome da unidade...',
                                                className="search-input"
                                            )
                                        ], className="search-input-container")
                                    ], className="search-group")
                                ], className="table-filter-col"),
                                
                                html.Div([
                                    html.Label("Nível de Atendimento:", className="filter-dropdown-label"),
                                    dcc.Dropdown(
                                        id='facility-level-filter',
                                        options=[
                                            {'label': 'Todos os Níveis', 'value': 'all'},
                                            {'label': 'Primário (PHC)', 'value': '1'},
                                            {'label': 'Secundário (SHC)', 'value': '2'},
                                            {'label': 'Terciário (THC)', 'value': '3'},
                                        ],
                                        value='all',
                                        clearable=False,
                                        className="filter-dropdown"
                                    )
                                ], className="table-filter-col"),
                                
                                html.Div([
                                    html.Label("Tipo de Unidade:", className="filter-dropdown-label"),
                                    dcc.Dropdown(
                                        id='facility-type-filter',
                                        options=[
                                            {'label': 'Todos os Tipos', 'value': 'all'},
                                            {'label': 'Unidades Existentes', 'value': 'Existente'},
                                            {'label': 'Novas Unidades', 'value': 'Nova'},
                                        ],
                                        value='all',
                                        clearable=False,
                                        className="filter-dropdown"
                                    )
                                ], className="table-filter-col"),
                            ], className="table-filters"),
                            
                            html.Div([
                                dash_table.DataTable(
                                    id='facilities-table',
                                    columns=[
                                        {'name': 'Nome', 'id': 'name'}, 
                                        {'name': 'Nível', 'id': 'level_name'}, 
                                        {'name': 'Tipo', 'id': 'type'},
                                        {'name': 'Capacidade', 'id': 'capacity', 'type': 'numeric', 'format': {'specifier': '.2f'}},
                                        {'name': 'Uso', 'id': 'usage', 'type': 'numeric', 'format': {'specifier': '.2f'}},
                                        {'name': '% de Uso', 'id': 'usage_pct', 'type': 'numeric', 'format': {'specifier': '.2f'}},
                                        {'name': 'Latitude', 'id': 'latitude', 'type': 'numeric', 'format': {'specifier': '.6f'}},
                                        {'name': 'Longitude', 'id': 'longitude', 'type': 'numeric', 'format': {'specifier': '.6f'}}
                                    ],
                                    data=facilities_df.to_dict('records'),
                                    filter_action='native',
                                    sort_action='native',
                                    sort_mode='multi',
                                    page_size=15,
                                    style_cell={
                                        'textAlign': 'left',
                                        'padding': '12px 15px',
                                        'fontFamily': 'Roboto, sans-serif',
                                        'fontSize': '14px',
                                        'overflow': 'hidden',
                                        'textOverflow': 'ellipsis',
                                        'maxWidth': 0
                                    },
                                    style_header={
                                        'backgroundColor': colors['primary'],
                                        'color': colors['white'],
                                        'fontWeight': 'bold',
                                        'fontSize': '15px',
                                        'padding': '15px 16px',
                                        'borderTop': f'1px solid {colors["primary"]}'
                                    },
                                    style_data={
                                        'backgroundColor': colors['white'],
                                        'border': f'1px solid {colors["light"]}'
                                    },
                                    style_data_conditional=[
                                        {
                                            'if': {'row_index': 'odd'},
                                            'backgroundColor': 'rgba(52, 152, 219, 0.05)'
                                        },
                                        {
                                            'if': {'column_id': 'usage_pct', 'filter_query': '{usage_pct} > 0.9'},
                                            'backgroundColor': 'rgba(231, 76, 60, 0.2)',
                                            'fontWeight': 'bold'
                                        },
                                        {
                                            'if': {'column_id': 'usage_pct', 'filter_query': '{usage_pct} > 0.7 && {usage_pct} <= 0.9'},
                                            'backgroundColor': 'rgba(230, 126, 34, 0.2)'
                                        },
                                        {
                                            'if': {'column_id': 'type', 'filter_query': '{type} eq "Nova"'},
                                            'color': colors['accent'],
                                            'fontWeight': 'bold'
                                        }
                                    ],
                                    tooltip_data=tooltip_data,
                                    tooltip_duration=None,
                                    style_as_list_view=True,
                                ),
                                html.Div(id="table-pagination-info", className="pagination-info"),
                            ], className="table-container")
                        ], className="facilities-tab-content")
                    ])
                ])
            ], className="content-container"),
            
            html.Div([
                html.P("Sistema de Visualização de Unidades de Saúde", className="footer-text"),
                html.P("© 2023 UFMG", className="footer-copyright")
            ], className="dashboard-footer"),
            
            # Add team detail modal
            html.Div([
                html.Div([
                    html.Div([
                        html.H3(id="team-modal-title", className="modal-title"),
                        html.Button("×", id="close-team-modal", className="close-button")
                    ], className="modal-header"),
                    html.Div(id="team-modal-content", className="modal-body"),
                ], className="modal-content")
            ], id="team-detail-modal", className="modal", style={'display': 'none'}),
            
            dcc.Store(id='filtered-facilities-data'),
            dcc.Store(id='summary-data'),
            dcc.Store(id='active-tab', data='map-tab'),
            dcc.Store(id='selected-facility-data'),
            
        ], className="dashboard-container")
        
        self.app = app
        self.register_callbacks()

    def register_callbacks(self):
        @self.app.callback(Output("info", "children"), Input("geojson", "hoverData"))
        def info_hover(feature):
            return self.Info(feature).children
        
        # Fix the callback to show team data when a facility is clicked
        @self.app.callback(
            [Output('team-detail-modal', 'style'),
             Output('team-modal-title', 'children'),
             Output('team-modal-content', 'children')],
            [Input('markers-layer', 'click_marker'),
             Input({'type': 'team-detail-btn', 'index': dash.dependencies.ALL}, 'n_clicks')],
            [State('markers-layer', 'click_marker')]
        )
        def show_team_details(marker_click, btn_clicks, marker_state):
            ctx = dash.callback_context
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else ""
            
            # Check if triggered by a button click
            if "team-detail-btn" in trigger_id:
                # Extract facility name from the button ID
                try:
                    facility_name = json.loads(trigger_id)['index']
                except:
                    return {'display': 'none'}, "", []
            elif marker_click:
                # Get name from marker click
                facility_name = marker_click.get('popup', '')
            else:
                return {'display': 'none'}, "", []
            
            if not facility_name:
                return {'display': 'none'}, "", []
            
            # Find facility data
            facility = None
            for f in self.facilities_data:
                if str(f.get('name', '')) == facility_name:
                    facility = f
                    break
            
            if not facility:
                return {'display': 'none'}, "", []
            
            # Get team data
            team_data = facility.get('team_data')
            
            # If no team data, show appropriate message
            if not team_data:
                return {'display': 'block'}, f"Informações de Equipe - {facility_name}", [
                    html.Div("Não há dados de equipe disponíveis para esta unidade.", 
                             className="no-data-message")
                ]
            
            # Create team variation content
            modal_title = f"Variações de Equipe - {facility_name}"
            
            original_team = team_data.get("original_team", {})
            additional_team = team_data.get("additional_team", {})
            total_team = team_data.get("total_team", {})
            
            # Create visualization with comparative bars
            team_viz = []
            for role in set(list(original_team.keys()) + list(additional_team.keys()) + list(total_team.keys())):
                orig_val = original_team.get(role, 0)
                add_val = additional_team.get(role, 0)
                total_val = total_team.get(role, 0)
                
                # Skip if all zeros
                if orig_val == 0 and add_val == 0 and total_val == 0:
                    continue
                    
                # Calculate percentages for bar widths
                max_val = max(orig_val, add_val, total_val, 1)  # Avoid divide by zero
                orig_pct = (orig_val / max_val) * 100
                add_pct = (add_val / max_val) * 100
                total_pct = (total_val / max_val) * 100
                
                team_viz.append(html.Div([
                    html.Div([
                        html.Strong(f"{role.capitalize()}: ", style={'width': '100px', 'display': 'inline-block'}),
                        html.Div([
                            html.Div(style={
                                'backgroundColor': '#2ecc71',
                                'width': f'{orig_pct}%',
                                'height': '15px',
                                'display': 'inline-block',
                                'position': 'relative'
                            }),
                            html.Span(f"{orig_val:.1f}", style={
                                'position': 'absolute',
                                'right': '-30px',
                                'top': '-2px',
                                'fontSize': '12px'
                            })
                        ], style={'position': 'relative', 'margin': '5px 0', 'width': '80%', 'display': 'inline-block'}),
                    ], style={'display': 'flex', 'alignItems': 'center'}),
                    
                    html.Div([
                        html.Strong("Adicional: ", style={'width': '100px', 'display': 'inline-block', 'color': '#e74c3c'}),
                        html.Div([
                            html.Div(style={
                                'backgroundColor': '#e74c3c',
                                'width': f'{add_pct}%',
                                'height': '15px',
                                'display': 'inline-block',
                                'position': 'relative'
                            }),
                            html.Span(f"{add_val:.1f}", style={
                                'position': 'absolute',
                                'right': '-30px',
                                'top': '-2px',
                                'fontSize': '12px'
                            })
                        ], style={'position': 'relative', 'margin': '5px 0', 'width': '80%', 'display': 'inline-block'}),
                    ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '15px'}),
                ], style={'marginBottom': '20px'}))
            
            content = html.Div([
                html.Div([
                    html.H4("Resumo da Equipe", style={'marginBottom': '15px', 'color': '#2c3e50'}),
                    html.Div([
                        html.Div([
                            html.Strong("Profissionais Originais:"),
                            html.Span(f" {sum(original_team.values()):.1f}", style={'fontSize': '18px', 'color': '#2ecc71'})
                        ], style={'flex': '1', 'textAlign': 'center', 'padding': '10px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px'}),
                        html.Div([
                            html.Strong("Adicionais:"),
                            html.Span(f" {sum(additional_team.values()):.1f}", style={'fontSize': '18px', 'color': '#e74c3c'})
                        ], style={'flex': '1', 'textAlign': 'center', 'padding': '10px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px', 'margin': '0 10px'}),
                        html.Div([
                            html.Strong("Total:"),
                            html.Span(f" {sum(total_team.values()):.1f}", style={'fontSize': '18px', 'color': '#3498db'})
                        ], style={'flex': '1', 'textAlign': 'center', 'padding': '10px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px'})
                    ], style={'display': 'flex', 'marginBottom': '20px'})
                ], className="team-summary-section"),
                
                html.Hr(style={'margin': '20px 0'}),
                
                html.Div([
                    html.H4("Detalhamento por Cargo", style={'marginBottom': '15px', 'color': '#2c3e50'}),
                    html.Div(team_viz, className="team-visualization")
                ], className="team-detail-section"),
                
                html.Hr(style={'margin': '20px 0'}),
                
                html.Div([
                    html.H4("Informações de Utilização", style={'marginBottom': '15px', 'color': '#2c3e50'}),
                    html.Div([
                        html.Div([
                            html.P([
                                html.Strong("Capacidade: "), 
                                f"{facility.get('capacity', 'N/A'):.1f}" if isinstance(facility.get('capacity'), (int, float)) 
                                else facility.get('capacity', 'N/A')
                            ]),
                            html.P([
                                html.Strong("Uso: "), 
                                f"{facility.get('usage', 'N/A'):.1f}" if isinstance(facility.get('usage'), (int, float))
                                else facility.get('usage', 'N/A')
                            ]),
                        ], style={'flex': '1'}),
                        html.Div([
                            html.P([
                                html.Strong("Utilização: "), 
                                f"{facility.get('usage_pct', 'N/A'):.1f}%" if isinstance(facility.get('usage_pct'), (int, float))
                                else f"{facility.get('usage_pct', 'N/A')}%"
                            ]),
                            # Add a progress bar for utilization
                            html.Div([
                                html.Div(style={
                                    'width': f"{min(100, float(facility.get('usage_pct', 0))):.1f}%" if isinstance(facility.get('usage_pct'), (int, float)) else "0%",
                                    'backgroundColor': '#3498db',
                                    'height': '100%',
                                    'borderRadius': '3px'
                                })
                            ], style={
                                'width': '100%',
                                'backgroundColor': '#ecf0f1',
                                'height': '15px',
                                'borderRadius': '3px',
                                'marginTop': '5px'
                            })
                        ], style={'flex': '1'})
                    ], style={'display': 'flex', 'gap': '20px'})
                ], className="usage-section")
            ])
            
            return {'display': 'block'}, modal_title, content
        
        # Close the modal when clicking the close button
        @self.app.callback(
            Output('team-detail-modal', 'style', allow_duplicate=True),
            [Input('close-team-modal', 'n_clicks')],
            prevent_initial_call=True
        )
        def close_modal(n_clicks):
            if n_clicks:
                return {'display': 'none'}
            raise PreventUpdate
        
        # Update statistics tab with team information
        @self.app.callback(
            [Output('stat-card-total', 'children'),
             Output('stat-card-existing', 'children'),
             Output('stat-card-new', 'children'),
             Output('stat-card-total-cost', 'children'),
             Output('stat-card-hospital-cost', 'children'),
             Output('stat-card-logistic-cost', 'children'),
             Output('cost-pie-chart', 'figure'),
             Output('facilities-distribution', 'figure'),
             Output('usage-bar-chart', 'figure')],
            [Input('app-tabs', 'value')]
        )
        def update_statistics(tab):
            # Only update if we're on the statistics tab (for performance)
            if tab != 'summary-tab':
                raise PreventUpdate
                
            # Calculate facility statistics
            total_facilities = len(self.facilities_data)
            existing_facilities = sum(1 for f in self.facilities_data if f.get('type') == 'Existente')
            new_facilities = total_facilities - existing_facilities
            
            # Create stat cards
            total_card = html.Div([
                html.Div([
                    html.I(className="fas fa-hospital fa-2x", style={'color': '#3498db'}),
                    html.H3("Total de Unidades", className="stat-title")
                ], className="stat-header"),
                html.Div([
                    html.Span(f"{total_facilities}", className="stat-value"),
                    html.Span("Unidades", className="stat-label")
                ], className="stat-body")
            ])
            
            existing_card = html.Div([
                html.Div([
                    html.I(className="fas fa-clinic-medical fa-2x", style={'color': '#2ecc71'}),
                    html.H3("Unidades Existentes", className="stat-title")
                ], className="stat-header"),
                html.Div([
                    html.Span(f"{existing_facilities}", className="stat-value"),
                    html.Span("Unidades", className="stat-label")
                ], className="stat-body")
            ])
            
            new_card = html.Div([
                html.Div([
                    html.I(className="fas fa-plus-circle fa-2x", style={'color': '#9b59b6'}),
                    html.H3("Novas Unidades", className="stat-title")
                ], className="stat-header"),
                html.Div([
                    html.Span(f"{new_facilities}", className="stat-value"),
                    html.Span("Unidades", className="stat-label")
                ], className="stat-body")
            ])
            
            # Cost statistics
            total_cost = self.costs_data.get('total_cost', 0)
            
            # Get facility construction and fixed costs correctly
            fixed_costs = self.costs_data.get('fixed_cost', {})
            facility_cost = (fixed_costs.get('existing', {}).get('total', 0) + 
                            fixed_costs.get('new', {}).get('total', 0))
            
            # Get team costs
            team_costs = self.costs_data.get('team_cost', {})
            team_cost = (team_costs.get('existing', {}).get('total', 0) + 
                         team_costs.get('new', 0))
            
            # Get logistics costs
            transportation_cost = self.costs_data.get('logist_cost', 0)
            
            hospital_cost = facility_cost + team_cost
            
            total_cost_card = html.Div([
                html.Div([
                    html.I(className="fas fa-dollar-sign fa-2x", style={'color': '#3498db'}),
                    html.H3("Custo Total", className="stat-title")
                ], className="stat-header"),
                html.Div([
                    html.Span(f"R$ {total_cost:,.2f}", className="stat-value"),
                    html.Span("Custo total do sistema", className="stat-label")
                ], className="stat-body")
            ])
            
            hospital_cost_card = html.Div([
                html.Div([
                    html.I(className="fas fa-building fa-2x", style={'color': '#e67e22'}),
                    html.H3("Custos de Instalação", className="stat-title")
                ], className="stat-header"),
                html.Div([
                    html.Span(f"R$ {hospital_cost:,.2f}", className="stat-value"),
                    html.Span(f"{(hospital_cost/total_cost*100) if total_cost > 0 else 0:.1f}% do total", className="stat-label")
                ], className="stat-body")
            ])
            
            logistics_cost_card = html.Div([
                html.Div([
                    html.I(className="fas fa-ambulance fa-2x", style={'color': '#e74c3c'}),
                    html.H3("Custos de Transporte", className="stat-title")
                ], className="stat-header"),
                html.Div([
                    html.Span(f"R$ {transportation_cost:,.2f}", className="stat-value"),
                    html.Span(f"{(transportation_cost/total_cost*100) if total_cost > 0 else 0:.1f}% do total", className="stat-label")
                ], className="stat-body")
            ])
            
            # Create pie chart for cost distribution
            cost_pie = px.pie(
                values=[facility_cost, team_cost, transportation_cost],
                names=['Custos Fixos', 'Custos de Equipe', 'Custos de Transporte'],
                color_discrete_sequence=['#e67e22', '#9b59b6', '#e74c3c'],
                hole=0.4
            )
            cost_pie.update_layout(
                margin=dict(l=20, r=20, t=30, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
            )
            
            # Create facilities distribution chart
            level_counts = {}
            for facility in self.facilities_data:
                level_name = facility.get('level_name', 'Desconhecido')
                facility_type = facility.get('type', 'Desconhecido')
                key = f"{level_name} ({facility_type})"
                level_counts[key] = level_counts.get(key, 0) + 1
            
            dist_fig = px.bar(
                x=list(level_counts.keys()),
                y=list(level_counts.values()),
                color=list(level_counts.keys()),
                labels={'x': 'Tipo de Unidade', 'y': 'Quantidade'},
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            dist_fig.update_layout(
                margin=dict(l=20, r=20, t=30, b=80),
                showlegend=False,
                xaxis_tickangle=-45
            )
            
            # Create usage bar chart
            usage_data = []
            for level, facilities in self.facility_usage.items():
                level_name = {"phc": "Primário", "shc": "Secundário", "thc": "Terciário"}.get(level, level)
                for name, stats in facilities.items():
                    if isinstance(stats, dict):  # Ensure it's a valid dictionary
                        usage_data.append({
                            'name': name,
                            'level': level_name,
                            'capacity': stats.get('capacity', 0),
                            'usage': stats.get('usage', 0),
                            'percentage': stats.get('usage_percentage', 0)  # Convert to percentage
                        })
            
            if usage_data:
                usage_df = pd.DataFrame(usage_data)
                usage_df = usage_df.sort_values('percentage', ascending=False)
                usage_fig = px.bar(
                    usage_df,
                    x='name',
                    y=['usage', 'capacity'],
                    labels={'value': 'Capacidade/Uso', 'name': 'Unidade', 'variable': 'Medida'},
                    color_discrete_map={'usage': '#3498db', 'capacity': '#95a5a6'},
                    barmode='overlay'    html.H5("Equipe:", style={'fontSize': '16px', 'color': '#3498db', 'marginBottom': '8px', 'marginTop': '15px'}),
                )da equipe", 
                usage_fig.update_layout(
                    margin=dict(l=20, r=20, t=30, b=100),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),popup_content.extend(team_section)
                    xaxis_tickangle=-45ignificant roles (up to 2) for preview
                )
            else:team_data.get('total_team'), dict):ty.get("longitude", 0))
                # Create empty figure if no datax: x[1], reverse=True)[:2]
                usage_fig = go.Figure()
                usage_fig.update_layout(
                    title="Sem dados de utilização disponíveis",
                    xaxis=dict(showticklabels=False),x'}),
                    yaxis=dict(showticklabels=False)
                )
                             style={'fontSize': '13px', 'margin': '3px 0', 'fontWeight': 'bold'}),r_children.append(dl.Popup(popup_div))
            return total_card, existing_card, new_card, total_cost_card, hospital_cost_card, logistics_cost_card, cost_pie, dist_fig, usage_fig {additional_members:.1f}" if additional_members > 0 else "Sem adições de equipe", 
                          style={'fontSize': '13px', 'margin': '3px 0', 'color': '#e74c3c' if additional_members > 0 else '#7f8c8d'})level = facility.get('level')
        # Update the map markers with clickable facilities
        @self.app.callback(', '.join(significant_roles)}" if significant_roles else "",
            [Output('markers-layer', 'children'),                  style={'fontSize': '13px', 'margin': '3px 0'})    position=[lat, lon],
             Output('flows-layer', 'children')],ackgroundColor': '#f8f9fa', 'padding': '10px', 'borderRadius': '5px', 'marginBottom': '8px'}),
            [Input('apply-filters-btn', 'n_clicks'),        html.Div([        "iconUrl": LEVEL.get(level),
             Input('reset-filters-btn', 'n_clicks')],ipe", id={'type': 'team-detail-btn', 'index': facility.get('name', '')},
            [State('level-filter', 'value'),
             State('type-filter', 'value'),                        'backgroundColor': '#3498db',    },
             State('show-flows', 'value')]
        )
        def update_map(apply_clicks, reset_clicks, selected_levels, selected_types, show_flows):                        'padding': '5px 10px',markers.append(m)
            def is_facility_visible(facility, selected_levels, selected_types):erRadius': '4px',
                if facility.get('type') == 'Existente':                        'fontSize': '12px',t(f"Error creating marker for facility: {e}")
                    return facility.get('level') in selected_levels and facility.get('type') in selected_types          'cursor': 'pointer',
                elif facility.get('type') == 'Nova':'width': '100%'
                    original_level = facility.get('original_level')            })
                    return original_level in selected_levels and facility.get('type') in selected_typeser'})
                return False
            section)dst_name, selected_levels, selected_types):
            markers = []  # Initialize the markers listel of the flow isn't selected, don't show it
            LEVEL = {titude", 0))
                "1": "https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png",on = float(facility.get("longitude", 0))   return False
                "2": "https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-yellow.png",
                "3": "https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png",n = []
                "4": "https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-orange.png",
                "5": "https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-violet.png",tip_text = str(facility.get("name", ""))ors = {
                "6": "https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-grey.png"            marker_children.append(dl.Tooltip(tooltip_text, permanent=False, direction="top"))            "1": "#2ecc71",  # Green for Demand → Level 1 (primary)
            }#f1c40f",  # Yellow for Level 1 → Level 2 (secondary)
            content, style={'minWidth': '200px', 'maxWidth': '300px'})Level 2 → Level 3 (tertiary)
            for facility in self.facilities_data:    marker_children.append(dl.Popup(popup_div))}
                try:
                    if is_facility_visible(facility, selected_levels, selected_types):
                        popup_content = [
                            html.H4(str(facility.get("name", "")), style={'color': '#2c3e50', 'marginBottom': '10px', 'fontSize': '18px'}),e, destinations in flows_by_source.items():
                            html.P(f"Unidade de {'Nova ' if facility.get('type') == 'Nova' else ''}Nível {facility.get('original_level', facility.get('level'))}",n=[lat, lon],isinstance(destinations, dict):
                                  style={'fontSize': '14px', 'marginBottom': '15px'})        icon={                for dest_name, flow_val in destinations.items():
                        ]ame, selected_levels, selected_types):
                        onSize": [20, 33],         source_coords = None
                        if 'capacity' in facility and facility['capacity'] != 'N/A':
                            usage_section = [
                                html.H5("Utilização:", style={'fontSize': '16px', 'color': '#3498db', 'marginBottom': '8px'}),
                                html.Div([   )                       if k == "1" and source_name in self.neighborhood_coords:
                                    html.P(f"Capacidade: {facility['capacity']:.2f}" if isinstance(facility['capacity'], (int, float)) else f"Capacidade: {facility['capacity']}",    markers.append(m)                            source_coords = [
                                          style={'fontSize': '13px', 'margin': '3px 0'}),),me].get('latitude', 0)), 
                                    html.P(f"Atendimentos: {facility['usage']:.2f}" if isinstance(facility['usage'], (int, float)) else f"Atendimentos: {facility['usage']}",r for facility: {e}")    float(self.neighborhood_coords[source_name].get('longitude', 0))
                                          style={'fontSize': '13px', 'margin': '3px 0'}),),
                                    html.P(f"% de Uso: {facility['usage_pct']:.2f}%" if isinstance(facility['usage_pct'], (int, float)) else f"% de Uso: {facility['usage_pct']}",
                                          style={'fontSize': '13px', 'margin': '3px 0'})})
                                ], style={'backgroundColor': '#f8f9fa', 'padding': '10px', 'borderRadius': '5px'})
                            ]
                            popup_content.extend(usage_section), selected_levels, selected_types):_coords = [float(facility.get('latitude', 0)), float(facility.get('longitude', 0))]
                            e flow isn't selected, don't show it            break
                        # Add team information if available with more details
                        if 'team_data' in facility:
                            team_data = facility['team_data']
                            
                            # Calculate total team members (sum of all roles)
                            total_members = sum(team_data.get('total_team', {}).values()) if isinstance(team_data.get('total_team'), dict) else 0})
                            additional_members = sum(team_data.get('additional_team', {}).values()) if isinstance(team_data.get('additional_team'), dict) else 0
                             for Level 1 → Level 2 (secondary)y create the flow line if both coordinates were found
                            team_section = [
                                html.H5("Equipe:", style={'fontSize': '16px', 'color': '#3498db', 'marginBottom': '8px', 'marginTop': '15px'}),
                                html.Div([
                                    html.P(f"Total de profissionais: {total_members:.1f}", s():Error, TypeError):
                                          style={'fontSize': '13px', 'margin': '3px 0', 'fontWeight': 'bold'}),els:        flow_value = 1.0
                                    html.P(f"Equipe adicional: {additional_members:.1f}" if additional_members > 0 else "Sem adições de equipe", 
                                          style={'fontSize': '13px', 'margin': '3px 0', 'color': '#e74c3c' if additional_members > 0 else '#7f8c8d'})al level key from the data
                                ], style={'backgroundColor': '#f8f9fa', 'padding': '10px', 'borderRadius': '5px', 'marginBottom': '8px'}),loop
                                html.P("Clique no marcador para ver detalhes completos da equipe", 
                                      style={'fontSize': '13px', 'fontStyle': 'italic', 'color': '#7f8c8d', 'textAlign': 'center'}) = None
                            ]dest_coords = None    # Scale line width more conservatively (divide by 100 instead of 50)
                            popup_content.extend(team_section)
                        borhood (demand point)
                        lat = float(facility.get("latitude", 0))"1" and source_name in self.neighborhood_coords:eate tooltip text showing flow details
                        lon = float(facility.get("longitude", 0))
                        rds[source_name].get('latitude', 0)), 
                        marker_children = []borhood_coords[source_name].get('longitude', 0))e with appropriate styling
                        ]line = dl.Polyline(
                        tooltip_text = str(facility.get("name", ""))
                        marker_children.append(dl.Tooltip(tooltip_text, permanent=False, direction="top"))
                        
                        popup_div = html.Div(popup_content, style={'minWidth': '200px', 'maxWidth': '300px'})    if facility.get('name') == source_name:    opacity=1.0,       # Full opacity (was 0.7)
                        marker_children.append(dl.Popup(popup_div))acility.get('longitude', 0))]
                        
                        level = facility.get('level')children=[dl.Tooltip(tooltip_text)]
                        
                        m = dl.Marker(
                            position=[lat, lon],if facility.get('name') == dest_name:
                            icon={e', 0)), float(facility.get('longitude', 0))]
                                "iconUrl": LEVEL.get(level),
                                "iconSize": [20, 33],
                                "iconAnchor": [10, 33]nd
                            },coords:
                            children=marker_children
                        )oat(flow_val) if flow_val and not isinstance(flow_val, bool) else 1.0
                        markers.append(m)TypeError):
                except Exception as e:
                    print(f"Error creating marker for facility: {e}")
                    continuee - always use the original level key from the data                                                # not the filtered key from the outer loop                                                flow_color = flow_colors.get(k, "#9b59b6")  # Added fallback color                                                                                                # Scale line width more conservatively (divide by 100 instead of 50)                                                line_width = max(0.7, min(5, 0.7 + (flow_value / 100)))                                                                                                # Create tooltip text showing flow details                                                tooltip_text = f"Fluxo: {source_name} → {dest_name} ({flow_value:.2f})"                                                                                                # Create the polyline with appropriate styling                                                line = dl.Polyline(                                                    positions=[source_coords, dest_coords],                                                    color=flow_color,  # Use the correct level color
                          weight=line_width,
            flow_lines = []ty=1.0,       # Full opacity (was 0.7)
            if show_flows and 'show' in show_flows:                                        dashArray=None,
                try:              pane="flowPane",
                    def should_draw_flow(k, src_name, dst_name, selected_levels, selected_types):                                            children=[dl.Tooltip(tooltip_text)]
                        # If the level of the flow isn't selected, don't show it                              )
                        if k not in selected_levels:         flow_lines.append(line)
                            return False                except Exception as e:
                        return Truef"Error generating flows: {e}")
                    
                    # Define colors per level - match the marker colorsturn markers, flow_lines
                    flow_colors = {    
                        "1": "#2ecc71",  # Green for Demand → Level 1 (primary)    def run(self):









































































```    mapa.run()    mapa = Create_Map("P.O Saude/dados_json/bairro_demanda_set.json")if __name__ == "__main__":        self.app.run_server(debug=True)    def run(self):                    return markers, flow_lines                                print(f"Error generating flows: {e}")                except Exception as e:                                                flow_lines.append(line)                                                )                                                    children=[dl.Tooltip(tooltip_text)]                                                    pane="flowPane",                                                    dashArray=None,                                                    opacity=1.0,       # Full opacity (was 0.7)                                                    weight=line_width,                                                    color=flow_color,  # Use the correct level color                                                    positions=[source_coords, dest_coords],                                                line = dl.Polyline(                                                # Create the polyline with appropriate styling                                                                                                tooltip_text = f"Fluxo: {source_name} → {dest_name} ({flow_value:.2f})"                                                # Create tooltip text showing flow details                                                                                                line_width = max(0.7, min(5, 0.7 + (flow_value / 100)))                                                # Scale line width more conservatively (divide by 100 instead of 50)                                                                                                flow_color = flow_colors.get(k, "#9b59b6")  # Added fallback color                                                # not the filtered key from the outer loop                                                # This is the fixed line - always use the original level key from the data                                                                                                    flow_value = 1.0                                                except (ValueError, TypeError):                                                    flow_value = float(flow_val) if flow_val and not isinstance(flow_val, bool) else 1.0                                                try:                                            if source_coords and dest_coords:                                            # Only create the flow line if both coordinates were found                                                                                                break                                                    dest_coords = [float(facility.get('latitude', 0)), float(facility.get('longitude', 0))]                                                if facility.get('name') == dest_name:                                            for facility in self.facilities_data:                                            # Look for destination facility coordinates                                                                                                    break                                                        source_coords = [float(facility.get('latitude', 0)), float(facility.get('longitude', 0))]                                                    if facility.get('name') == source_name:                                                for facility in self.facilities_data:                                            else:                                            # For other levels - source is a facility                                                ]                                                    float(self.neighborhood_coords[source_name].get('longitude', 0))                                                    float(self.neighborhood_coords[source_name].get('latitude', 0)),                                                 source_coords = [                                            if k == "1" and source_name in self.neighborhood_coords:                                            # For level 1 - source is a neighborhood (demand point)                                                                                        dest_coords = None                                            source_coords = None                                        if should_draw_flow(k, source_name, dest_name, selected_levels, selected_types):                                    for dest_name, flow_val in destinations.items():                                if isinstance(destinations, dict):                            for source_name, destinations in flows_by_source.items():                        if k in selected_levels:                    for k, flows_by_source in self.flows.items():                                        }                        "3": "#e74c3c",  # Red for Level 2 → Level 3 (tertiary)                        "2": "#f1c40f",  # Yellow for Level 1 → Level 2 (secondary)        self.app.run_server(debug=True)

if __name__ == "__main__":
    mapa = Create_Map("P.O Saude/dados_json/bairro_demanda_set.json")
    mapa.run()
```
