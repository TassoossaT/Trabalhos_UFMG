import math
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

class TSPSolverVND:
    def __init__(self, data):
        self.data = data
        self.best_route = None
        self.best_cost = float('inf')
        self.time: time = None

    def solve(self):
        start_time = time.time()
        initial_route = list(range(self.data.n_node))
        self.best_route = initial_route
        self.best_cost = self.route_cost(initial_route)
        improved = True
        while improved:
            improved = False
            for neighborhood in [self.swap, self.two_opt, self.insert]:
                new_route, new_cost = neighborhood(self.best_route)
                if new_cost < self.best_cost:
                    self.best_route = new_route
                    self.best_cost = new_cost
                    # self.print_solution()
                    improved = True
                    end_time = time.time()
                    self.time = end_time - start_time
                    break
    def route_cost(self, route):
        return sum(self.data.matrix[route[i]][route[i + 1]] for i in range(len(route) - 1)) + self.data.matrix[route[-1]][route[0]]

    def swap(self, route):
        best_route = route[:]
        best_cost = self.route_cost(route)
        for i in range(len(route) - 1):
            for j in range(i + 1, len(route)):
                new_route = route[:]
                new_route[i], new_route[j] = new_route[j], new_route[i]
                new_cost = self.route_cost(new_route)
                if new_cost < best_cost:
                    best_route = new_route
                    best_cost = new_cost
        return best_route, best_cost

    def two_opt(self, route):
        best_route = route[:]
        best_cost = self.route_cost(route)
        for i in range(len(route) - 1):
            for j in range(i + 1, len(route)):
                new_route = route[:i] + route[i:j + 1][::-1] + route[j + 1:]
                new_cost = self.route_cost(new_route)
                if new_cost < best_cost:
                    best_route = new_route
                    best_cost = new_cost
        return best_route, best_cost

    def insert(self, route):
        best_route = route[:]
        best_cost = self.route_cost(route)
        for i in range(len(route)):
            for j in range(len(route)):
                if i != j:
                    new_route = route[:]
                    node = new_route.pop(i)
                    new_route.insert(j, node)
                    new_cost = self.route_cost(new_route)
                    if new_cost < best_cost:
                        best_route = new_route
                        best_cost = new_cost
        return best_route, best_cost

    def get_resullt(self,filename):
        return f"File: {filename} | Total distance: {solver.best_cost} | Elapsed time: {self.time} seconds\n"

if __name__ == "__main__":
    name = "dat.dat"
    with open("TSP_VND_solution.txt", "w") as arq:
        arq.write("Solution:\n")
        with open(f'Data/{name}', "r") as file:
            for line in file:
                filename = line.strip()
                data = Data(f'Data/{filename}')
                print(filename)
                solver = TSPSolverVND(data)
                solver.solve()
                arq.write(solver.get_resullt(filename))