import math
import pulp
import time

class Data:
    def __init__(self, filename):
        self.filename = filename
        self.read_data()
        self.make_dist_matrix()

    class Node:#this is bad
        def __init__(self, id, x, y):
            self.id = id
            self.x = x
            self.y = y

    def distance(self, i, j):
        xd, yd = self.node[i].x - self.node[j].x, self.node[i].y - self.node[j].y
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

class TSPSolver:
    def __init__(self, data):
        self.data = data
        self.prob = pulp.LpProblem("TSP", pulp.LpMinimize)
        self.create_variables()
        self.create_constraints()
        self.create_objective()

    def create_variables(self):
        self.x = pulp.LpVariable.dicts('x', (range(self.data.n_node), range(self.data.n_node)), cat='Binary')
        self.y = pulp.LpVariable.dicts('y', (range(self.data.n_node), range(self.data.n_node)), lowBound=0, cat='Continuous')

    def create_constraints(self):
        for j in range(self.data.n_node):
            self.prob += pulp.lpSum(self.x[i][j] for i in range(self.data.n_node) if i != j) == 1, f"Out_{j}"
        for i in range(self.data.n_node):
            self.prob += pulp.lpSum(self.x[i][j] for j in range(self.data.n_node) if i != j) == 1, f"In_{i}"
        for i in range(self.data.n_node):
            for j in range(self.data.n_node):
                if i != j:
                    self.prob += (self.data.n_node - 1) * self.x[i][j] >= self.y[i][j], f"Delivery_{i}_{j}"
        self.prob += pulp.lpSum(self.y[j][0] for j in range(1, self.data.n_node)) + self.data.n_node == pulp.lpSum(self.y[0][j] for j in range(1, self.data.n_node)) + 1, "Initial_Delivery"
        for i in range(1, self.data.n_node):
            self.prob += pulp.lpSum(self.y[j][i] for j in range(self.data.n_node) if j != i) == pulp.lpSum(self.y[i][j] for j in range(self.data.n_node) if j != i) + 1, f"Delivery_Count_{i}"

    def create_objective(self):
        self.prob += pulp.lpSum(self.data.matrix[i][j] * self.x[i][j] for i in range(self.data.n_node) for j in range(self.data.n_node) if i != j), "Total_Distance"

    def solve(self):
        start_time = time.time()
        self.prob.solve()
        end_time = time.time()
        self.elapsed_time = end_time - start_time
        self.solution = [(i, j) for i in range(self.data.n_node) for j in range(self.data.n_node) if pulp.value(self.x[i][j]) == 1]

    def print_solution(self):
        print("Solution:")
        for i, j in self.solution:
            print(f"From city {i + 1} to city {j + 1}")
        print(f"Total cost: {pulp.value(self.prob.objective)}")

    def save_solution(self, filename):
        with open(filename, "w") as file:
            file.write("Solution:\n")
            step = 0
            current_node = 0
            visited = set()
            while len(visited) < self.data.n_node:
                for i, j in self.solution:
                    if i == current_node and j not in visited:
                        distance = self.data.matrix[i][j]
                        file.write(f"Step {step + 1}\t: Moving from node {i + 1}\t to node {j + 1}\t with distance {distance}\t\n")
                        visited.add(j)
                        current_node = j
                        step += 1
                        break
            file.write(f"Total cost: {pulp.value(self.prob.objective)}\n")
            file.write(f"Elapsed time: {self.elapsed_time:.2f} seconds\n")
        # with open(filename, "w") as file:
        #     file.write("Solution:\n")
        #     for i, j in self.solution:
        #         file.write(f"From city {i + 1} to city {j + 1}\n")
        #     file.write(f"Total cost: {pulp.value(self.prob.objective)}\n")
    def get_resullt(self, filename: str):
        return(f"File: {filename}\nTotal distance: {self.prob.objective}| Elapsed time: {self.elapsed_time}\n")

if __name__ == "__main__":
    name = "dat.dat"
    with open("TSP_optimal_solution.txt", "w") as arq:
        arq.write("Solution:\n")
    with open(name, "r") as file:
        for line in file:
            filename = line.strip()
            data = Data(filename)
            print(filename)
            solver = TSPSolver(data)
            solver.solve()
            arq.write(solver.get_resullt(filename))
        # data = Data("berlin52.tsp")
        # # data.print_distance_matrix()
        # solver = TSPSolver(data)
        # solver.solve()
        # solver.print_solution()
        # solver.save_solution("tsp_solution.txt")

