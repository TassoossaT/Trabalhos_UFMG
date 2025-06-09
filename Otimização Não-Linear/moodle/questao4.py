import numpy as np
import matplotlib.pyplot as plt
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from otimo import BFGS, Newton, NelderMeadSimplex, QuasiNewton, DFP, GradienteConjugado, HookeJeeves, Gradiente, DirecoesAleatorias, SecaoAurea, Quadratica

# Diretório para salvar resultados (relativo ao diretório deste script)
RESULTADO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Resultado')
os.makedirs(RESULTADO_DIR, exist_ok=True)

# Dicionário de otimizadores com nomes legíveis
otimizadores = {
    "Newton": Newton(unidimensional=SecaoAurea())
}
# Função-objetivo da equação (9)
def funcaoobjetivo(x):
    x1, x2 = x
    return 0.6382 * x1**2 + 0.3191 * x2**2 - 0.2809 * x1 * x2 - 67.906 * x1 - 14.29 * x2

ponto_inicial = [0, 0]
for nome_otimizador, otimizador in otimizadores.items():
    # Executa a otimização
    solucao = otimizador.resolva(funcaoobjetivo, ponto_inicial)

    # Extraindo os resultados
    x1_opt, x2_opt = solucao.x
    valor_minimo = float(solucao.fx)
    num_iteracoes = solucao.iter

    # Imprime os resultados
    print(f"Resultados para {nome_otimizador}:")
    print(f"Temperaturas de regime permanente (x1, x2): ({x1_opt:.4f}, {x2_opt:.4f})")
    print(f"Valor mínimo da função: {valor_minimo:.4f}")
    print(f"Número de iterações: {num_iteracoes}")


'''
Resultados para Newton:
Temperaturas de regime permanente (x1, x2): (64.3641, 50.7203)
Valor mínimo da função: -2547.7231
Número de iterações: 1
'''