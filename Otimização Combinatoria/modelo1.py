from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpBinary, LpContinuous,GUROBI_CMD, LpStatus, LpStatusOptimal, LpStatusNotSolved, LpStatusInfeasible, LpStatusUnbounded, LpStatusUndefined
from itertools import chain, combinations
import os
import math

# Parametros
C = {
                (1, 2): 10, (1, 3): 2,  (1, 4): 4,  (1, 5): 6,  (1, 6): 2,  (1, 7): 5,  (1, 8): 3,
    (2, 1): 9,              (2, 3): 9,  (2, 4): 3,  (2, 5): 1,  (2, 6): 5,  (2, 7): 4,  (2, 8): 2,
    (3, 1): 4,  (3, 2): 5,              (3, 4): 5,  (3, 5): 6,  (3, 6): 8,  (3, 7): 9,  (3, 8): 3,
    (4, 1): 3,  (4, 2): 5,  (4, 3): 7,              (4, 5): 7,  (4, 6): 8,  (4, 7): 10, (4, 8): 5,
    (5, 1): 2,  (5, 2): 7,  (5, 3): 10, (5, 4): 8,              (5, 6): 3,  (5, 7): 1,  (5, 8): 4,
    (6, 1): 9,  (6, 2): 5,  (6, 3): 10, (6, 4): 3,  (6, 5): 7,              (6, 7): 6,  (6, 8): 7,
    (7, 1): 4,  (7, 2): 1,  (7, 3): 2,  (7, 4): 8,  (7, 5): 9,  (7, 6): 5,              (7, 8): 6,
    (8, 1): 2,  (8, 2): 3,  (8, 3): 2,  (8, 4): 6,  (8, 5): 4,  (8, 6): 2,  (8, 7): 5
}
N = list(range(1, 9))

# Função para gerar todos os subconjuntos não vazios de N
def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)))

# Conjunto S contendo todos os subconjuntos não vazios de N
# S = list(powerset(N))

def LowerBound(C, N):
    # Relaxação do problema de atribuição (AP) com saída adaptada para tratar possíveis subtours.
    model_ap = LpProblem("AP_Relaxation", LpMinimize)
    xij_ap = {(i, j): LpVariable(f"x_ap_{i}_{j}", lowBound=0,cat=LpContinuous) for i in N for j in N}

    model_ap += lpSum(C[(i, j)] * xij_ap[i, j] for i in N for j in N if i != j)
    for j in N:
        model_ap += lpSum(xij_ap[i, j] for i in N if i != j) == 1, f"ap_out_{j}"
    for i in N:
        model_ap += lpSum(xij_ap[i, j] for j in N if i != j) == 1, f"ap_into_{i}"

    
    # Subtour elimination (DFJ)
    S = list(powerset(N))
    for s in S:
        model_ap += lpSum(xij_ap[i, j] for i in s for j in s if i != j) <= len(s) - 1, f"subtour_{s}"

    model_ap.solve(GUROBI_CMD(msg=0))

    if model_ap.status == LpStatusOptimal:
        cost = model_ap.objective.value()
        # Montar mapeamento do AP: de cada nó i, encontrar j com xij_ap[i,j]==1
        mapping = {}
        for i in N:
            for j in N:
                if i != j and xij_ap[i, j].varValue > 0:
                    # print(f"x[{i},{j}]: {xij_ap[i, j].varValue}")
                    mapping[i] = j
                    break
        # Detectar ciclos (subtours)
        cycles = []
        visited_all = set()
        for i in N:
            if i not in visited_all:
                cycle = []
                current = i
                while current not in cycle:
                    cycle.append(current)
                    visited_all.add(current)
                    current = mapping[current]
                cycles.append(cycle)

        # Se houver apenas um ciclo, ele é um tour completo
        if len(cycles) == 1 and len(cycles[0]) == len(N):
            tour = cycles[0] + [cycles[0][0]]
            return cost, tour
        else:
            # Retorna a lista de subtours com aviso
            # print("Aviso: A solução da relaxação AP contém subtours:", cycles)
            return cost, cycles
    else:
        return None, []

def ExactAlgorithm(C, N):
    # Algoritmo exato (DFJ) para ATSP encapsulado em função
    model_exact = LpProblem("ATSP_Exact", LpMinimize)
    xij_exact = {(i, j): LpVariable(f"x_exact_{i}_{j}", 0, 1, LpBinary) for i in N for j in N if i != j}
    
    # Restrições de fluxo
    for j in N:
        model_exact += lpSum(xij_exact[i, j] for i in N if i != j) == 1, f"out_{j}"
    for i in N:
        model_exact += lpSum(xij_exact[i, j] for j in N if i != j) == 1, f"into_{i}"
    
    # Subtour elimination (DFJ)
    S = list(powerset(N))
    for s in S:
        model_exact += lpSum(xij_exact[i, j] for i in s for j in s if i != j) <= len(s) - 1, f"subtour_{s}"
    
    # Objetivo
    model_exact += lpSum(C[(i, j)] * xij_exact[i, j] for i in N for j in N if i != j)
    
    model_exact.solve(GUROBI_CMD(msg=0))
    
    if model_exact.status == LpStatusOptimal:
        cost = model_exact.objective.value()
        tour = []
        visited = set()
        current = N[0]
        while len(visited) < len(N):
            tour.append(current)
            visited.add(current)
            for j in N:
                if current != j and xij_exact[current, j].varValue > 0:
                    current = j
                    break
        tour.append(tour[0])
        return cost, tour
    else:
        return None, []

def UpperBound(C, N):
    # Heurística do vizinho mais próximo para obter um upperbound
    start = N[0]
    tour = [start]
    visited = {start}
    total_cost = 0
    current = start
    while len(visited) < len(N):
        next_node = None
        min_cost = float('inf')
        for j in N:
            if j not in visited and (current, j) in C:
                if C[(current, j)] < min_cost:
                    min_cost = C[(current, j)]
                    next_node = j
        if next_node is None:
            break  # Caso não haja próximo nó disponível
        tour.append(next_node)
        visited.add(next_node)
        total_cost += min_cost
        current = next_node
    if (current, start) in C:
        total_cost += C[(current, start)]
        tour.append(start)
    return total_cost, tour

class Data:
    def __init__(self, filename):
        self.filename = filename
        self.read_data()
        self.make_dist_matrix()

    class Node:
        def __init__(self, id, x, y):
            self.id = id
            self.x = x
            self.y = y

    def distance(self, i, j):
        xd = self.node[i].x - self.node[j].x
        yd = self.node[i].y - self.node[j].y
        if self.edge_weight_type == "EUC_2D":
            return int(math.sqrt(xd * xd + yd * yd))
        else:
            rij = math.sqrt((xd * xd + yd * yd) / 10.0)
            tij = int(rij)
            return tij + 1 if tij < rij else tij

    def read_data(self):
        with open(self.filename, "r") as file:
            for line in file:
                if line.startswith("EDGE_WEIGHT_TYPE"):
                    self.edge_weight_type = line.split(":")[1].strip()
                elif line.startswith("DIMENSION"):
                    self.n_node = int(line.split(":")[1].strip())
                    self.node = [None] * self.n_node
                elif line.startswith("NODE_COORD_SECTION"):
                    for i in range(self.n_node):
                        parts = next(file).split()
                        self.node[i] = self.Node(int(parts[0]), float(parts[1]), float(parts[2]))

    def make_dist_matrix(self):
        self.matrix = [[self.distance(i, j) for j in range(self.n_node)] for i in range(self.n_node)]

    def print_distance_matrix(self):
        print("Distance Matrix:")
        print("    ", end="")
        for i in range(self.n_node):
            print(f"{i + 1:4}", end=" ")
        print("\n   +" + "-----" * self.n_node)
        for i in range(self.n_node):
            print(f"{i + 1:2} |", end=" ")
            for j in range(self.n_node):
                print(f"{self.matrix[i][j]:4}", end=" ")
            print()

    def get_distance_dict(self):
        dist_dict = {}
        for i in range(self.n_node):
            for j in range(self.n_node):
                dist_dict[(i + 1, j + 1)] = self.matrix[i][j]
        return dist_dict

def process_data_files():
    data_folder = r"C:\Users\tastc\Desktop\Trabalhos_UFMG\Otimização Combinatoria\Data"
    for filename in os.listdir(data_folder):
        if filename.lower().endswith((".tsp", ".txt")):
            filepath = os.path.join(data_folder, filename)
            print(f"Processing file: {filename}")
            data_instance = Data(filepath)
            C = data_instance.get_distance_dict()
            N = list(range(1, data_instance.n_node + 1))
            ex_cost, ex_tour = multiCommodity(C, N)
            print("Exact Algorithm: cost =", ex_cost, "tour =", ex_tour)
            ub_cost, ub_tour = UpperBound(C, N)
            print("Upper Bound: cost =", ub_cost, "tour =", ub_tour)
            lb_cost, lb_tour = multiCommodity(C, N, False)
            print("Lower Bound: cost =", lb_cost, "tour =", lb_tour)
            print("-" * 40)

def multiCommodity(C, N, relaxation=False):
    # Algoritmo multi-commodity para ATSP com formulação CLAUS (n - 1 commodities)
    model_exact = LpProblem("multiCommodity", LpMinimize)
    
    xij = {(i, j): LpVariable(f"x__{i}_{j}", 0, 1, LpBinary) for i in N for j in N if i != j}
    if relaxation:
        # Criar variáveis contínuas para arcos (i,j) para relaxação
        xij = {(i, j): LpVariable(f"x__{i}_{j}", lowBound=0, upBound=1, cat=LpContinuous) for i in N for j in N if i != j}

    # Criar variáveis contínuas para commodities k = 2,...,n para cada arco (i,j)
    wkij = {(i, j, k): LpVariable(f"w_{i}_{j}_{k}", lowBound=0, cat=LpContinuous)
                for i in N for j in N if i != j for k in N if k != 1}
    
    # Objetivo
    model_exact += lpSum(C[(i, j)] * xij[i, j] for i in N for j in N if i != j)
    
    # Restrições de fluxo
    for j in N:
        model_exact += lpSum(xij[i, j] for i in N if i != j) == 1, f"out_{j}"
    for i in N:
        model_exact += lpSum(xij[i, j] for j in N if i != j) == 1, f"into_{i}"
    
    # Restrições CLAUS:
    # (13) para i,k = 2,...,n, com i ≠ k: sum_{j≠i} w_{i,j}^k - sum_{j≠i} w_{j,i}^k = 0
    for k in N:
        for i in N:
            if i != k and k != 1:
                model_exact += (lpSum(wkij[i, j, k] for j in N if j != i)
                                - lpSum(wkij[j, i, k] for j in N if j != i)) == 0, f"claus13_{i}_{k}"
        
    # (14) para k = 2,...,n: sum_{j≠1} w_{1,j}^k - sum_{j≠1} w_{j,1}^k = 1
    for k in N:
        if k != 1:
            model_exact += (lpSum(wkij[1, j, k] for j in N if j != 1)
                            - lpSum(wkij[j, 1, k] for j in N if j != 1)) == -1, f"claus14_{k}"
        
    # (15) para i = 2,...,n: sum_{j≠i} w_{i,j}^i - sum_{j≠i} w_{j,i}^i = 1
    for i in N:
        if i!=1:
            model_exact += (lpSum(wkij[i, j, i] for j in N if j != i)
                            - lpSum(wkij[j, i, i] for j in N if j != i)) == 1, f"claus15_{i}"
        
    # (16) para todos (i, j, k): w_{i,j}^k ≤ x_{ij}
    for i in N:
        for j in N:
            for k in N:
                if i != j and k != 1:
                    model_exact += wkij[i, j, k] <= xij[i, j], f"claus16_{i}_{j}_{k}"

    
    model_exact.solve(GUROBI_CMD())
    if model_exact.status == LpStatusOptimal:
        cost = model_exact.objective.value()
        tour = []
        visited = set()
        current = N[0]
        while len(visited) < len(N):
            tour.append(current)
            visited.add(current)
            for j in N:
                if current != j and xij[current, j].varValue > 0:
                    current = j
                    break
        tour.append(tour[0])
        return cost, tour
    else:
        return None, []
if __name__ == '__main__':
    # ex_cost, ex_tour = ExactAlgorithm(C, N)
    # print("Solução Ótima Custo:", ex_cost)
    # print("Solução Ótima Caminho:", " -> ".join(map(str, ex_tour)))
    # ub_cost, ub_tour = UpperBound(C, N)
    # print("Upper Bound Custo:", ub_cost)
    # print("Upper Bound Caminho:", " -> ".join(map(str, ub_tour)))
    # lb_cost, lb_tour = LowerBound(C, N)
    # print("Lower Bound Custo:", lb_cost)
    # print("Lower Bound Caminho:", " -> ".join(map(str, lb_tour)))
    
    # process_data_files()
    
    multiCommodity(C, N)