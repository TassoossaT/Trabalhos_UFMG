"""
Data management module for healthcare visualization application.
Handles loading, processing, and providing access to data.
"""

import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from shapely import wkt
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.colors import PowerNorm
from .config import DATA_PATHS, ALT_PATHS, MARKER_LEVEL_MAP, FACILITY_TYPES, FACILITY_TYPE_KEYS

class DataManager:
    """
    Manages all data operations for the application.
    """
    
    def __init__(self):
        """Initialize data manager and load all required data."""
        self.data = None  # Neighborhood GeoDataFrame
        self.center = None  # Map center coordinates
        self.bounds = None  # Map bounds
        self.facilities_data = []  # All facilities (existing and new)
        self.neighborhood_coords = {}  # Neighborhood centroids
        self.team_data = {}  # Team information per facility
        self.costs_data = {}  # Cost information
        self.facility_usage = {}  # Facility usage data
        self.flows = {}  # Flow data between points
        
        # Load data
        self.load_neighborhood_data()
        self.load_facilities_data()
        self.load_results_data()
    
    def load_neighborhood_data(self):
        """Load and process neighborhood data."""
        try:
            with open(DATA_PATHS["neighborhoods"], encoding="utf-8") as f:
                self.data = gpd.GeoDataFrame(json.load(f))
            
            # Process geometry
            if "GEOMETRIA" in self.data.columns:
                geometry = self.data["GEOMETRIA"].apply(wkt.loads)
                self.data = gpd.GeoDataFrame(self.data, geometry=geometry)
            elif "longitude" in self.data.columns and "latitude" in self.data.columns:
                geometry = self.data.apply(lambda row: Point(row["longitude"], row["latitude"]), axis=1)
                self.data = gpd.GeoDataFrame(self.data, geometry=geometry)
            else:
                raise AttributeError("No geometry data found. Provide 'GEOMETRIA' or 'longitude' and 'latitude' columns.")
            
            # Calculate map center and bounds
            bounds = self.data.total_bounds
            self.center = [(bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2]
            self.bounds = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]
            
            # Extract neighborhood centroids
            for idx, row in self.data.iterrows():
                if 'NOME' in row and hasattr(row.geometry, 'centroid'):
                    centroid = row.geometry.centroid
                    self.neighborhood_coords[row['NOME']] = {
                        'latitude': centroid.y,
                        'longitude': centroid.x
                    }
            
            # Add colors to data
            self.add_colors_to_data()
            
        except Exception as e:
            print(f"Error loading neighborhood data: {e}")
            raise
    
    def add_colors_to_data(self):
        """Add color information to neighborhoods based on population."""
        min_val = self.data['QTDPESSOAS'].min()
        max_val = self.data['QTDPESSOAS'].max()
        norm = PowerNorm(gamma=0.1, vmin=min_val, vmax=max_val)
        color = lambda cor: mcolors.to_hex(plt.get_cmap('Blues')(norm(cor)))
        self.data['color'] = self.data['QTDPESSOAS'].apply(lambda x: color(x))
    
    def load_facilities_data(self):
        """Load existing and new healthcare facilities."""
        self.facilities_data = []
        
        # Load existing facilities
        for level in ["1", "2", "3"]:
            try:
                with open(DATA_PATHS["facilities"][f"level{level}"], 'r', encoding='utf-8') as f:
                    markers_data = json.load(f)
                for m in markers_data:
                    m["level"] = level
                    m["type"] = "Existente"
                    m["level_name"] = FACILITY_TYPES.get(level, "Desconhecido")
                    self.facilities_data.append(m)
            except Exception as e:
                print(f"Error loading facilities for level {level}: {e}")
        
        # Load new facilities
        try:
            # Try to load saved new locations
            try:
                with open(DATA_PATHS["new_locations"], encoding="utf-8") as f:
                    saved_names = json.load(f)
            except:
                with open(ALT_PATHS["new_locations"], encoding="utf-8") as f:
                    saved_names = json.load(f)
                    
            # Process each level of new facilities
            for level_key, names in saved_names.items():
                if names:
                    try:
                        coord_file = DATA_PATHS["new_facilities"][f"level{level_key}"]
                        with open(coord_file, encoding='utf-8') as f:
                            coord_markers = json.load(f)
                        for m in [m for m in coord_markers if m["name"] in names]:
                            m["level"] = MARKER_LEVEL_MAP.get(level_key, level_key)
                            m["original_level"] = level_key
                            m["type"] = "Nova"
                            m["level_name"] = FACILITY_TYPES.get(level_key, "Desconhecido")
                            self.facilities_data.append(m)
                    except Exception as e:
                        print(f"Error loading new facilities for level {level_key}: {e}")
        except Exception as e:
            print(f"Error loading new facilities: {e}")
    
    def load_results_data(self):
        """Load simulation results data including costs, usage and flows."""
        try:
            with open(DATA_PATHS["flow_results"], encoding="utf-8") as f:
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
                    # Create placeholder for team data
                    self.team_data = {
                        "phc": {},
                        "shc": {},
                        "thc": {}
                    }
                    
                    # Add team variation data based on existing information
                    for facility_type in ["phc", "shc", "thc"]:
                        if facility_type in self.facility_usage:
                            for facility_name, usage_data in self.facility_usage[facility_type].items():
                                if isinstance(usage_data, dict) and "usage" in usage_data:
                                    self.team_data[facility_type][facility_name] = {
                                        "original_team": {"medico": 2, "enfermeiro": 3, "tecnico": 5},
                                        "additional_team": {"medico": 1, "enfermeiro": 1, "tecnico": 2},
                                        "total_team": {"medico": 3, "enfermeiro": 4, "tecnico": 7}
                                    }
                
                # Process usage data for facilities
                self._process_facility_usage()
                
        except Exception as e:
            print(f"Error loading results data: {e}")
            self.costs_data = {}
            self.facility_usage = {}
            self.flows = {}
            self.team_data = {}
    
    def _process_facility_usage(self):
        """Process facility usage data and add it to facility objects."""
        for facility in self.facilities_data:
            level_key = facility.get("original_level", facility.get("level"))
            facility_type = FACILITY_TYPE_KEYS.get(level_key, "phc")
            
            # First add usage data
            if facility_type in self.facility_usage:
                usage_data = self.facility_usage[facility_type].get(facility["name"], {})
                facility["capacity"] = usage_data.get("capacity", "N/A")
                facility["usage"] = usage_data.get("usage", "N/A")
                facility["usage_pct"] = usage_data.get("usage_percentage", "N/A")
            
            # Then add team data
            if facility_type in self.team_data and facility["name"] in self.team_data[facility_type]:
                facility["team_data"] = self.team_data[facility_type][facility["name"]]
        
        # Sanitize facilities data
        self._sanitize_facilities_data()
    
    def _sanitize_facilities_data(self):
        """Sanitize facility data to ensure proper display."""
        for facility in self.facilities_data:
            # Convert nested objects to strings, but preserve team_data
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
    
    def get_facility_by_name(self, facility_name):
        """
        Find a facility by its name.
        
        Args:
            facility_name (str): The name of the facility to find
            
        Returns:
            dict or None: The facility data if found, None otherwise
        """
        for facility in self.facilities_data:
            if str(facility.get('name', '')) == facility_name:
                return facility
        return None
    
    def get_facilities_dataframe(self):
        """
        Convert facilities data to a pandas DataFrame.
        
        Returns:
            pandas.DataFrame: DataFrame containing facility information
        """
        # Create a clean copy of facilities data for DataFrame conversion
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
        
        return pd.DataFrame(facilities_list)

    def get_geojson_data(self):
        """
        Get neighborhood data as GeoJSON.
        
        Returns:
            dict: GeoJSON representation of neighborhood data
        """
        return json.loads(self.data.to_json())
    
    def filter_facilities(self, selected_levels=None, selected_types=None):
        """
        Filter facilities based on level and type.
        
        Args:
            selected_levels (list): List of level values to include
            selected_types (list): List of facility types to include
            
        Returns:
            list: Filtered list of facilities
        """
        if selected_levels is None:
            selected_levels = ["1", "2", "3"]
        if selected_types is None:
            selected_types = ["Existente", "Nova"]
            
        filtered = []
        for facility in self.facilities_data:
            if self._is_facility_visible(facility, selected_levels, selected_types):
                filtered.append(facility)
        return filtered
    
    def _is_facility_visible(self, facility, selected_levels, selected_types):
        """Determine if a facility should be visible based on filters."""
        if facility.get('type') == 'Existente':
            return facility.get('level') in selected_levels and facility.get('type') in selected_types
        elif facility.get('type') == 'Nova':
            original_level = facility.get('original_level')
            return original_level in selected_levels and facility.get('type') in selected_types
        return False
