import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt



# Adicionar logo após os imports existentes
import os
from otimo import BFGS, Newton, NelderMeadSimplex, QuasiNewton, DFP, GradienteConjugado, HookeJeeves, Gradiente, DirecoesAleatorias, SecaoAurea, Quadratica
# Função que representa o sistema de controle (sistema de primeira ordem)
def system(T, t, u):
    # Equação diferencial de um sistema de primeira ordem
    # dT/dt = -T + u
    return -T + u

# Função que define o controlador PID
def pid_controller(Kp, Ki, Kd, e, e_integral, e_derivative):
    return Kp * e + Ki * e_integral + Kd * e_derivative

# Função para simular o sistema controlado
def simulate_pid(Kp, Ki, Kd, T_ref, T0, t):
    T = T0  # Temperatura inicial do sistema
    e_integral = 0  # Parte integral do erro
    e_previous = 0  # Erro anterior (para derivada)
    response = []  # Armazenar a resposta do sistema

    for i in range(len(t)):
        # Erro entre a referência e o valor atual
        e = T_ref - T
        # Integral do erro
        e_integral += e * (t[1] - t[0])
        # Derivada do erro
        e_derivative = (e - e_previous) / (t[1] - t[0])

        # Sinal de controle (PID)
        u = pid_controller(Kp, Ki, Kd, e, e_integral, e_derivative)

        # Atualizar a temperatura usando a equação diferencial
        T = odeint(system, T, [t[i], t[i] + (t[1] - t[0])], args=(u,))[-1].item()
        # Armazenar a resposta e atualizar o erro anterior
        response.append(T)
        e_previous = e

    return np.array(response)

# Função-objetivo: calcular o erro quadrático médio (MSE) entre a resposta e a referência
def funcaoobjetivo(x):
    # Parâmetros de simulação


    T_ref = 100.0   # Temperatura de referência (setpoint)
    T0 = 25.0      # Temperatura inicial do sistema
    t = np.linspace(0, 10, 100)  # Tempo de simulação
    Kp, Ki, Kd = x
    response = simulate_pid(Kp, Ki, Kd, T_ref, T0, t)
    mse = np.mean((T_ref - response) ** 2)

    return mse


# Chute inicial para os parâmetros do controlador PID
ponto_inicial = [1.0, 0.1, 0.01]

# Diretório para salvar resultados (relativo ao diretório deste script)
RESULTADO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Resultado')
os.makedirs(RESULTADO_DIR, exist_ok=True)

# Dicionário de otimizadores com nomes legíveis
otimizadores = {
    # "Quadratica": Quadratica() Quadrática não é adequada para este problema 
    "Gradiente": Gradiente(unidimensional=SecaoAurea()),
    "Newton": Newton(unidimensional=SecaoAurea()),
    "Quasi-Newton": QuasiNewton(unidimensional=SecaoAurea()),
    "DFP": DFP(unidimensional=SecaoAurea()),
    "BFGS": BFGS(unidimensional=SecaoAurea()),
    "Gradiente Conjugado": GradienteConjugado(unidimensional=SecaoAurea()),
    "Hooke-Jeeves": HookeJeeves(),
    "Nelder-Mead Simplex": NelderMeadSimplex(),
}

resultados = []

for nome_otimizador, otimizador in otimizadores.items():
    # Alternativa: usar NelderMeadSimplex que não requer cálculo de gradientes
    # otimizador = NelderMeadSimplex(precisao=1e-4)

    # Executar a otimização
    solucao = otimizador.resolva(funcaoobjetivo, ponto_inicial)

    # Extraia aqui os parâmetros PID otimizados
    Kp_opt, Ki_opt, Kd_opt = solucao.x
    num_iter = solucao.iter

    # Simulação final com os parâmetros otimizados
    T_ref = 100.0
    T0 = 25.0
    t = np.linspace(0, 10, 100)
    response_opt = simulate_pid(Kp_opt, Ki_opt, Kd_opt, T_ref, T0, t)

    # Melhore a visualização
    plt.figure(figsize=(8, 5))
    plt.plot(
        t,
        response_opt,
        label=f'Otimizado: Kp={Kp_opt:.2f}, Ki={Ki_opt:.2f}, Kd={Kd_opt:.2f}\nIterações: {num_iter}',
        linewidth=2
    )
    plt.axhline(y=T_ref, color='r', linestyle='--', label='Referência', linewidth=1.5)
    plt.xlabel('Tempo', fontsize=12)
    plt.ylabel('Temperatura', fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.title(f'({nome_otimizador})', fontsize=14)
    plt.tight_layout()
    nome_arquivo = f"PID_{nome_otimizador.replace(' ', '_')}.png"
    caminho_arquivo = os.path.join(RESULTADO_DIR, nome_arquivo)
    plt.savefig(caminho_arquivo, dpi=150)
    plt.close()

    # # Salvar gráfico do valor da função objetivo (MSE) ao longo do tempo
    # mse_array = (T_ref - response_opt) ** 2
    # plt.figure(figsize=(8, 5))
    # plt.plot(t, mse_array, label='Erro Quadrático Instantâneo', color='purple', linewidth=2)
    # plt.xlabel('Tempo', fontsize=12)
    # plt.ylabel('Erro Quadrático (MSE)', fontsize=12)
    # plt.title(f'Erro Quadrático ao Longo do Tempo\n({nome_otimizador})', fontsize=14)
    # plt.grid(True, linestyle=':', alpha=0.7)
    # plt.tight_layout()
    # plt.legend(fontsize=10)
    # nome_arquivo_mse = f"MSE_{nome_otimizador.replace(' ', '_')}.png"
    # caminho_arquivo_mse = os.path.join(RESULTADO_DIR, nome_arquivo_mse)
    # plt.savefig(caminho_arquivo_mse, dpi=150)
    # plt.close()

    resultados.append({
        "Otimizador": nome_otimizador,
        "Kp": Kp_opt,
        "Ki": Ki_opt,
        "Kd": Kd_opt,
        "iterções": num_iter
    })

# Printar tabela de resultados
print("\nResumo dos parâmetros PID otimizados:")
print(f"{'Otimizador':<25} {'Kp':>8} {'Ki':>8} {'Kd':>8} {'iterções':>30}")
print("-" * 110)
for r in resultados:
    print(f"{r['Otimizador']:<25} {r['Kp']:8.3f} {r['Ki']:8.3f} {r['Kd']:8.3f} {r['iterções']:>30}")
'''
Gradiente                    9.279   14.463    0.004                            574
Newton                       9.344   12.626    0.007                             99
Quasi-Newton                 9.409   13.198   -0.000                             13
DFP                            nan      nan      nan                            130
BFGS                         9.410   13.185   -0.000                              9
Gradiente Conjugado          9.407   13.202    0.000                             93
Hooke-Jeeves                 9.403   13.218    0.000                            266
Nelder-Mead Simplex          9.408   13.200    0.000                             98
'''