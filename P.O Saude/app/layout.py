"""
Layout module for the healthcare visualization application.
Defines the structure and components of the user interface.
"""

from dash import html, dcc, dash_table
import dash_leaflet as dl
from dash_extensions.javascript import assign  # Add this import for the assign function

from .components.modals import create_team_modal
from .config import COLORS

def create_layout(data_manager):
    """
    Create the main application layout.
    
    Args:
        data_manager (DataManager): The data manager instance with loaded data
    
    Returns:
        html.Div: The complete application layout
    """
    # Dashboard container
    return html.Div([
        # Header
        create_header(),
        
        # Main content container with tabs
        html.Div([
            dcc.Tabs(id="app-tabs", value='map-tab', className="custom-tabs", children=[
                # Map tab
                create_map_tab(data_manager),
                
                # Statistics tab
                create_statistics_tab(),
                
                # Facilities list tab
                create_facilities_tab(data_manager),
            ])
        ], className="content-container"),
        
        # Footer
        create_footer(),
        
        # Modals
        create_team_modal(),
        
        # Data stores
        dcc.Store(id='filtered-facilities-data'),
        dcc.Store(id='summary-data'),
        dcc.Store(id='active-tab', data='map-tab'),
        dcc.Store(id='selected-facility-data'),
        
    ], className="dashboard-container")

def create_header():
    """Create the dashboard header."""
    return html.Div([
        html.Div([
            html.H1("Sistema de Saúde de Belo Horizonte", className="header-title"),
            html.P("Visualização de Unidades de Saúde e Análise de Dados", className="header-subtitle")
        ], className="header-content")
    ], className="dashboard-header")

def create_footer():
    """Create the dashboard footer."""
    return html.Div([
        html.P("Sistema de Visualização de Unidades de Saúde", className="footer-text"),
        html.P("© 2023 UFMG", className="footer-copyright")
    ], className="dashboard-footer")

def create_map_tab(data_manager):
    """Create the map tab content."""
    return dcc.Tab(
        label='Mapa Interativo', 
        value='map-tab', 
        className='custom-tab', 
        selected_className='custom-tab--selected', 
        children=[
            html.Div([
                # Filters sidebar
                html.Div([
                    html.Div([
                        html.H3("Filtros", className="filter-heading"),
                        
                        # Level filter
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
                        
                        # Type filter
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
                        
                        # Flow visualization toggle
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
                        
                        # Filter buttons
                        html.Div([
                            html.Button('Aplicar Filtros', id='apply-filters-btn', className="apply-btn"),
                            html.Button('Redefinir', id='reset-filters-btn', className="reset-btn"),
                        ], className="filter-actions")
                    ], className="filter-card")
                ], className="filter-sidebar"),
                
                # Map container
                html.Div([
                    html.Div([
                        dl.Map(
                            id='map-display',
                            children=[
                                dl.TileLayer(url='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', 
                                             attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'),
                                create_geojson_layer(data_manager),
                                create_info_overlay(),
                                dl.Pane(id="flowPane", name="flowPane", style={"zIndex": 610}),
                                dl.LayerGroup(id='markers-layer'),
                                dl.LayerGroup(id='flows-layer'),
                            ], 
                            center=data_manager.center,
                            minZoom=11.4,
                            bounds=data_manager.bounds,
                            maxBounds=data_manager.bounds,
                            maxBoundsViscosity=0.1,
                            worldCopyJump=False,
                            style={'width': '100%', 'height': '70vh', 'borderRadius': '8px'}
                        ),
                        create_map_legend()
                    ], className="map-container")
                ], className="map-wrapper")
            ], className="map-tab-content")
        ]
    )

def create_geojson_layer(data_manager):
    """Create GeoJSON layer for map."""
    geojson_data = data_manager.get_geojson_data()
    
    # Use the assign function from dash_extensions.javascript
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
        data=geojson_data,
        style=style_handle,
        zoomToBounds=True,
        zoomToBoundsOnClick=True,
        hoverStyle={"weight": 1, "color": '#666', "dashArray": ''},
        id="geojson"
    )

def create_info_overlay():
    """Create info overlay component for map."""
    return html.Div(
        children=get_info_content(), 
        id="info", 
        className="info",
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
        }
    )

def get_info_content(feature=None):
    """Get content for info overlay."""
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

def create_map_legend():
    """Create legend for map markers."""
    return html.Div([
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

def create_statistics_tab():
    """Create statistics tab content."""
    return dcc.Tab(
        label='Painel de Estatísticas', 
        value='summary-tab', 
        className='custom-tab', 
        selected_className='custom-tab--selected', 
        children=[
            html.Div([
                # Stats cards
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
                
                # Charts
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
        ]
    )

def create_facilities_tab(data_manager):
    """Create facilities list tab with data table."""
    facilities_df = data_manager.get_facilities_dataframe()
    
    # Generate tooltip data
    tooltip_data = []
    for row in facilities_df.to_dict('records'):
        row_tooltips = {}
        for column, value in row.items():
            # Make sure we only use strings in tooltips
            row_tooltips[column] = {'value': str(value) if value is not None else '', 'type': 'markdown'}
        tooltip_data.append(row_tooltips)
    
    return dcc.Tab(
        label='Lista de Unidades', 
        value='facilities-tab', 
        className='custom-tab', 
        selected_className='custom-tab--selected', 
        children=[
            html.Div([
                # Table filters
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
                
                # Facilities table
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
                            'backgroundColor': COLORS['primary'],
                            'color': COLORS['white'],
                            'fontWeight': 'bold',
                            'fontSize': '15px',
                            'padding': '15px 16px',
                            'borderTop': f'1px solid {COLORS["primary"]}'
                        },
                        style_data={
                            'backgroundColor': COLORS['white'],
                            'border': f'1px solid {COLORS["light"]}'  # Fixed quote syntax in f-string
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
                                'color': COLORS['accent'],
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
        ]
    )
