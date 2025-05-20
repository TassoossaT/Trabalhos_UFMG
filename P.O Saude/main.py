"""
Main entry point for the healthcare visualization application.
Initializes and runs the Dash app.
"""

from dash import Dash
from app.data_manager import DataManager
from app.layout import create_layout
from app.callbacks import CallbackManager
from app.config import EXTERNAL_STYLESHEETS

def main():
    """
    Initialize and run the application.
    """
    print("Loading data...")
    data_manager = DataManager()
    
    print("Initializing Dash app...")
    app = Dash(__name__, 
               suppress_callback_exceptions=True, 
            external_stylesheets=EXTERNAL_STYLESHEETS)
    
    print("Creating layout...")
    app.layout = create_layout(data_manager)
    
    print("Registering callbacks...")
    callback_manager = CallbackManager(app, data_manager)
    
    print("Starting server...")
    app.run_server(debug=True)
    
if __name__ == "__main__":
    main()
