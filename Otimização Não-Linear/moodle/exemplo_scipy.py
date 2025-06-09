import numpy as np

# Importa a função minimize do módulo scipy.optimize que implementa os métodos
# de otimização
from scipy.optimize import minimize

# Definição da função-objetivo
def funcaoobjetivo(x):
    x1, x2 = x
    fx = 4*x1**2 + 4*x2**2
    return fx

# Parâmetros gerais
maximo_iteracoes = 1000
maximo_avaliacoes = 15000
solucao_inicial = [1, 1]

# Método Quasi-Newton - BFGS
resultado = minimize(funcaoobjetivo, solucao_inicial, method='BFGS',
                     options={'maxiter': maximo_iteracoes})

# Método Gradiente Conjugado
resultado = minimize(funcaoobjetivo, solucao_inicial, method='CG',
                     options={'maxiter': maximo_iteracoes})

# Método Nelder-Mead Simplex
resultado = minimize(funcaoobjetivo, solucao_inicial, method='Nelder-Mead',
                     options={'maxiter': maximo_iteracoes,
                              'maxfev': maximo_avaliacoes})

# Extrai os resultados
solucao_final = resultado.x
funcaoobjetivo_final = resultado.fun
numero_iteracoes = resultado.nit
numero_avaliacoes = resultado.nfev

# Exibe os resultados
print(f'Solução final: {solucao_final}')
print(f'Função-objetivo final: {funcaoobjetivo_final}')
print(f'Número de iterações: {numero_iteracoes}')
print(f'Número de avaliações: {numero_avaliacoes}')
