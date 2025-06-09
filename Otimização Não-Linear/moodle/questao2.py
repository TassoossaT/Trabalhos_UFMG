import numpy as np

# Função sigmoide
def sigmoid(z):
    return 1 / (1 + np.exp(-z))

# Função-objetivo
def funcaoobjetivo(w):
    
    # Carregar os dados do problema
    dados = np.load('moodle\questao2_dados.npz')
    X = dados['X'] # Entrada: matriz de dimensões m x n
    y = dados['y'] # Saída: rótulos binários
    m, n = X.shape
    lambd = 0.1

    h = sigmoid(X @ w)
    loss = -np.mean(y * np.log(h + 1e-9) + (1 - y) * np.log(1 - h + 1e-9))
    reg = (lambd / 2) * np.sum(w**2)
    return loss + reg


# Chute inicial dos pesos
n = 500 # elevada dimensão
w0 = np.zeros(n)

""" IMPLEMENTE AQUI A CHAMADA DO ALGORTIMO DE OTIMIZAÇÃO """

from otimo import SecaoAurea,Gradiente, Newton,QuasiNewton,GradienteConjugado,BFGS,NelderMeadSimplex,HookeJeeves,DFP
import time


otimizadores = {
    # "BFGS": BFGS(unidimensional=SecaoAurea()),
    "Gradiente Conjugado": GradienteConjugado(unidimensional=SecaoAurea())
}
'''
Em geral, métodos quasi-Newton convergem em menos iteraçôes,
porém requerem mais computaçãao e mais memória por iteração.
Portanto, gradientes conjugados é mais indicado em problemas de
elevada dimensão
'''

# Configura o método de busca de linha
for nome_otimizador, otimizador in otimizadores.items():
    inicial = time.time()    # Executa a otimização
    sol = otimizador.resolva(funcaoobjetivo, w0)
    total = time.time() - inicial
    # Resultados
    custo_final = sol.fx
    numero_iteracoes = sol.iter
    numero_avaliacoes = sol.aval
    print(f"Resultados para {nome_otimizador}:")
    print(f"Custo final: {custo_final:.4f}")
    print(f"Número de iterações: {numero_iteracoes}")
    print(f"Número de avaliações da função-objetivo: {numero_avaliacoes}")
    print(f"Tempo total de execução: {total:.4f} segundos")
    
'''
Resultados para BFGS:
Custo final: 0.0948
Número de iterações: 19
Número de avaliações da função-objetivo: 10200
Tempo total de execução: 2228.9764 segundos

Resultados para Gradiente Conjugado:
Custo final: 1065565756843717689344.0000
Número de iterações: 2
Número de avaliações da função-objetivo: 1530
Tempo total de execução: 336.6283 segundos



Eu não sei o que acontece para o gradiente resultar nisso, a primeira iteração é boa, mas a segunda é um desastre.
0.09368533856799674
1.0655663084298253e+21

porém ele ainda é o mais util, o problema é que demora muito tempo para um resultado e isso atrapalha para corrir o problema
'''