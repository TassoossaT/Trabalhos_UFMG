"""
Callback functions for the healthcare visualization application.
Organized into a modular, extensible system for easier maintenance and future enhancements.
"""

import logging
from dash import Output, Input, State, callback, html
from dash.exceptions import PreventUpdate
import dash_leaflet as dl
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from .components.modals import generate_team_modal_content
from .config import MARKER_ICONS, FLOW_COLORS, COLORS

# Set up logger
logger = logging.getLogger(__name__)

class CallbackManager:
    """
    Manages all callbacks for the application in a modular, extensible way.
    
    This class is designed to be easily extended with new callbacks.
    Each callback group is organized into its own category with standardized 
    registration methods.
    """
    
    def __init__(self, app, data_manager):
        """
        Initialize the callback manager.
        
        Args:
            app (dash.Dash): The Dash application
            data_manager (DataManager): Data manager instance
        """
        self.app = app
        self.data_manager = data_manager
        self.callback_registry = {}  # Registry to track registered callbacks
        self.register_all_callbacks()
    
    def register_all_callbacks(self):
        """Register all application callbacks by category."""
        # Map related callbacks
        self.register_map_callbacks()
        
        # UI element callbacks
        self.register_ui_interaction_callbacks()
        
        # Data visualization callbacks
        self.register_data_visualization_callbacks()
        
        logger.info(f"Successfully registered {len(self.callback_registry)} callbacks")
    
    def register_callback(self, callback_id, callback_func):
        """
        Helper method to register and track callbacks.
        
        Args:
            callback_id (str): Unique identifier for the callback
            callback_func (callable): The registered callback function
        """
        self.callback_registry[callback_id] = callback_func
        logger.debug(f"Registered callback: {callback_id}")
    
    def register_map_callbacks(self):
        """Register all map-related callbacks."""
        # Neighborhood info hover callback
        @self.app.callback(
            Output("info", "children"), 
            Input("geojson", "hoverData")
        )
        def info_hover(feature):
            """Update info panel when hovering over neighborhoods."""
            try:
                # Will be expanded in future implementations
                return []
            except Exception as e:
                logger.error(f"Error in info hover callback: {e}")
                return []
        
        self.register_callback("info_hover", info_hover)
        
        # Map markers and flows callback
        @self.app.callback(
            [Output('markers-layer', 'children'),
             Output('flows-layer', 'children')],
            # Add a 'loading' input that always fires - makes this run on page load
            [Input('apply-filters-btn', 'n_clicks'),
             Input('reset-filters-btn', 'n_clicks'),
             Input('app-tabs', 'value')],  # Add tab value to trigger on page load
            [State('level-filter', 'value'),
             State('type-filter', 'value'),
             State('show-flows', 'value')]
        )
        def update_map(apply_clicks, reset_clicks, active_tab, selected_levels, selected_types, show_flows):
            """
            Update map markers and flow lines based on filters.
            Also runs on initial page load due to app-tabs input.
            """
            try:
                return self._generate_map_markers_and_flows(
                    active_tab, selected_levels, selected_types, show_flows)
            except Exception as e:
                logger.error(f"Error updating map: {e}")
                return [], []  # Return empty lists if an error occurs
        
        self.register_callback("update_map", update_map)
    
    def _generate_map_markers_and_flows(self, active_tab, selected_levels, selected_types, show_flows):
        """
        Helper function to generate map markers and flows.
        This makes the callback function cleaner and easier to maintain.
        
        Args:
            active_tab (str): Current active tab
            selected_levels (list): Selected facility levels
            selected_types (list): Selected facility types
            show_flows (list): Whether to show flow lines
            
        Returns:
            tuple: (markers, flow_lines) for the map
        """
        # Set default values if none provided
        if not selected_levels:
            selected_levels = ["1", "2", "3"]
        if not selected_types:
            selected_types = ["Existente", "Nova"]
        if not show_flows:
            show_flows = []
        
        # Initialize the markers list
        markers = []
        
        # Add neighborhood markers
        if active_tab == 'map-tab':
            markers.extend(self._create_neighborhood_markers())
        
        # Add facility markers
        markers.extend(self._create_facility_markers(selected_levels, selected_types))
        
        # Add flow lines
        flow_lines = []
        if (show_flows and 'show' in show_flows) or active_tab == 'map-tab':
            flow_lines = self._create_flow_lines(selected_levels, selected_types)
        
        return markers, flow_lines
    
    def _create_neighborhood_markers(self):
        """Generate markers for neighborhood centroids."""
        markers = []
        logger.debug("Adding demand points to map...")
        
        for name, coords in self.data_manager.neighborhood_coords.items():
            try:
                marker = dl.Marker(
                    position=[float(coords['latitude']), float(coords['longitude'])],
                    icon={
                        "iconUrl": "https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png",
                        "iconSize": [15, 24],
                        "iconAnchor": [7, 24]
                    },
                    children=[
                        dl.Tooltip(f"Demanda: {name}", permanent=False),
                        dl.Popup(html.Div([
                            html.H4(f"Bairro: {name}", style={'fontSize': '16px'}),
                            html.P("Ponto de demanda", style={'fontSize': '14px'})
                        ], style={'minWidth': '150px'}))
                    ]
                )
                markers.append(marker)
            except Exception as e:
                logger.error(f"Error creating demand marker for {name}: {e}")
        
        return markers
    
    def _create_facility_markers(self, selected_levels, selected_types):
        """Generate markers for healthcare facilities."""
        markers = []
        
        for facility in self.data_manager.facilities_data:
            try:
                if self.data_manager._is_facility_visible(facility, selected_levels, selected_types):
                    popup_content = self._generate_facility_popup_content(facility)
                    
                    lat = float(facility.get("latitude", 0))
                    lon = float(facility.get("longitude", 0))
                    
                    marker_children = []
                    
                    tooltip_text = str(facility.get("name", ""))
                    marker_children.append(dl.Tooltip(tooltip_text, permanent=False, direction="top"))
                    
                    popup_div = html.Div(popup_content, style={'minWidth': '200px', 'maxWidth': '300px'})
                    marker_children.append(dl.Popup(popup_div))
                    
                    level = facility.get('level')
                    
                    m = dl.Marker(
                        position=[lat, lon],
                        icon={
                            "iconUrl": MARKER_ICONS.get(level, MARKER_ICONS["1"]),
                            "iconSize": [20, 33],
                            "iconAnchor": [10, 33]
                        },
                        children=marker_children
                    )
                    markers.append(m)
            except Exception as e:
                logger.error(f"Error creating marker for facility {facility.get('name', 'unknown')}: {e}")
        
        return markers
    
    def _generate_facility_popup_content(self, facility):
        """Generate popup HTML content for a facility marker."""
        popup_content = [
            html.H4(str(facility.get("name", "")), style={'color': '#2c3e50', 'marginBottom': '10px', 'fontSize': '18px'}),
            html.P(f"Unidade de {'Nova ' if facility.get('type') == 'Nova' else ''}Nível {facility.get('original_level', facility.get('level'))}",
                  style={'fontSize': '14px', 'marginBottom': '15px'})
        ]
        
        if 'capacity' in facility and facility['capacity'] != 'N/A':
            usage_section = [
                html.H5("Utilização:", style={'fontSize': '16px', 'color': '#3498db', 'marginBottom': '8px'}),
                html.Div([
                    html.P(f"Capacidade: {facility['capacity']:.2f}" if isinstance(facility['capacity'], (int, float)) else f"Capacidade: {facility['capacity']}",
                            style={'fontSize': '13px', 'margin': '3px 0'}),
                    html.P(f"Atendimentos: {facility['usage']:.2f}" if isinstance(facility['usage'], (int, float)) else f"Atendimentos: {facility['usage']}",
                            style={'fontSize': '13px', 'margin': '3px 0'}),
                    html.P(f"% de Uso: {facility['usage_pct']:.2f}%" if isinstance(facility['usage_pct'], (int, float)) else f"% de Uso: {facility['usage_pct']}",
                            style={'fontSize': '13px', 'margin': '3px 0'})
                ], style={'backgroundColor': '#f8f9fa', 'padding': '10px', 'borderRadius': '5px'})
            ]
            popup_content.extend(usage_section)
        
        if 'team_data' in facility:
            team_section = [
                html.H5("Equipe:", style={'fontSize': '16px', 'color': '#3498db', 'marginBottom': '8px', 'marginTop': '15px'}),
                html.P("Clique no marcador para ver detalhes da equipe", 
                        style={'fontSize': '13px', 'fontStyle': 'italic', 'color': '#7f8c8d'})
            ]
            popup_content.extend(team_section)
        
        return popup_content
    
    def _create_flow_lines(self, selected_levels, selected_types):
        """Generate flow lines between facilities and/or neighborhoods."""
        flow_lines = []
        
        try:
            for k, flows_by_source in self.data_manager.flows.items():
                if k in selected_levels:
                    flow_lines.extend(self._process_flow_level(k, flows_by_source, selected_levels, selected_types))
            
            logger.info(f"Created {len(flow_lines)} flow lines")
        except Exception as e:
            logger.error(f"Error in flow generation process: {e}")
        
        return flow_lines
    
    def _process_flow_level(self, level, flows_by_source, selected_levels, selected_types):
        """Process flows for a specific level."""
        flow_lines = []
        
        for source_name, destinations in flows_by_source.items():
            if isinstance(destinations, dict):
                for dest_name, flow_val in destinations.items():
                    try:
                        line = self._create_single_flow_line(level, source_name, dest_name, 
                                                           flow_val, selected_levels, selected_types)
                        if line:
                            flow_lines.append(line)
                    except Exception as e:
                        logger.error(f"Error generating flow from '{source_name}' to '{dest_name}': {e}")
        
        return flow_lines
    
    def _create_single_flow_line(self, level, source_name, dest_name, flow_val, selected_levels, selected_types):
        """Create a single flow line between source and destination."""
        # If the level is not selected, don't show the flow
        if level not in selected_levels:
            return None
        
        source_coords = self._get_location_coordinates(level, source_name)
        dest_coords = self._get_facility_coordinates(dest_name)
        
        if not source_coords or not dest_coords:
            return None
        
        try:
            flow_value = float(flow_val) if flow_val and not isinstance(flow_val, bool) else 1.0
        except (ValueError, TypeError):
            flow_value = 1.0
        
        flow_color = FLOW_COLORS.get(level, FLOW_COLORS["default"])
        line_width = max(0.7, min(5, 0.7 + (flow_value / 100)))
        tooltip_text = f"Fluxo: {source_name} → {dest_name} ({flow_value:.2f})"
        
        return dl.Polyline(
            positions=[source_coords, dest_coords],
            color=flow_color,
            weight=line_width,
            opacity=1.0,
            pane="flowPane",
            children=[dl.Tooltip(tooltip_text)]
        )
    
    def _get_location_coordinates(self, level, name):
        """Get coordinates for a location (neighborhood or facility)."""
        # For level 1 - source is a neighborhood (demand point)
        if level == "1" and name in self.data_manager.neighborhood_coords:
            return [
                float(self.data_manager.neighborhood_coords[name].get('latitude', 0)), 
                float(self.data_manager.neighborhood_coords[name].get('longitude', 0))
            ]
        # For other levels - source is a facility
        else:
            return self._get_facility_coordinates(name)
        
    def _get_facility_coordinates(self, name):
        """Get coordinates for a facility by name."""
        for facility in self.data_manager.facilities_data:
            if facility.get('name') == name:
                return [float(facility.get('latitude', 0)), float(facility.get('longitude', 0))]
        return None
    
    def register_ui_interaction_callbacks(self):
        """Register all UI interaction related callbacks (modals, panels, etc)."""
        # Team detail modal callbacks
        @self.app.callback(
            [Output('team-detail-modal', 'style'),
             Output('team-modal-title', 'children'),
             Output('team-modal-content', 'children')],
            [Input('markers-layer', 'click_marker')]
        )
        def show_team_details(marker_click):
            """Show team details when a facility marker is clicked."""
            try:
                if not marker_click:
                    return {'display': 'none'}, "", []
                
                # Extract facility name from the marker popup
                facility_name = marker_click.get('popup', '')
                if not facility_name:
                    logger.warning("No facility name found in marker popup")
                    return {'display': 'none'}, "", []
                
                # Find the facility data using the data manager
                facility = self.data_manager.get_facility_by_name(facility_name)
                
                if not facility:
                    logger.warning(f"Facility not found: {facility_name}")
                    return {'display': 'none'}, "", []
                
                # Generate the modal content
                modal_title, modal_content = generate_team_modal_content(facility)
                
                return {'display': 'block'}, modal_title, modal_content
            except Exception as e:
                logger.error(f"Error showing team details: {e}")
                return {'display': 'none'}, "Error", [html.P("Ocorreu um erro ao exibir os detalhes da equipe.")]
        
        self.register_callback("show_team_details", show_team_details)
        
        @self.app.callback(
            Output('team-detail-modal', 'style', allow_duplicate=True),
            [Input('close-team-modal', 'n_clicks')],
            prevent_initial_call=True
        )
        def close_modal(n_clicks):
            """Close the team details modal when the close button is clicked."""
            if n_clicks:
                return {'display': 'none'}
            raise PreventUpdate
        
        self.register_callback("close_team_modal", close_modal)
        
        # Facilities table filter callback
        @self.app.callback(
            Output('facilities-table', 'data'),
            [Input('facility-search', 'value'),
             Input('facility-level-filter', 'value'),
             Input('facility-type-filter', 'value'),
             Input('app-tabs', 'value')]
        )
        def filter_facilities_table(search_term, level_filter, type_filter, active_tab):
            """Filter the facilities table based on search term, level, and type."""
            try:
                # Only update when on facilities tab
                if active_tab != 'facilities-tab':
                    raise PreventUpdate
                
                return self._filter_facilities_data(search_term, level_filter, type_filter)
            except PreventUpdate:
                raise
            except Exception as e:
                logger.error(f"Error filtering facilities table: {e}")
                return []  # Return empty list on error
        
        self.register_callback("filter_facilities_table", filter_facilities_table)
        
        # Pagination info callback
        @self.app.callback(
            Output('table-pagination-info', 'children'),
            [Input('facilities-table', 'data'),
             Input('facilities-table', 'page_current'),
             Input('facilities-table', 'page_size')]
        )
        def update_pagination_info(data, page_current, page_size):
            """Update pagination information display."""
            try:
                if not data:
                    return "Nenhuma unidade encontrada"
                
                total_facilities = len(data)
                start_idx = (page_current or 0) * page_size + 1 if total_facilities > 0 else 0
                end_idx = min(start_idx + page_size - 1, total_facilities)
                
                return f"Exibindo {start_idx}-{end_idx} de {total_facilities} unidades"
            except Exception as e:
                logger.error(f"Error updating pagination info: {e}")
                return "Error loading pagination info"
        
        self.register_callback("update_pagination_info", update_pagination_info)
    
    def _filter_facilities_data(self, search_term, level_filter, type_filter):
        """Helper function to filter facilities data based on criteria."""
        # Get base facilities data
        facilities_df = self.data_manager.get_facilities_dataframe()
        
        # Apply search filter if provided
        if search_term:
            search_term = search_term.lower()
            facilities_df = facilities_df[facilities_df['name'].str.lower().str.contains(search_term, na=False)]
        
        # Apply level filter if not 'all'
        if level_filter and level_filter != 'all':
            # For facilities with original_level, check that first
            level_condition = ((facilities_df['original_level'] == level_filter) | 
                             (facilities_df['level'] == level_filter))
            facilities_df = facilities_df[level_condition]
        
        # Apply type filter if not 'all'
        if type_filter and type_filter != 'all':
            facilities_df = facilities_df[facilities_df['type'] == type_filter]
        
        return facilities_df.to_dict('records')
    
    def register_data_visualization_callbacks(self):
        """Register all data visualization callbacks (charts, statistics, etc)."""
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
            """Update statistics panel when tab changes."""
            try:
                # Only update if we're on the statistics tab (for performance)
                if tab != 'summary-tab':
                    raise PreventUpdate
                    
                # Get all statistics components
                facility_cards = self._generate_facility_stat_cards()
                cost_cards = self._generate_cost_stat_cards()
                charts = self._generate_statistics_charts()
                
                # Combine all components for return
                return (*facility_cards, *cost_cards, *charts)
            except PreventUpdate:
                raise
            except Exception as e:
                logger.error(f"Error updating statistics: {e}")
                # Return empty placeholders for all outputs in case of error
                empty_card = html.Div("Error loading data")
                empty_figure = px.bar(x=[], y=[])
                return (empty_card, empty_card, empty_card, 
                       empty_card, empty_card, empty_card,
                       empty_figure, empty_figure, empty_figure)
        
        self.register_callback("update_statistics", update_statistics)
    
    def _generate_facility_stat_cards(self):
        """Generate the facility statistics cards."""
        # Calculate facility statistics
        total_facilities = len(self.data_manager.facilities_data)
        existing_facilities = sum(1 for f in self.data_manager.facilities_data if f.get('type') == 'Existente')
        new_facilities = total_facilities - existing_facilities
        
        # Create facility stat cards
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
        
        return total_card, existing_card, new_card
    
    def _generate_cost_stat_cards(self):
        """Generate the cost statistics cards."""
        # Cost statistics
        total_cost = self.data_manager.costs_data.get('total_cost', 0)
        
        # Get facility construction and fixed costs
        fixed_costs = self.data_manager.costs_data.get('fixed_cost', {})
        facility_cost = (fixed_costs.get('existing', {}).get('total', 0) + 
                        fixed_costs.get('new', {}).get('total', 0))
        
        # Get team costs
        team_costs = self.data_manager.costs_data.get('team_cost', {})
        team_cost = (team_costs.get('existing', {}).get('total', 0) + 
                     team_costs.get('new', 0))
        
        # Get logistics costs
        transportation_cost = self.data_manager.costs_data.get('logist_cost', 0)
        
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
        
        return total_cost_card, hospital_cost_card, logistics_cost_card
    
    def _generate_statistics_charts(self):
        """Generate all charts for the statistics tab."""
        cost_pie = self._generate_cost_pie_chart()
        distribution_chart = self._generate_facilities_distribution_chart()
        usage_chart = self._generate_usage_chart()
        
        return cost_pie, distribution_chart, usage_chart
    
    def _generate_cost_pie_chart(self):
        """Generate pie chart showing cost distribution."""
        # Cost statistics
        fixed_costs = self.data_manager.costs_data.get('fixed_cost', {})
        facility_cost = (fixed_costs.get('existing', {}).get('total', 0) + 
                        fixed_costs.get('new', {}).get('total', 0))
        
        team_costs = self.data_manager.costs_data.get('team_cost', {})
        team_cost = (team_costs.get('existing', {}).get('total', 0) + 
                     team_costs.get('new', 0))
        
        transportation_cost = self.data_manager.costs_data.get('logist_cost', 0)
        
        # Create pie chart 
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
        
        return cost_pie
    
    def _generate_facilities_distribution_chart(self):
        """Generate bar chart showing distribution of facilities by type and level."""
        level_counts = {}
        for facility in self.data_manager.facilities_data:
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
        
        return dist_fig
    
    def _generate_usage_chart(self):
        """Generate chart showing facility usage vs capacity."""
        usage_data = []
        for level, facilities in self.data_manager.facility_usage.items():
            level_name = {"phc": "Primário", "shc": "Secundário", "thc": "Terciário"}.get(level, level)
            for name, stats in facilities.items():
                if isinstance(stats, dict):  # Ensure it's a valid dictionary
                    usage_data.append({
                        'name': name,
                        'level': level_name,
                        'capacity': stats.get('capacity', 0),
                        'usage': stats.get('usage', 0),
                        'percentage': stats.get('usage_percentage', 0)
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
                barmode='overlay'
            )
            usage_fig.update_layout(
                margin=dict(l=20, r=20, t=30, b=100),
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
                xaxis_tickangle=-45
            )
        else:
            # Create empty figure if no data
            usage_fig = go.Figure()
            usage_fig.update_layout(
                title="Sem dados de utilização disponíveis",
                xaxis=dict(showticklabels=False),
                yaxis=dict(showticklabels=False)
            )
        
        return usage_fig
