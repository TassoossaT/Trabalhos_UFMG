"""
Modal dialog components for the healthcare visualization app.
"""

from dash import html

def create_team_modal():
    """
    Create the team details modal component.
    
    Returns:
        html.Div: The modal dialog component
    """
    return html.Div([
        html.Div([
            html.Div([
                html.H3(id="team-modal-title", className="modal-title"),
                html.Button("×", id="close-team-modal", className="close-button")
            ], className="modal-header"),
            html.Div(id="team-modal-content", className="modal-body"),
        ], className="modal-content")
    ], id="team-detail-modal", className="modal", style={'display': 'none'})

def generate_team_modal_content(facility):
    """
    Generate content for the team details modal.
    
    Args:
        facility (dict): Facility data containing team information
        
    Returns:
        tuple: (modal_title, modal_content) for the modal dialog
    """
    if not facility:
        return "", []
        
    # Get facility name
    facility_name = facility.get('name', 'Unknown Facility')
    
    # Get team data
    team_data = facility.get('team_data')
    
    # If no team data, show appropriate message
    if not team_data:
        return f"Informações de Equipe - {facility_name}", [
            html.Div("Não há dados de equipe disponíveis para esta unidade.", 
                     className="no-data-message")
        ]
    
    # Create team variation content
    modal_title = f"Variações de Equipe - {facility_name}"
    
    original_team = team_data.get("original_team", {})
    additional_team = team_data.get("additional_team", {})
    total_team = team_data.get("total_team", {})
    
    content = html.Div([
        html.Div([
            html.H4("Equipe Original"),
            html.Table([
                html.Thead(html.Tr([
                    html.Th("Cargo"),
                    html.Th("Quantidade")
                ])),
                html.Tbody([
                    html.Tr([html.Td(role), html.Td(f"{count:.1f}")])
                    for role, count in original_team.items()
                ])
            ], className="team-table")
        ], className="team-section"),
        
        html.Div([
            html.H4("Equipe Adicional"),
            html.Table([
                html.Thead(html.Tr([
                    html.Th("Cargo"),
                    html.Th("Quantidade")
                ])),
                html.Tbody([
                    html.Tr([html.Td(role), html.Td(f"{count:.1f}")])
                    for role, count in additional_team.items()
                ])
            ], className="team-table")
        ], className="team-section"),
        
        html.Div([
            html.H4("Equipe Total"),
            html.Table([
                html.Thead(html.Tr([
                    html.Th("Cargo"),
                    html.Th("Quantidade")
                ])),
                html.Tbody([
                    html.Tr([html.Td(role), html.Td(f"{count:.1f}")])
                    for role, count in total_team.items()
                ])
            ], className="team-table")
        ], className="team-section"),
        
        html.Div([
            html.H4("Informações de Utilização"),
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
            html.P([
                html.Strong("Utilização: "), 
                f"{facility.get('usage_pct', 'N/A'):.1f}%" if isinstance(facility.get('usage_pct'), (int, float))
                else f"{facility.get('usage_pct', 'N/A')}%"
            ])
        ], className="usage-section")
    ])
    
    return modal_title, content
