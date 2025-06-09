from mip import Model, xsum, minimize, CBC, OptimizationStatus, BINARY
from itertools import product
import matplotlib.pyplot as plt
from math import sqrt
import numpy as np

ni,nj = 30,10
I,J = range(ni),range(nj)

# custo de instalacao das facilidades
f = [430, 452, 382, 242, 366, 259, 449, 500, 371, 297]

# demanda dos clientes
d = [10, 7, 6, 10, 4, 5, 3, 4, 3, 1, 10, 5, 8, 2, 2, 3, 3, 1, 2, 9, 7, 9, 5, 9, 4, 4, 10, 7, 10, 5]

# posicao geografica dos clientes
posc = np.array([(25, 36), (27, 7), (3, 23), (17, 28), (33, 21), (32, 40), (26, 41), (20, 14), (31, 49),\
                (23,31), (38, 29), (14, 34), (45, 17), (9, 4), (19, 1), (36, 6), (7, 26), (46, 35), (30, 20),\
                (18, 16),(40,27), (43, 46), (42, 11), (5, 8), (10, 24), (4, 39), (47, 47), (22, 3), (11, 48), (16, 19)])

# posicao geografica das plantas
posp = np.array([(19, 24), (20, 40), (14, 23), (39, 12), (33, 43), (10, 26), (41, 18), (25, 42), (36, 33),(8, 7)])

# distancia Euclidiana entre i e j para encontrar custo unitario de transporte
c = [ [ sqrt( (posc[i][0] - posp[j][0])**2 + (posc[i][1] - posp[j][1])**2 ) for j in J ] for i in I]

# declaracao do modelo
model = Model('Problema de Localizacao',solver_name=CBC)
model.verbose = 0
# declaracao das variaveis

# variavel: igual a 1 se uma planta e instalada em j; 0, caso contrario
y = [model.add_var(var_type=BINARY) for j in J]

# variavel: proporcao da demanda do cliente i atendida pela facilidade j
x = {(i,j) : model.add_var(lb=0.0) for j in J for i in I}

# definicao da funcao objetivo
# funcao objetivo: minimizar o custo total
model.objective = minimize(xsum(f[j] * y[j] for j in J) + xsum(d[i] * c[i][j] * x[i,j] for (i,j) in product(I,J)))
# restricoes

# restricao: a demanda do cliente deve ser totalmente atendida por alguma facilidade j
# s.t. restricao_demanda{i in I}: sum{j in J} x[i,j] = 1;
for i in I:
    model += xsum(x[i,j] for j in J) == 1

# restricao: o cliente i so pode ser atendido por j, se j estiver instalado
# s.t. restricao_ativacao{i in I,j in J}: x[i,j] <= y[j];
for (i,j) in product(I,J):
    model += x[i,j] <= y[j]

# otimiza o modelo chamando o resolvedor
status = model.optimize()

# imprime solucao
if status == OptimizationStatus.OPTIMAL:
    print("Custo total de instalacao: {:12.2f}".format(sum([y[j].x * f[j] for j in J])))
    print("Custo total de transporte: {:12.2f} ".format(sum([x[i,j].x * d[i] * c[i][j] for (i,j) in product(I,J)])))
    print("Custo total : {:12.2f}.".format(model.objective_value))
    print( "facilidades : demanda : clientes ")
for j in J:
    if y[j].x > 1e-6:
        print("{:11d} : {:7.0f} : ".format(j+1,sum([x[i,j].x * d[i] for i in I])),end=' ')
        for i in I:
            if x[i,j].x > 1e-6:
                print("{:d}".format(i+1),end=' ')
        print()

fig, ax = plt.subplots()
plt.scatter(posc[:,0],posc[:,1],marker="o",color='black',s=10,label="clientes")
for i in I:
    plt.text(posc[i,0],posc[i,1], "{:d}".format(i + 1))

for (i, j) in [(i, j) for (i, j) in product(I, J) if x[(i, j)].x >= 1e-6]:
    plt.plot((posc[i][0], posp[j][0]), (posc[i][1], posp[j][1]), linestyle="--", color="black")

plt.scatter(posp[:,0],posp[:,1],marker="^",color='black',s=100,label="plantas")
for j in J:
    plt.text(posp[j][0]+.5,posp[j][1], "{:d}".format(j+1))
plt.legend()
plt.plot()
plt.savefig("exemplo_solucao.pdf")
#plt.show()

print("##################################################\n")
print("1. Problema de localização de facilidades\n")
print("##################################################\n")
print(" não estou conseguindo fazer isso direito")
sorted_distances = [sorted(set(c[i])) for i in I]
K = [range(len(sorted_distances[i])) for i in I]

m = Model('Problema de Localizacao', solver_name=CBC)
m.verbose = 0
# Decision variables
y = [m.add_var(var_type=BINARY) for j in J]
z = [[m.add_var(var_type=BINARY) for k in K[i]] for i in I]
# Objective function
m.objective = minimize(
    xsum(f[j] * y[j] for j in J) +
    xsum(
        sorted_distances[i][0] + 
        xsum((sorted_distances[i][k+1] - sorted_distances[i][k]) * z[i][k] for k in range(len(K[i])-1))
        for i in I
    )
)

# Constraints
for i in I:
    m += z[i][0] + xsum(y[j] for j in J if c[i][j] == sorted_distances[i][0]) >= 1

for i in I:
    for k in range(1, len(K[i])):
        m += z[i][k] + xsum(y[j] for j in J if c[i][j] == sorted_distances[i][k]) >= z[i][k-1]

# Optimize the model
status = m.optimize()

# Print the solution
if status == OptimizationStatus.OPTIMAL:
    print("Custo total de instalacao: {:12.2f}".format(sum([y[j].x * f[j] for j in J])))
    print("Custo total de transporte: {:12.2f}".format(sum([sorted_distances[i][0] + sum((sorted_distances[i][k+1] \
                                                                - sorted_distances[i][k]) * z[i][k].x \
                                                                for k in range(len(K[i])-1)) for i in I])))
    print("Custo total : {:12.2f}.".format(m.objective_value))
    print("facilidades : demanda : clientes ")
    for j in J:
        if y[j].x > 1e-6:
            print("{:11d} : {:7.0f} : ".format(j+1, sum([d[i] for i in I if c[i][j] == sorted_distances[i][0]])), end=' ')
            for i in I:
                if c[i][j] == sorted_distances[i][0]:
                    print("{:d}".format(i+1), end=' ')
            print()

print("##################################################\n")
print("2. Problema de atribuição generalizada\n")
print("##################################################\n")

m = 5
n = 5
bi = [10, 15, 10, 20, 10]
aij = [[2, 4, 6, 8, 10],
       [1, 3, 5, 7, 9],
       [2, 4, 6, 8, 10],
       [1, 3, 5, 7, 9],
       [2, 4, 6, 8, 10]]
cij = [[10, 20, 30, 40, 50],
       [15, 25, 35, 45, 55],
       [10, 20, 30, 40, 50],
       [15, 25, 35, 45, 55],
       [10, 20, 30, 40, 50]]
# Conjuntos
M = range(1, m + 1)  # Conjunto de funcionários
N = range(1, n + 1)  # Conjunto de tarefas
# Criar o modelo
model = Model('Alocacao de Tarefas', solver_name=CBC)
model.verbose = 0
# Variáveis de decisão
x = [[model.add_var(var_type=BINARY) for j in N] for i in M]

# Função objetivo: minimizar o custo total de atribuição
model.objective = xsum(cij[i-1][j-1] * x[i-1][j-1] for i in M for j in N)

# Restrições
# Cada tarefa j ∈ N é executada por um único funcionário i ∈ M
for j in N:
    model += xsum(x[i-1][j-1] for i in M) == 1

# Capacidade de recursos de cada funcionário i ∈ M é respeitada
for i in M:
    model += xsum(aij[i-1][j-1] * x[i-1][j-1] for j in N) <= bi[i-1]

# Resolver o modelo
status = model.optimize()

# Imprimir a solução
if status == OptimizationStatus.OPTIMAL:
    print("Custo total de atribuição: {:12.2f}".format(model.objective_value))
    print("Atribuições:")
    for i in M:
        for j in N:
            if x[i-1][j-1].x >= 0.99:  
                print(f"Funcionário {i} -> Tarefa {j}")
else:
    print("Não foi encontrada uma solução ótima.")

from mip import Model, xsum, BINARY, CBC, OptimizationStatus
print("##################################################\n")
print("3. Problema do caixeiro viajante\n")
print("##################################################\n")

n = 5  
N = range(n)  
A = [(i, j) for i in N for j in N if i != j]

cij = [[0, 10, 15, 20, 25],
       [10, 0, 35, 25, 30],
       [15, 35, 0, 30, 20],
       [20, 25, 30, 0, 15],
       [25, 30, 20, 15, 0]]

model = Model('Caixeiro Viajante', solver_name=CBC)
model.verbose = 0

x = { (i, j): model.add_var(var_type=BINARY) for i, j in A }
f = { (i, j): model.add_var() for i, j in A }

model.objective = xsum(cij[i][j] * x[i, j] for i, j in A)

for i in N:
    model += xsum(x[i, j] for j in N if i != j) == 1
    model += xsum(x[j, i] for j in N if i != j) == 1

for i in N:
    if i != 0:
        model += xsum(f[i, j] for j in N if i != j) - xsum(f[j, i] for j in N if i != j) == 1

model += xsum(f[0, j] for j in N if j != 0) == n - 1

for i, j in A:
    model += f[i, j] <= (n - 1) * x[i, j]
    model += f[i, j] >= 0

status = model.optimize()

if status == OptimizationStatus.OPTIMAL:
    print("Custo total de viagem: {:12.2f}".format(model.objective_value))
    print("Rota:")
    for i, j in A:
        if x[i, j].x >= 0.99:
            print(f"De {i} para {j}")
else:
    print("Não foi encontrada uma solução ótima.")