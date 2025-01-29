import pandas as pd
import geopandas as gpd
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash import Dash, html, Output, Input
from dash_extensions.javascript import arrow_function, assign
import json
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.colors import PowerNorm

from python.Data import Data, LEVEL


class Create_Map:
    def __init__(self, data: pd.DataFrame):
            self.data = data
            bounds = data.total_bounds
            self.center = [(bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2]
            self.bounds = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]
            self.App()
    def Color(self):
        min = self.data['QTDPESSOAS'].min()
        max = self.data['QTDPESSOAS'].max()
        norm = PowerNorm(gamma=0.5, vmin=min, vmax=max)  # Ajuste o valor de gamma conforme necessário
        color = lambda cor: mcolors.to_hex(plt.get_cmap('viridis')(norm(cor)))
        self.data['color'] = self.data['QTDPESSOAS'].apply(lambda x: color(x))
    def GeoJSON(self):
        self.Color()
        style_handle = assign("""
            function(feature, context) {
                return {
                    weight: 2,
                    opacity: 1,
                    color: 'white',
                    dashArray: '3',
                    fillOpacity: 0.7,
                    fillColor: feature.properties['color']
                };
            }
        """)
        return dl.GeoJSON(
            data=json.loads(self.data.to_json()),
            style=style_handle,
            zoomToBounds=True,
            zoomToBoundsOnClick=True,
            hoverStyle={"weight": 5, "color": '#666', "dashArray": ''},
            id="geojson"
            )
    def Info(self,feature=None):
    # Função para gerar as informações a serem exibidas no popup
        def get_info(feature=None):
            header = [html.H4("População por Bairro")]
            if not feature:
                return header + [html.P("Passe o mouse sobre um bairro")]
            bairro      = feature["properties"]["NOME"]
            qtd_pessoas = feature["properties"]["QTDPESSOAS"]
            return header + [html.B(bairro), html.Br(), f"{qtd_pessoas} pessoas"]
        
        return html.Div(children=get_info(feature), id="info", className="info", 
                        style={"position": "absolute", "top": "10px", "right": "10px", "zIndex": "1000"})
    def App(self):
        # Criar o aplicativo Dash
        app = Dash(__name__)
        app.layout = html.Div([
            dl.Map(
                children=[
                    dl.TileLayer(),
                    self.GeoJSON(),
                    self.Info()
                ], 
                center=self.center,  # Centro do mapa
                minZoom=11.4,  # Zoom mínimo permitido
                bounds=self.bounds,  # Limitar navegação
                maxBounds=self.bounds,  # Limitar navegação
                maxBoundsViscosity=0.1,  # Rigor na limitação
                worldCopyJump=False,  # Impedir cópias do mapa ao atravessar o meridiano
                style={'width': '100%', 'height': '600px'}  # Estilo do mapa
            )
        ])
        self.app = app
        self.register_callbacks()

    def add_markers(self, data: pd.DataFrame):
        _markers = data
        markers = []
        for idx, row in _markers.iterrows():
            I_icon_url = {
                # "1":  "assets/hospital-location-stroke-icon-by-Vexels.png",
                "1": "https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png",
                "2": "https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-yellow.png",
                "3": "https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png",
            }
            icon = dict(iconUrl=I_icon_url.get(LEVEL.get(row['SIGLA_CATEGORIA'])))
            marker = dl.Marker( 
                position=[row.geometry.y, row.geometry.x],
                icon = icon,
                children=[
                    dl.Tooltip(row['NOME']),
                    dl.Popup([
                        html.H4(row['NOME']),
                        html.P(f"Categoria: {row['CATEGORIA']}"),
                        html.P(f"Endereço:  {row['TIPO_LOGRADOURO']} {row['LOGRADOURO']}, {row['NUMERO_IMOVEL']}"),
                        html.P(f"Bairro:    {row['NOME_BAIRRO_POPULAR']}"),
                        html.P(f"Telefone:  {row['TELEFONE']}")
                    ])
                ]
            )
            markers.append(marker)
        self.app.layout.children[0].children.append(dl.LayerGroup(markers))
    def register_callbacks(self):
        @self.app.callback(Output("info", "children"), Input("geojson", "hoverData"))
        def info_hover(feature):
            return self.Info(feature).children
    def run(self):
        self.app.run_server(debug=True)
        

if __name__ == "__main__":
    data = Data()
    mapa = Create_Map(data.get_neighborhood())
    mapa.add_markers(data.get_health())
    mapa.run()