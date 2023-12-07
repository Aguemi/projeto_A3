from flask import Flask, render_template, request
import networkx as nx
import folium
from geopy.distance import geodesic

app = Flask(__name__)


# Todas as cidades 

class LogisticaRelampago:
    def __init__(self):
        self.cidades = {
            "Curitiba/PR": {"endereco": "Endereco Curitiba", "posicao": (-25.4294, -49.2719)},
            "Londrina/PR": {"endereco": "Endereco Londrina", "posicao": (-23.3045, -51.1696)},
            "Foz do Iguaçu/PR": {"endereco": "Endereco Foz do Iguaçu", "posicao": (-25.5478, -54.5882)},
            "União da Vitória/PR": {"endereco": "Endereco União da Vitória", "posicao": (-26.2376, -51.0873)},
            "Joinville/SC": {"endereco": "Endereco Joinville", "posicao": (-26.3032, -48.8410)},
            "Chapecó/SC": {"endereco": "Endereco Chapecó", "posicao": (-27.1009, -52.6157)},
            "Porto Alegre/RS": {"endereco": "Endereco Porto Alegre", "posicao": (-30.0346, -51.2177)},
            "Uruguaiana/RS": {"endereco": "Endereco Uruguaiana", "posicao": (-29.7541, -57.0856)},
            "Pelotas/RS": {"endereco": "Endereco Pelotas", "posicao": (-31.7649, -52.3376)},
        }

        self.custo_por_km = 20
        self.max_km_por_dia = 500

        self.grafo = self.criar_grafo()

#Criando o grafo

    def criar_grafo(self):
        G = nx.Graph()

        for cidade, info in self.cidades.items():
            G.add_node(cidade, endereco=info["endereco"], posicao=info["posicao"])

        # Adiciona arestas considerando as regras de negócio
        G.add_edge("Foz do Iguaçu/PR", "União da Vitória/PR", weight=self.calcular_distancia("Foz do Iguaçu/PR", "União da Vitória/PR"))
        G.add_edge("Joinville/SC", "Chapecó/SC", weight=self.calcular_distancia("Joinville/SC", "Chapecó/SC"))

        # Adiciona arestas entre cidades que têm conexões indiretas
        G.add_edge("Curitiba/PR", "Foz do Iguaçu/PR", weight=self.calcular_distancia("Curitiba/PR", "Foz do Iguaçu/PR"))
        G.add_edge("União da Vitória/PR", "Foz do Iguaçu/PR", weight=self.calcular_distancia("União da Vitória/PR", "Foz do Iguaçu/PR"))

        return G
#Calculo distancia 

    def calcular_distancia(self, cidade_origem, cidade_destino):
        posicao_origem = self.cidades[cidade_origem]["posicao"]
        posicao_destino = self.cidades[cidade_destino]["posicao"]
        return geodesic(posicao_origem, posicao_destino).kilometers

#Calculo caminho e custo 

    def calcular_caminho_e_custo(self, origem, destino):
        if origem not in self.cidades or destino not in self.cidades:
            print("Origem ou destino inválidos.")
            return None, None, None, None, None

        if not nx.has_path(self.grafo, origem, destino):
            print(f"Não há um caminho válido entre {origem} e {destino}.")
            return None, None, None, None, None

        caminho = nx.shortest_path(self.grafo, origem, destino, weight="weight")
        distancia_total = nx.shortest_path_length(self.grafo, origem, destino, weight="weight")
        custo_total = distancia_total * self.custo_por_km
        tempo_estimado = distancia_total / self.max_km_por_dia  # Em dias
        data_hora_chegada = "Calcular com base no tempo estimado"

        return caminho, distancia_total, custo_total, tempo_estimado, data_hora_chegada

# Exibir mapa

    def exibir_mapa(self, caminho):
        mapa = folium.Map(location=self.cidades[caminho[0]]["posicao"], zoom_start=7)

        for cidade in caminho:
            folium.Marker(
                location=self.cidades[cidade]["posicao"],
                popup=f"{cidade}\n{self.cidades[cidade]['endereco']}",
                icon=folium.Icon(color="blue"),
            ).add_to(mapa)

        folium.PolyLine(
            locations=[self.cidades[cidade]["posicao"] for cidade in caminho],
            color="red",
            weight=5,
            opacity=0.7,
        ).add_to(mapa)

        mapa.save("templates/caminho_otimizado")

@app.route("/", methods=["GET", "POST"])
def index():
    logistica_relampago = LogisticaRelampago()
    caminho, distancia, custo, tempo, data_hora_chegada = None, None, None, None, None

    if request.method == "POST":
        origem = request.form["origem"]
        destino = request.form["destino"]

        caminho, distancia, custo, tempo, data_hora_chegada = logistica_relampago.calcular_caminho_e_custo(origem, destino)

    return render_template("index.html", caminho=caminho, distancia=distancia, custo=custo, tempo=tempo, data_hora_chegada=data_hora_chegada)

if __name__ == "__main__":
    app.run(debug=True)
