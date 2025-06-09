import numpy as np
from otimo import NelderMeadSimplex, HookeJeeves
# Adicionar logo após os imports existentes
import os
# Função de custo negativa (para maximização do lucro)
def funcaoobjetivo(x):
    '''
        Os parâmetros da campanha são: o d, o tempo de
    duração da promoção (t)
    orçamento em marketing (m)
    O lucro da empresa (L(d, t, m)) é igual a receita (R(d, t, m)) menos os custos (C(d, t, m)). 
    '''
    d, t, m = x  # Desconto, tempo, orçamento
    VB = 100000  # Vendas básicas
    CB = 10000  # Custo fixo inicial
    


    # f1(d) = −0.005d² + 0.2d é o incremento percentual nas vendas devido ao desconto.
    def f1(d):
        return -0.005 * d ** 2 + 0.2 * d
    # f2(t) = 0.05t é o incremento nas vendas proporcional ao tempo da promoção.
    def f2(t):
        return 0.05 * t
    
    # Custo
    def P(d, t, m):
        penalidades = 0
        '''
        E importante frisar que: ´
        O desconto não pode ser menor que 0% nem maior que 50% (0 ≤ d ≤ 50).
        O tempo de duração da promoção não pode ser menor que 1 dia nem maior
        que 30 dias (1 ≤ t ≤ 30).
        O orçamento de marketing não pode ser menor que R$1000 nem maior que
        R$50000 (1000 ≤ m ≤ 50000).
        Para implementar essas restrições você pode acrescentá-las `as penalizações. Por
        exemplo, se qualquer uma dessas variáveis ultrapassar os limites, você pode adicionar
        somar um valor muito alto, por exemplo, 1.000.000.
        '''
        if d > 30:
            penalidades += 5000  # Penalidade fixa se o desconto for maior que 30%
        if d <= 0 or d >= 50:
            penalidades += 1000000
        if t > 15:
            penalidades += 3000 # Penalidade fixa se o tempo for maior que 15 dias
        if t < 1 or t > 30:
            penalidades += 1000000
        if m < 1000 or m > 50000:
            penalidades += 1000000
        return penalidades
    def CM():
        return m
    """
    Implemente agora as penalidades. Por exemplo:
    
    if x > 100:
        penalidades += 5000
    """
    '''
    C(d, t, m) = CB + CM(m) + P(d, t, m) (7)
    CB é o custo fixo inicial.
    CM(m) = m é o custo de marketing.
    P(d, t) é uma penalização não contínua:
    '''
    custo_total = CB + CM() + P(d, t, m)
    # Receita
    '''
    A receita é dada por:
    R(d, t, b) = VB · (1 + f1(d) + f2(t)) · log(1 + b)
    
    VB é o número de vendas sem promoção.
    onde:
    '''
    receita = VB * (1 + f1(d) + f2(t)) * np.log(1 + m)

    # Lucro
    lucro = receita - custo_total
    
    # Lembre-se que eu quero maximizar o lucro e meu algoritmo de otimização minimiza a função objetivo
    return -lucro 

# Chute inicial

""" IMPLEMENTE AQUI A CHAMADA DO ALGORTIMO DE OTIMIZAÇÃO """
# Diretório para salvar resultados (relativo ao diretório deste script)
RESULTADO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Resultado3')
os.makedirs(RESULTADO_DIR, exist_ok=True)

# Dicionário de otimizadores com nomes legíveis
otimizadores = {
    "Hooke-Jeeves": HookeJeeves(),
    "Nelder-Mead Simplex": NelderMeadSimplex(),
}
ponto_inicial = [10, 10, 10000]
resultados = []
# Resultados
# d = ???
# t = ???
# m = ???
# lucro = ???
for nome_otimizador, otimizador in otimizadores.items():
    # Alternativa: usar NelderMeadSimplex que não requer cálculo de gradientes
    # otimizador = NelderMeadSimplex(precisao=1e-4)

    # Executar a otimização
    solucao = otimizador.resolva(funcaoobjetivo, ponto_inicial)

    # Extraia aqui os parâmetros PID otimizados
    d, t, m = solucao.x
    lucro = -solucao.fx  # Lembre-se que a função objetivo é negativa do lucro
    num_iter = solucao.iter

    resultados.append({
        "Otimizador": nome_otimizador,
        "d": float(d),
        "t": float(t),
        "m": float(m),
        "Lucro": float(lucro),
        "Iterações": num_iter
    })

# Printar tabela de resultados
print("\nResumo dos parâmetros otimizados:")
print(f"{'Otimizador':<25} {'d':>8} {'t':>8} {'m':>12} {'Lucro':>15} {'Iterações':>12}")
print("-" * 80)
for r in resultados:
    print(f"{r['Otimizador']:<25} {r['d']:8.3f} {r['t']:8.3f} {r['m']:12.3f} {r['Lucro']:15.3f} {r['Iterações']:12}")

