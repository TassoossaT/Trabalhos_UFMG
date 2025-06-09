import numpy as np
from otimo import SecaoAurea, Gradiente, Newton, BFGS, GradienteConjugado, NelderMeadSimplex

# Definição da função-objetivo
def funcaoobjetivo(x):
    x1, x2 = x
    fx = 4*x1**2 + 4*x2**2
    return fx

# Parâmetros gerais
otimizacao_unidimensional = SecaoAurea(precisao=1e-2, passo=1e-3, maxaval=200)
maximo_iteracoes = 1000
maximo_avaliacoes = 15000
solucao_inicial = [1, 1]

# Método Quasi-Newton
metodo = Gradiente(unidimensional=otimizacao_unidimensional,
                   maxit=maximo_iteracoes,
                   maxaval=maximo_avaliacoes)
resultado = metodo.resolva(funcaoobjetivo, solucao_inicial)

# Método de Newton
metodo = Newton(unidimensional=otimizacao_unidimensional,
                maxit=maximo_iteracoes,
                maxaval=maximo_avaliacoes)
resultado = metodo.resolva(funcaoobjetivo, solucao_inicial)

# Método Quais-Newton BFGS
metodo = BFGS(unidimensional=otimizacao_unidimensional,
              maxit=maximo_iteracoes,
              maxaval=maximo_avaliacoes)
resultado = metodo.resolva(funcaoobjetivo, solucao_inicial)

# Método do Gradiente Conjugado
metodo = GradienteConjugado(unidimensional=otimizacao_unidimensional,
                            maxit=maximo_iteracoes,
                            maxaval=maximo_avaliacoes)
resultado = metodo.resolva(funcaoobjetivo, solucao_inicial)

# Método Nelder-Mead Simplex
metodo = NelderMeadSimplex(maxit=maximo_iteracoes,
                            maxaval=maximo_avaliacoes)
resultado = metodo.resolva(funcaoobjetivo, solucao_inicial)

# Extrai os resultados
solucao_final = resultado.x
funcaoobjetivo_final = resultado.fx
numero_iteracoes = resultado.iter
numero_avaliacoes = resultado.aval

# Exibe os resultados
print(f'Solução final: {solucao_final}')
print(f'Função-objetivo final: {funcaoobjetivo_final}')
print(f'Número de iterações: {numero_iteracoes}')
print(f'Número de avaliações: {numero_avaliacoes}')

# Plota trajetória para o caso bidimensional
resultado.resultados(funcaoobjetivo,
                     [-5, 5], # Intervalo para x1
                     [-5, 5]) # Intervalo para x2