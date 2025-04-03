from  pulp import LpProblem, LpMinimize, LpVariable, LpContinuous, LpBinary, LpInteger, lpSum
import pandas as pd




# aprimorar o custo do estoque
# preço de valor perdido por comprar mais caro

model = LpProblem("EntregaCompraEstoque", LpMinimize)

POSTOS = {}
# Parametros
COMBUSTIVEIS        = ["ETANOL", "GASOLINA", "GASOLINA ADITIVADA"]
DEMANDA             = {
                        1: {"ETANOL":4100, "ETANOL ADITIVADO":170, "GASOLINA":8687, "GASOLINA ADITIVADA":284}}


PRECO_ESTOOQUE      = {"ETANOL":0.01,  "GASOLINA":0.01, "GASOLINA ADITIVADA":0.01}
CAPACIDADE_ESTOQUE  = {"ETANOL": 20000, "ETANOL ADITIVADO":20000, "GASOLINA":30000, "GASOLINA ADITIVADA":15000}
ESTOQUE_SEGURANCA   = {"ETANOL": 10000, "ETANOL ADITIVADO":5000, "GASOLINA":10000, "GASOLINA ADITIVADA":5000}

FORNECEDORES = {"ZEMA", "TORRÃO", "FIC", "ALE", "IPIRANGA", "SHELL", "RUFF", "TERRANA", 
    "IMPERIAL", "SP", "RDP", "CIA PETRO", "FLEX PETRO", "POTENCIAL", "LARCO", 
    "BRENO", "PETR BA", "PETR JQ"}

PRECO_COMPRA = {
    "ZEMA": {"ETANOL": 5.2810, "GASOLINA": 5.2950, "GASOLINA ADITIVADA": 5.3060},
    "TORRÃO": {"ETANOL": 3.7820, "GASOLINA": 5.2810, "GASOLINA ADITIVADA": 5.3060},
    "FIC": {"ETANOL": 3.6850, "GASOLINA": 5.2950, "GASOLINA ADITIVADA": 5.3050},
    "ALE": {"ETANOL": 3.8269, "GASOLINA": 5.3469, "GASOLINA ADITIVADA": 5.4669},
    "IPIRANGA": {"ETANOL": 3.8351, "GASOLINA": 5.4525, "GASOLINA ADITIVADA": 5.5745},
    "SHELL": {"ETANOL": 3.8590, "GASOLINA": 5.4650, "GASOLINA ADITIVADA": 5.6383},
    "RUFF": {"ETANOL": 3.7859, "GASOLINA": 5.3444, "GASOLINA ADITIVADA": 5.3574},
    "TERRANA": {"ETANOL": 1000, "GASOLINA": 5.2900, "GASOLINA ADITIVADA": 1000},
    "IMPERIAL": {"ETANOL": 3.7300, "GASOLINA": 5.3300, "GASOLINA ADITIVADA": 1000},
    "SP": {"ETANOL": 3.7390, "GASOLINA": 5.2966, "GASOLINA ADITIVADA": 5.3066},
    "RDP": {"ETANOL": 1000, "GASOLINA": 5.2990, "GASOLINA ADITIVADA": 5.3090},
    "CIA PETRO": {"ETANOL": 3.8300, "GASOLINA": 5.3500, "GASOLINA ADITIVADA": 5.3600},
    "FLEX PETRO": {"ETANOL": 1000, "GASOLINA": 5.3100, "GASOLINA ADITIVADA": 1000},
    "POTENCIAL": {"ETANOL": 3.7524, "GASOLINA": 5.2922, "GASOLINA ADITIVADA": 5.3022},
    "LARCO": {"ETANOL": 3.7400, "GASOLINA": 5.3000, "GASOLINA ADITIVADA": 5.3100},
    "BRENO": {"ETANOL": 1000, "GASOLINA": 5.6400, "GASOLINA ADITIVADA": 5.6500},
    "PETR BA": {"ETANOL": 3.7700, "GASOLINA": 5.3900, "GASOLINA ADITIVADA": 5.4000},
    "PETR JQ": {"ETANOL": 3.8700, "GASOLINA": 5.6400, "GASOLINA ADITIVADA": 5.7400},
}
PRECO_ENTREGA = {
    fornecedor: {combustivel: 0.043 for combustivel in COMBUSTIVEIS}
    for fornecedor in FORNECEDORES
}

PERIODO             = [0,1]

TAMANHO_LOTE        = 5000
LOTES_DISPONIVEIS   = {fornecedor: 10 for fornecedor in FORNECEDORES}

ESTOQUE_INICIAL     = {"ETANOL":10816.76, "ETANOL ADITIVADO":3646.94, "GASOLINA":11477.88, "GASOLINA ADITIVADA":2599.58}


VEICULOS = {'TRUCK','CEGONHA','TREM'}
N_COMPARTIMENTOS = {'TRUCK': 2, 'CEGONHA': 3, 'METRO': 10}
COMPARTIMENTOS = {'TRUCK': ['A','B'], 'CEGONHA': ['A','B','C'], 'TREM': ['A','A','A','A','A','B','B','B','B','C']}
CAPCIDADE_COMPARTIMENTO = {'A': 10000, 'B': 5000, 'C': 3000}


############################################################################################################
# Variáveis de decisão

estoque = {
    # O estoque não pode ser menor que o estoque de segurança nem maior que a capacidade maxima em cada periodo
    t:{combustivel: LpVariable("estoque_"+ combustivel + "_" + str(t), 
                                        lowBound=ESTOQUE_SEGURANCA[combustivel],
                                        upBound=CAPACIDADE_ESTOQUE[combustivel], cat=LpContinuous) 
            for combustivel in COMBUSTIVEIS}
        for t in PERIODO}

compra = {
    # Quantidade de cada combustivel comprado de cada fornecedor 
    t:{fornecedor:{combustivel: LpVariable("compra_"+ fornecedor + "_" + combustivel + "_" + str(t), 
                                        0, None, LpContinuous) 
            for combustivel in COMBUSTIVEIS}
        for fornecedor in FORNECEDORES}
    for t in PERIODO}

lotes_comprados = {
    # Quantidade de lotes comprados de cada fornecedor
    t:{fornecedor:{combustivel: LpVariable("lotes_comprados_"+ fornecedor + "_"+ combustivel + "_" + str(t),
                                        0, None, LpInteger) 
            for combustivel in COMBUSTIVEIS}
        for fornecedor in FORNECEDORES}
    for t in PERIODO}

carregamento = {
    t: {k: {w: {j: {p: LpVariable(f"carregamento_{t}_{k}_{w}_{j}_{p}", 0, 1, LpBinary)
                    for p in COMBUSTIVEIS}
                for j in POSTOS}
            for w in COMPARTIMENTOS[k]}
        for k in VEICULOS} 
    for t in PERIODO}

entrega = {
    t:{i:{j:{k: LpVariable(f"entrega_{t}_{i}_{j}_{k}", 0, 1, LpBinary)
                for k in VEICULOS}
            for j in POSTOS}
        for i in POSTOS}
    for t in PERIODO}


############################################################################################################
# Função Objetivo
CustoCompra  = lambda t: sum(PRECO_COMPRA[fornecedor][combustivel] * compra[t][fornecedor][combustivel] for fornecedor in FORNECEDORES for combustivel in COMBUSTIVEIS) 
CustoEstoque = lambda t: sum(PRECO_ESTOOQUE[combustivel]*estoque[t][combustivel]  for combustivel in COMBUSTIVEIS)
CustoEntrega = lambda t: sum(PRECO_ENTREGA[fornecedor][combustivel] * compra[t][fornecedor][combustivel] for fornecedor in FORNECEDORES for combustivel in COMBUSTIVEIS)

model  += lpSum((CustoCompra(t) + CustoEstoque(t) + CustoEntrega(t)) for t in PERIODO)
############################################################################################################
# Valores iniciasis 
# Adicionar estoque inicial no período 0
# estoque[0] = {combustivel: ESTOQUE_INICIAL[combustivel] for combustivel in COMBUSTIVEIS}
############################################################################################################
# Restrições de Estoque 

for t in PERIODO:
    if t == 0:
        estoque[t] = {combustivel: ESTOQUE_INICIAL[combustivel] for combustivel in COMBUSTIVEIS}
    else:
        for combustivel in COMBUSTIVEIS:
            model += \
            estoque[t][combustivel] == estoque[t-1][combustivel] +\
            lpSum(compra[t-1][fornecedor][combustivel] for fornecedor in FORNECEDORES) -\
            DEMANDA[t][combustivel]
            
            model += estoque[t][combustivel] <= CAPACIDADE_ESTOQUE[combustivel]
            model += estoque[t][combustivel] >= ESTOQUE_SEGURANCA[combustivel]

############################################################################################################
# Restrições de Entrega
for t in PERIODO:
    # Limitação de lote de compra 
    for combustivel in COMBUSTIVEIS:
        for fornecedor in FORNECEDORES:
            model += compra[t][fornecedor][combustivel] == lotes_comprados[t][fornecedor][combustivel] * TAMANHO_LOTE

############################################################################################################
# Restrições de Transporte

############################################################################################################

model.solve()

import matplotlib.pyplot as plt

# Quantidade comprada de cada combustível
# Gráfico XY para mostrar a quantidade comprada de período a período
for combustivel in COMBUSTIVEIS:
    quantidade_por_periodo = [sum(compra[t][fornecedor][combustivel].varValue for fornecedor in FORNECEDORES) for t in PERIODO]
    plt.plot(PERIODO, quantidade_por_periodo, label=combustivel)

plt.title("Quantidade Comprada por Período")
plt.xlabel("Período")
plt.ylabel("Quantidade")
plt.legend()
plt.show()
# Tabela de compra por fornecedor
dados_tabela = []
for t in PERIODO:
    for fornecedor in FORNECEDORES:
        for combustivel in COMBUSTIVEIS:
            total_compra = compra[t][fornecedor][combustivel].varValue
            if total_compra:
                dados_tabela.append({"Periodo": t,"Fornecedor": fornecedor, "Combustível": combustivel, "Quantidade Comprada": total_compra})    
estoque_final = {combustivel: estoque[1][combustivel].varValue for combustivel in COMBUSTIVEIS}
print(estoque_final)
tabela = pd.DataFrame(dados_tabela)
print(tabela)