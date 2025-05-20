"""
Configuration settings and constants for the healthcare visualization application.
"""

# File paths
DATA_PATHS = {
    "neighborhoods": "P.O Saude/dados_json/bairro_demanda_set.json",
    "facilities": {
        "level1": "P.O Saude/dados_json/EL_1.json",
        "level2": "P.O Saude/dados_json/EL_2.json", 
        "level3": "P.O Saude/dados_json/EL_3.json"
    },
    "new_locations": "P.O Saude/Resultado/new_locations.json",
    "flow_results": "P.O Saude/Resultado/flow_results.json",
    "new_facilities": {
        "level1": "P.O Saude/dados_json/novas_unidades_nivel_1.json",
        "level2": "P.O Saude/dados_json/novas_unidades_nivel_2.json",
        "level3": "P.O Saude/dados_json/novas_unidades_nivel_3.json"
    }
}

# Alternative paths (fallbacks)
ALT_PATHS = {
    "new_locations": "new_locations.json"
}

# External stylesheets
EXTERNAL_STYLESHEETS = [
    'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css'
]

# Color schemes
COLORS = {
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

# Marker colors based on facility level
MARKER_ICONS = {
    "1": "https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png",
    "2": "https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-yellow.png",
    "3": "https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png",
    "4": "https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-orange.png",
    "5": "https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-violet.png",
    "6": "https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-grey.png"
}

# Flow colors
FLOW_COLORS = {
    "1": "#2ecc71",  # Green for Demand → Level 1 (primary)
    "2": "#f1c40f",  # Yellow for Level 1 → Level 2 (secondary)
    "3": "#e74c3c",  # Red for Level 2 → Level 3 (tertiary)
    "default": "#9b59b6"  # Purple as fallback
}

# Facility type mapping
FACILITY_TYPES = {
    "1": "Primário (PHC)",
    "2": "Secundário (SHC)", 
    "3": "Terciário (THC)"
}

# Marker level mapping
MARKER_LEVEL_MAP = {"1": "4", "2": "5", "3": "6"}

# Facility type to key mapping
FACILITY_TYPE_KEYS = {"1": "phc", "2": "shc", "3": "thc"}
