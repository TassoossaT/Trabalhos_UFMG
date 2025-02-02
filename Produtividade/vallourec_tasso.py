import pandas as pd
#import matplotlib.pyplot as plt

df = pd.DataFrame({
    "Atividade": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N"],
    "Descrição": [  "Produção de Aço"           , #A
                    "Laminação do Tubo"         , #B
                    "Tratamento termico"        , #C
                    "Laboratório de superfícies", #D
                    "Transporte entre planta"   , #E
                    "Usinagem"                  , #F
                    "Rosqueadeira"              , #G
                    "Preparação para entrega"   , #H
                    "Laboratório de amostra"    , #I
                    "Laminação da Luva"         , #J
                    "Tratamento térmico da Luva", #K
                    "Laboratorio da luva"       , #L
                    "Acabamento da Luva"        , #M
                    "Acoplamento"]              , #N
    "Atividades Predecessoras": [   " ",        #A
                                    "A",        #B
                                    "B",        #C
                                    "C",        #D
                                    "C",        #E
                                    "E",        #F
                                    "F",        #G
                                    "D,I,L,N",  #H
                                    "F",        #I
                                    "A",        #J
                                    "J",        #K
                                    "K",        #L
                                    "K",        #M
                                    "G,M"       #N
                                    ],
    "Duração [Dias]": [25, 21, 23, 32, 13, 2, 2, 2, 32, 7, 8, 32, 2, 3]
})
def cmax(df):
    import pulp
    
    atividades      = df['Atividade'].tolist()
    duracoes        = df['Duração [Dias]'].tolist()
    predecessores   = df['Atividades Predecessoras'].tolist()
    
    problem = pulp.LpProblem("Minimize Cmax", pulp.LpMinimize)
    ti      = pulp.LpVariable.dicts("ti", atividades, lowBound=0, cat=pulp.LpContinuous)
    Cmax    = pulp.LpVariable("Cmax", lowBound=0, cat=pulp.LpContinuous)
    # (2)
    for i, atividade in enumerate(atividades):
        problem += ti[atividade] + duracoes[i] <= Cmax
        for predecessor in predecessores[i].split(','):
            if predecessor != " ":
                problem += ti[atividade] >= ti[predecessor] + duracoes[atividades.index(predecessor)]
    problem.solve()

    print(Cmax.varValue)
    for i, atividade in enumerate(atividades):
        print(f"Custo para chegar em {atividade}: {ti[atividade].varValue}")

cmax(df)
#def caminho_critico_pulp(df):
#    import pulp
#
#    atividades      = df['Atividade'].tolist()
#    duracoes        = df['Duração [Dias]'].tolist()
#    predecessores   = df['Atividades Predecessoras'].tolist()
#
#    problem = pulp.LpProblem("Caminho Crítico", pulp.LpMinimize)
#    x       = pulp.LpVariable.dicts("x", atividades, lowBound=0, cat=pulp.LpInteger)
#    for i, atividade in enumerate(atividades):
#        for predecessor in predecessores[i].split(','):
#            if predecessor != ' ':
#                problem += x[atividade] >= x[predecessor] + duracoes[i]
#
#    problem += pulp.lpSum([x[atividade] for atividade in atividades])
#    problem.solve()
#    caminho_critico = {}
#    for atividade in atividades:
#            caminho_critico[atividade] = x[atividade].varValue + duracoes[len(atividade)-1]
#    return caminho_critico, pulp.value(problem.objective)
def grafo_caminho_critico(df):
    import networkx as nx
    atividades      = df['Atividade'].tolist()
    duracoes        = df['Duração [Dias]'].tolist()
    predecessores   = df['Atividades Predecessoras'].tolist()

    grafo = nx.DiGraph()
    for i, atividade in enumerate(atividades):
        grafo.add_node(atividade)
        for predecessor in predecessores[i].split(','):
            if predecessor != ' ':
                grafo.add_edge(predecessor, atividade)
    caminho_critico = []
    while grafo.nodes:
        for nodo in nx.topological_sort(grafo):
            if not nx.descendants(grafo, nodo):
                caminho_critico.append(nodo)
                grafo.remove_node(nodo)
                break
    return caminho_critico

#grafo = grafo_caminho_critico(df)
#pulp, duracao  = caminho_critico_pulp(df)
#
#print('Caminho Crítico com metodo grafo')
#for atividade in grafo:
#    #duracao += df['Duração [Dias]'][df['Atividade'][atividade]]
#    print(atividade)
#print('Caminho Crítico usando P.O com pulp')
#print(f"Valor da função objetivo: {duracao}//somatorio de todas as durações")
#for atividade, tempo in pulp.items():
#    print(f"{atividade}: {tempo:.2f} dias")

