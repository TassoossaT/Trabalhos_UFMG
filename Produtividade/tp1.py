import matplotlib.pyplot as plt
from dotmap import DotMap

from dea_compacto_Tasso import *

data_dist.print()

#if __name__ == "__main__":
#    main()
''' Tp 1
Rode os modelos CRS/CCR e analise os resultados. Identifique os itens abaixo:

• a eficiência das DMUs
• histograma das eficiências
• identifique as DMUs dentro das eficiências do histograma
• os benchmarks para cada DMU
• os pesos relativos dos inputs e outputs
• identifique as DMUs fortemente e fracamente eficientes
• apresente as projeções e metas para os inputs e outputs
'''
def Tp_1():
    dados().print()
    ccr_multiplicadores = Model_frabric_Weight(normatize_data(dados()))
    ccr_envelope = Model_frabric_Envelope(normatize_data(dados()),slack=True)
    
    ccr_multiplicadores.model()
    ccr_envelope.model()
    
    ccr_multiplicadores.print_solution(only_ef=True)
    ccr_multiplicadores.print_solution()
    ccr_envelope.print_solution(print_all=False)
    ccr_envelope.goal(lamda=True)
    Classificador_Eficiencia(dados()).print()
    ccr_envelope.print_goal()
    
''' Tp 2
Rode os modelos BCC, IRS, DRS em ambas orientações e analise os resultados. Identifique os itens
abaixo:

• a eficiência (pura,total e escala) das DMUs
• identifique em que escala as DMUs operam para cada modelo
• histograma das eficiências
• identifique as DMUs dentro das eficiências do histograma
• os benchmarks para cada DMU
• os pesos relativos dos inputs e outputs
• apresente as projeções e metas para os inputs e outputs
• calcule o FDH para os dois tipos de abordagem (provisão e distribuição)
'''
def Tp_2():
    bcc_multi_inp = Model_frabric_Weight(normatize_data(dados()),scale="Const")
    bcc_multi_out = Model_frabric_Weight(normatize_data(dados()),mode="Output",scale="Const")
    
    irs_multi_inp = Model_frabric_Weight(normatize_data(dados()),scale="Negative")
    irs_multi_out = Model_frabric_Weight(normatize_data(dados()),mode="Output",scale="Negative")
    
    drs_multi_inp = Model_frabric_Weight(normatize_data(dados()),scale="Positive")
    drs_multi_out = Model_frabric_Weight(normatize_data(dados()),mode="Output",scale="Positive")
    bcc_multi_inp.model()
    bcc_multi_out.model()
    irs_multi_inp.model()
    irs_multi_out.model()
    drs_multi_inp.model()
    drs_multi_out.model()
    bcc_multi_inp.print_solution(only_ef=True)
    #bcc_multi_out.print_solution(only_ef=True)
    irs_multi_inp.print_solution(only_ef=True)
    #irs_multi_out.print_solution(only_ef=True)
    drs_multi_inp.print_solution(only_ef=True)
    #drs_multi_out.print_solution(only_ef=True)
''' Tp 3
Rode o modelo aditivo de Pareto-Koopmans e compare com o resultado dos modelos BCC e CCR obtidos
nos laboratórios I e II. Analise os resultados e identifique os itens abaixo:

• a eficiência (pura,total e escala) das DMUs
• identifique em que escala as DMUs operam para cada modelo
• histograma das eficiências
• identifique as DMUs dentro das eficiências do histograma
• os benchmarks para cada DMU
• os pesos relativos dos inputs e outputs
'''

''' Tp 4
Rode o modelo baseado em folgas e compare com o resultado dos modelos BCC, CCR, e Pareto-Koopmans
obtidos nos laboratórios I a III. Analise os resultados e identifique os itens abaixo:

• a eficiência (pura,total e escala) das DMUs
• identifique em que escala as DMUs operam para cada modelo
• histograma das eficiências
• identifique as DMUs dentro das eficiências do histograma
• os benchmarks para cada DMU
• os pesos relativos dos inputs e outputs
''' 

''' Tp 5
Rode o modelo da medida aprimorada de Russel e compare com o resultado dos modelos BCC, CCR,
Pareto-Koopmans, e baseado em folgas obtidos nos laboratórios I a IV. Analise os resultados e identifique

• a eficiência (pura,total e escala) das DMUs
• identifique em que escala as DMUs operam para cada modelo
• histograma das eficiências
• identifique as DMUs dentro das eficiências do histograma
• os benchmarks para cada DMU
• os pesos relativos dos inputs e outputs
'''