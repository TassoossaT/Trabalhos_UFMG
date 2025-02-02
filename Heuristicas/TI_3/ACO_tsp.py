import numpy as np
import math

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

class ACO:
    def __init__(self, num_ants, num_iterations, decay, alpha=1, beta=1):
        self.num_ants = num_ants
        self.num_iterations = num_iterations
        self.decay = decay
        self.alpha = alpha
        self.beta = beta

    def initialize_pheromone(self, num_cities):
        return np.ones((num_cities, num_cities))

    def update_pheromone_AS(self, pheromone, ants, Q):
        for i in range(len(pheromone)):
            for j in range(len(pheromone)):
                pheromone[i][j] *= (1 - self.decay)
                for ant in ants:
                    pheromone[i][j] += ant.pheromone_delta[i][j]

    def update_pheromone_MMAS(self, pheromone, best_ant, smin, smax):
        for i in range(len(pheromone)):
            for j in range(len(pheromone)):
                pheromone[i][j] = max(min((1 - self.decay) * pheromone[i][j] + best_ant.pheromone_delta[i][j], smax), smin)

    def update_pheromone_ACS(self, pheromone, ant, u, s0):
        for i in range(len(pheromone)):
            for j in range(len(pheromone)):
                if ant.visited[i][j]:
                    pheromone[i][j] = (1 - self.decay) * pheromone[i][j] + u * s0

    def run(self, data):
        num_cities = data.n_node
        pheromone = self.initialize_pheromone(num_cities)
        best_ant = None

        for iteration in range(self.num_iterations):
            ants = [Ant(self, num_cities) for _ in range(self.num_ants)]
            for ant in ants:
                ant.find_tour(data.matrix, pheromone)
                if best_ant is None or ant.tour_length < best_ant.tour_length:
                    best_ant = ant
                    # print(ant.tour_length, best_ant.tour_length)

            self.update_pheromone_AS(pheromone, ants, Q=1)
            # Uncomment the following line to use MMAS
            # self.update_pheromone_MMAS(pheromone, best_ant, smin=0.1, smax=10)
            # Uncomment the following line to use ACS
            # self.update_pheromone_ACS(pheromone, best_ant, u=0.1, s0=1)
        # print(best_ant.tour, best_ant.tour_length)
        return best_ant.tour_length

class Ant:
    def __init__(self, aco, num_cities):
        self.aco = aco
        self.num_cities = num_cities
        self.tour = []
        self.tour_length = 0
        self.pheromone_delta = np.zeros((num_cities, num_cities))
        self.visited = np.zeros((num_cities, num_cities), dtype=bool)

    def find_tour(self, graph, pheromone):
        self.tour = [np.random.randint(self.num_cities)]
        while len(self.tour) < self.num_cities:
            next_city = self.select_next_city(graph, pheromone)
            self.tour.append(next_city)
            self.visited[self.tour[-2]][next_city] = True
        self.tour_length = self.calculate_tour_length(graph)
        # print(self.tour_length)
        self.update_pheromone_delta()

    def select_next_city(self, graph, pheromone):
        current_city = self.tour[-1]
        probabilities = []
        for city in range(self.num_cities):
            if city not in self.tour:
                probabilities.append((pheromone[current_city][city] ** self.aco.alpha) *
                                     ((1 / graph[current_city][city]) ** self.aco.beta))
            else:
                probabilities.append(0)
        probabilities = np.array(probabilities)
        probabilities /= probabilities.sum()
        return np.random.choice(range(self.num_cities), p=probabilities)

    def calculate_tour_length(self, graph):
        length = 0
        for i in range(len(self.tour) - 1):
            length += graph[self.tour[i]][self.tour[i + 1]]
        length += graph[self.tour[-1]][self.tour[0]]
        # print(length)
        return length

    def update_pheromone_delta(self):
        for i in range(len(self.tour) - 1):
            self.pheromone_delta[self.tour[i]][self.tour[i + 1]] = 1 / self.tour_length
        self.pheromone_delta[self.tour[-1]][self.tour[0]] = 1 / self.tour_length
    
if __name__ == "__main__":
    import time
    name = "dat.dat"
    with open("TSP_ACO_solution.txt", "w") as arq:
        arq.write("Solution:\n")
        with open(f'Data/{name}', "r") as file:
            for line in file:
                filename = line.strip()
                data = Data(f'Data/{filename}')
                print(filename)
                aco = ACO(num_ants=50 , num_iterations=1000, decay=0.5, alpha=1, beta=2)
                start_time = time.time()
                best_cost = aco.run(data)
                elapsed_time = time.time() - start_time
                result = f"File: {filename} | Total distance: {best_cost} | Elapsed time: {elapsed_time} seconds\n"
                arq.write(result)
