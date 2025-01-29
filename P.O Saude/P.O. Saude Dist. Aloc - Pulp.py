from pulp import LpProblem, lpSum, LpMinimize, LpMaximize, LpVariable, LpBinary, PULP_CBC_CMD

class Set_Covering:
    '''
    Set-covering [Ahmadi-Javid et al., 2017]

    I : The set of demand points.
    J : The set of candidate locations for Health Care Unit (HCU)
    ▶dij The travel time from demand point i ∈ I to candidate location j ∈ J.
    ▶Di The maximum acceptable travel time from demand i ∈ I (the cover time).
    Ni = {j ∈ J : dij ≤ Di} : Set of all candidate locations that can cover demand i.
    ▶fj The fixed cost of locating HCU at candidate location j ∈ J.
    ▶xj ∈ {0, 1} 1, if a facility is located at candidate location j ∈ J; 0 otherwise.

    '''
    # Contruction = takes the data
    def __init__(self,I,J,d,D,f):
        self.set_data(I,J,d,D,f)
    def set_data(self,I,J,d,D,f):
        self.I  = I
        self.J  = J
        self.d  = {(I[i],J[j]): d[i][j] for i in range(len(self.I)) for j in range(len(self.J))}
        self.D  = {I[i]: D[i] for i in range(len(I))}
        self.f  = {J[j]: f[j] for j in range(len(J))}
        self.N  = {(i): [j for j in J if self.d[i,j] <= self.D[i]] for i in I}
    # create the model 
    def model(self):
        I,J,f,N = self.I,self.J,self.f,self.N
        # Create the model
        model = LpProblem("Set-covering", LpMinimize)
        # model.isMIP
        # Variable
        x = {j: LpVariable(f"x{j}", cat=LpBinary) for j in J}
        model.objective= lpSum(f[j] * x[j] for j in J)
        # Restrictions
        for i in I:
            model += lpSum(x[j] for j in N[i]) >= 1

        # Solver
        self._model = model
        self.x = x
        model.solve(PULP_CBC_CMD(msg=False))
    
    def print_solution(self):
        model = self._model
        I, J, d, f, N = self.I, self.J, self.d, self.f, self.N

        print("===========================================")
        print("Set Covering")
        print(f"Total Cost: {model.objective.value()}\n")
        print("===========================================")
        for i in I:
            for j in N[i]:
                if self.x[j].varValue > 0.5:
                    print(f"{i}\t--> [{j}]:\t {d[i,j]:.2f} km ($ {f[j]:.2f})")
        print("===========================================\n")

class Maximal_Covering:
    '''
    Maximal covering [Ahmadi-Javid et al., 2017]

    I : The set of demand points.
    J : The set of candidate locations for Health Care Unit (HCU)
    ▶ dij The travel time from demand point i ∈ I to candidate location j ∈ J.
    ▶ Di The maximum acceptable travel time from demand i ∈ I (the cover time).
    Ni = {j ∈ J : dij ≤ Di} : Set of all candidate locations that can cover demand i.
    ▶ wi The demand point at i ∈ I.
    ▶ p The number of candidate locations to be established.
    ▶ xj ∈ {0, 1} 1, if a facility is located at candidate location j ∈ J; 0 otherwise.
    ▶ zi ∈ {0, 1} 1, if demand point i ∈ I is covered; 0 otherwise.
    '''
    
    def __init__(self, I,J,d,D,w,p):
        self.set_data(I,J,d,D,w,p)
    def set_data(self, I,J,d,D,w,p):
        self.I  = I
        self.J  = J
        self.d  = {(I[i],J[j]): d[i][j] for i in range(len(self.I)) for j in range(len(self.J))}
        self.D  = {I[i]: D[i] for i in range(len(I))}
        self.w  = {I[i]: w[i] for i in range(len(I))}
        self.p  = p
        self.N  = {i: [j for j in J if self.d[i,j] <= self.D[i]] for i in I}
    def model(self):
        I,J,w,p,N = self.I,self.J,self.w,self.p,self.N
        
        model = LpProblem("Maximal covering", LpMaximize)
        
        x = {j: LpVariable(f"x{j}", cat=LpBinary) for j in J}
        z = {i: LpVariable(f"z{i}", cat=LpBinary) for i in I}

        model += lpSum(w[i]*z[i] for i in I)

        model += lpSum(x[j] for j in J) == p
        for i in I:
            model += lpSum(x[j] for j in N[i]) >= z[i]
        # Resolução do modelo
        self._model = model
        self.x,self.z = x,z
        
        model.solve(PULP_CBC_CMD(msg=False))
    
    def print_solution(self):
        model = self._model
        I, J, d, N = self.I, self.J, self.d, self.N
        print("===========================================")
        print("Maximal Covering")
        print(f"Total Covered Demand: {model.objective.value():.2f}\n")
        print(f"Selected Locations: {sum(self.x[j].value() for j in J)}")
        print("===========================================")
        for i in I:
            for j in N[i]:
                if self.x[j].value() > 0.5:
                    print(f"[{i}] is covered by [{j}]: {d[i,j]:.2f} km")
        print("===========================================\n")

class P_Center:
    '''
    P-center [Ahmadi-Javid et al., 2017]

    I : The set of demand points.
    J : The set of candidate locations for Health Care Unit (HCU)
    ▶ dij The travel time from demand point i ∈ I to candidate location j ∈ J.
    ▶ Di The maximum acceptable travel time from demand i ∈ I (the cover time).
    Ni = {j ∈ J : dij ≤ Di} : Set of all candidate locations that can cover demand i.
    ▶ wi The demand point at i ∈ I.
    ▶ p The number of candidate locations to be established.
    ▶ xj ∈ {0, 1} 1, if a facility is located at candidate location j ∈ J; 0 otherwise.
    ▶ yij ∈ {0, 1} 1, if demand point i is assigned to a facility at candidate location
    j ∈ Ni; 0 otherwise.
    ▶ L ≥ 0 L is an auxiliary variable (not a decision variable) that is used to compute
    the maximum distance.
    '''
    def __init__(self,I,J,d,D,w,p):
        self.set_data(I,J,d,D,w,p)
    def set_data(self,I,J,d,D,w,p):
        self.I  = I
        self.J  = J
        self.d  = {(I[i],J[j]): d[i][j] for i in range(len(self.I)) for j in range(len(self.J))}
        self.D  = {I[i]: D[i] for i in range(len(I))}
        self.w  = {I[i]: w[i] for i in range(len(I))}
        self.p  = p
        self.N  = {i: [j for j in J if self.d[i,j] <= self.D[i]] for i in I}
    
    def model(self):
        I,J,d,w,p,N = self.I,self.J,self.d,self.w,self.p,self.N
        
        model = LpProblem("P-center", LpMinimize)

        L = LpVariable("L")

        x = {j: LpVariable(f"x{j}", cat=LpBinary) for j in J}
        y = {(i, j): LpVariable(f"y{i}{j}", cat=LpBinary) for i in I for j in N[i]}

        model.objective = L

        # Constraint (10): Each demand point i must be assigned to exactly one facility j
        for i in I:
            model += lpSum(y[i,j] for j in N[i]) == 1

        # Constraint (11): Exactly p facilities must be established
        model += lpSum(x[j] for j in J) == p

        # Constraint (12): The weighted travel time for each demand point i must be less than or equal to L
        for i in I:
            model += lpSum(w[i] * d[i,j] * y[i,j] for j in N[i]) <= L

        # Constraint (13): A demand point i can only be assigned to a facility j if that facility is established
        for i in I:
            for j in N[i]:
                model += y[i,j]  <= x[j]

        self._model = model
        self.x,self.y=x,y
        model.solve(PULP_CBC_CMD(msg=False))
    
    def print_solution(self):
        model = self._model
        I, J, d, N = self.I, self.J, self.d, self.N
        print("===========================================")
        print("P Center")
        print(f"Maximum Distance: {model.objective.value():.2f}\n")
        print(f"Selected Locations: {sum(self.x[j].value() for j in J)}")
        print("===========================================")
        for i in I:
            for j in N[i]:
                if self.y[i,j].value() > 0.5:
                    print(f"[{i}] is assigned to [{j}]: {d[i,j]:.2f} km")
        print("===========================================\n")

class P_Median:
    '''
    P-median [Ahmadi-Javid et al., 2017]

    I : The set of demand points.
    J : The set of candidate locations for Health Care Unit (HCU)
    ▶ dij The travel time from demand point i ∈ I to candidate location j ∈ J.
    ▶ wi The demand point at i ∈ I.
    ▶ p The number of candidate locations to be established.
    ▶ xj ∈ {0, 1} 1, if a facility is located at candidate location j ∈ J; 0 otherwise.
    ▶ yij ∈ {0, 1} 1, if demand point i is assigned to a facility at candidate location
    j ∈ Ni; 0 otherwise.
    '''
    def __init__(self,I,J,d,w,p) -> None:
        self.set_data(I,J,d,w,p)
    def set_data(self,I,J,d,w,p):
        self.I  = I
        self.J  = J
        self.d  = {(I[i],J[j]): d[i][j] for i in range(len(self.I)) for j in range(len(self.J))}
        self.w  = {I[i]: w[i] for i in range(len(I))}
        self.p  = p
    
    def model(self):
        I, J, d, w, p = self.I, self.J, self.d, self.w, self.p

        model = LpProblem("P-median", LpMinimize)
        

        x = {j: LpVariable(f"x{j}", cat=LpBinary) for j in J}
        y = {(i,j): LpVariable(f"y{i}{j}", cat=LpBinary) for j in J for i in I}

        # Objective function: minimize the weighted travel time
        model.objective = lpSum(w[i] * d[i,j] * y[i,j] for i in I for j in J)

        # Constraint (18): Each demand point i must be assigned to exactly one facility j
        for i in I:
            model += lpSum(y[i,j] for j in J) == 1

        # Constraint (19): Exactly p facilities must be established
        model += lpSum(x[j] for j in J) == p

        # Constraint (20): A demand point i can only be assigned to a facility j if that facility is established
        for i in I:
            for j in J:
                model += y[i,j] <= x[j]
        self.x,self.y=x,y
        self._model = model
        model.solve(PULP_CBC_CMD(msg=False))
    
    def print_solution(self):
        model = self._model
        I, J, d, w, p = self.I, self.J, self.d, self.w, self.p
        print("===========================================")
        print("P Median")
        print(f"total demand-weighted distance: {model.objective.value():.2f}")
        print("\nSelected Locations:")
        for j in J:
            if self.x[j].value() > 0.5:  # Verifica se a instalação foi selecionada
                print(f"Facility {j} is selected")
        print("===========================================")
        for i in I:
            for j in J:
                if self.y[i,j].value() > 0.5:  # Verifica se a demanda foi atribuída à instalação
                    print(f"[{i}]\tis assigned to [{j}]: {d[i,j]:.2f} km")
        print("===========================================")

class Fixed_Charge:
    '''
    Fixed-charge [Ahmadi-Javid et al., 2017]

    I : The set of demand points.
    J : The set of candidate locations for Health Care Unit (HCU)
    ▶ dij The travel time from demand point i ∈ I to candidate location j ∈ J.
    ▶ fj Fixed charge of establishing a facility at candidate location j ∈ J.
    ▶ v Variable transportation cost per item per distance unit.
    ▶ Uj facility Capacity (In a capacitated Fixed-charge Location Problem).
    ▶ xj ∈ {0, 1} 1, if a facility is located at candidate location j ∈ J; 0 otherwise.
    ▶ yij ∈ {0, 1} 1, if demand point i is assigned to a facility at candidate location
    j ∈ Ni; 0 otherwise.
    '''
    def __init__(self, I,J,d,f,v,U,w):
        self.set_data(I,J,d,f,v,U,w)
    def set_data(self, I,J,d,f,v,U,w):
        self.I  = I
        self.J  = J
        self.d  = {(I[i],J[j]): d[i][j] for i in range(len(self.I)) for j in range(len(self.J))}
        self.f  = {J[j]: f[j] for j in range(len(J))}
        self.v  = v
        self.U  = {J[j]: U[j] for j in range(len(J))}
        self.w  = {I[i]: w[i] for i in range(len(I))}
        
    def model(self):
        I,J,d,f,v,U,w = self.I,self.J,self.d,self.f,self.v,self.U,self.w

        model = LpProblem("Fixed-charge", LpMinimize)
        

        x = {j:     LpVariable(f"x{j}", cat=LpBinary) for j in J}
        y = {(i,j): LpVariable(f"y{i}{j}", cat=LpBinary) for j in J for i in I}

        # Objective function: minimize the fixed charge and variable transportation cost
        model.objective = lpSum(f[j] * x[j] for j in J) + lpSum(v * w[i] * d[i,j] * y[i,j] for i in I for j in J)

        # Constraint (24): Each demand point i must be assigned to exactly one facility j
        for i in I:
            model += lpSum(y[i,j] for j in J) == 1

        # Constraint (25): A demand point i can only be assigned to a facility j if that facility is established
        for i in I:
            for j in J:
                model += y[i,j] <= x[j]

        # Constraint (26): The total demand assigned to each facility j must not exceed its capacity
        for j in J:
            model += lpSum(w[i] * y[i,j] for i in I) <= U[j]
        self.x,self.y=x,y
        self._model = model
        model.solve(PULP_CBC_CMD(msg=False))
    def print_solution(self):
        model = self._model
        I, J, d = self.I, self.J, self.d
        print("===========================================")
        print("Fixed Charge")
        print(f"total fixed and variable costs: {model.objective.value():.2f}\n")
        print(f"Selected Locations: {sum(self.x[j].value() for j in J)}")
        print("===========================================")
        for i in I:
            for j in J:
                if self.y[i,j].value() > 0.5:
                    print(f"[{i}]\tis assigned to [{j}]: {d[i,j]:.2f} km")
        print("===========================================\n")

class Hierarchical:
    '''
    Hierarchical [Ahmadi-Javid et al., 2017]

    I : The set of demand points.
    K : The set of candidate locations for a level-1 PCF (e.g., clinics).
    J : The set of candidate locations for a level-2 PCF (e.g., hospitals).
    ▶ d1ik The travel time from demand point i ∈ I to a level-1 PCF in a candidate
    location k ∈ K.
    ▶ d2kj The travel time from a level-1 PCF in a candidate location k ∈ K and a
    level-2 PCF in a candidate location j ∈ J.
    ▶ wi The population size, demand point at i ∈ I.
    ▶ p The number of a level-1 PCF locations to be established.
    ▶ q The number of a level-2 PCF locations to be established.
    ▶ C1k The capacity of a level-1 PCF in candidate location k ∈ K.
    ▶ C2j The capacity of a level-2 PCF in candidate location j ∈ J
    ▶ Ok Proportion of level-1 PCF patients at candidate location k ∈ K
    referred to a level-2 PCF.

    x1k ∈ {0, 1} 1, if a level-1 PCF is established at candidate location k ∈ K; 0
    otherwise.
    ▶ x2j ∈ {0, 1} 1, if a level-2 PCF is established at candidate location j ∈ J; 0
    otherwise.
    ▶ uik The flow of patients between demand point i ∈ I and a level-1 PCF at
    candidate location k ∈ K
    ▶ vkj The flow of patients between demand point k ∈ K and a level-2 PCF at
    candidate location j ∈ J
    '''
    def __init__(self,I,J,K,d1ik,d2kj,w,p,q,C1,C2,O):
        self.set_data(I,J,K,d1ik,d2kj,w,p,q,C1,C2,O)
    def set_data(self,I,J,K,d1ik,d2kj,w,p,q,C1,C2,O):
        self.I      =  I
        self.J      =  J
        self.K      =  K
        self.d1ik   =  {(I[i], K[k]): d1ik[i][k] for i in range(len(I)) for k in range(len(K))}
        self.d2kj   =  {(K[k], J[j]): d2kj[k][j] for k in range(len(K)) for j in range(len(J))}
        self.w      =  {I[i]: w[i] for i in range(len(I))}
        self.p      =  p
        self.q      =  q
        self.C1     =  {K[k]: C1[k] for k in range(len(K))}
        self.C2     =  {J[j]: C2[j] for j in range(len(J))}
        self.O      =  {K[k]: O[k]  for k in range(len(K))}      
    def model(self):
        I,J,K=self.I,self.J,self.K
        d1ik,d2kj,w,p,q,C1,C2,O=self.d1ik,self.d2kj,self.w,self.p,self.q,self.C1,self.C2 ,self.O
    
        model = LpProblem("Hierarchical", LpMinimize)
        

        x1 = {k:    LpVariable(f"x1{k}", cat=LpBinary) for k in K}
        x2 = {j:    LpVariable(f"x2{j}", cat=LpBinary) for j in J}
        u  = {(i,k):LpVariable(f"u{i}{k}",lowBound=0) for k in K for i in I}
        v  = {(k,j):LpVariable(f"v{k}{j}",lowBound=0) for j in J for k in K}

        # Objective function: minimize the travel time
        model.objective = lpSum(d1ik[i,k] * u[i,k] for i in I for k in K) + lpSum(d2kj[k,j] * v[k,j] for k in K for j in J)

        # Constraint (29): Each demand point i must be assigned to exactly one level-1 PCF k
        for i in I:
            model += lpSum(u[i,k] for k in K) == w[i]

        # Constraint (30): The flow of patients from level-1 PCF k to level-2 PCF j
        for k in K:
            model += lpSum(v[k,j] for j in J) == O[k] * lpSum(u[i,k] for i in I)

        # Constraint (31): The total demand assigned to each level-1 PCF k must not exceed its capacity
        for k in K:
            model += lpSum(u[i,k] for i in I) <= C1[k] * x1[k]

        # Constraint (32): The total demand assigned to each level-2 PCF j must not exceed its capacity
        for j in J:
            model += lpSum(v[k,j] for k in K) <= C2[j] * x2[j]

        # Constraint (33): Exactly p level-1 PCF locations must be established
        model += lpSum(x1[k] for k in K) == p

        # Constraint (34): Exactly q level-2 PCF locations must be established
        model += lpSum(x2[j] for j in J) == q
        
        self._model = model
        self.x1,self.x2,self.u,self.v=x1,x2,u,v
        model.solve(PULP_CBC_CMD(msg=False))
    def print_solution(self):
        I, J, K, = self.I, self.J, self.K
        model = self._model
        if model.status:
            print("Optimal solution found.")
            print("===========================================")
            print("Hierarchical")
            print(f"Total Cost: {model.objective.value():.2f}\n")
            print(f"Selected Level-1 PCF Locations: {sum(self.x1[k].value() for k in K)}")
            print(f"Selected Level-2 PCF Locations: {sum(self.x2[j].value() for j in J)}")
            print("===========================================")
            for k in K:
                if self.x1[k].value() > 0.5:
                    print(f"Level-1 PCF at \t{k}\t covers:")
                    covered_demands = [i for i in I if self.u[i,k].value() > 0.5]
                    print(f"  Demand points covered: {', '.join(covered_demands)}")
            print("===========================================")
            for j in J:
                if self.x2[j].value() > 0.5:
                    print(f"Level-2 PCF at {j}")
            print("===========================================\n")
        else:
            print("No optimal solution found.")
        
if __name__ == "__main__":
    #exemple
    I = ["A", "B", "C", "D", "E", "F", "G", "H", "J", "T"]  # 10 demand points
    J = ["D",'E','F','G','H']  # 5 candidate locations
    K = ["D",'E','F','G','H']
    d = [
        [71, 81, 100, 93, 94],
        [63, 55, 51, 68, 44],
        [49, 55, 56, 67, 88],
        [38, 69, 55, 48, 66],
        [90, 76, 86, 47, 52],
        [52, 78, 52, 72, 32],
        [64, 40, 73, 85, 57],
        [72, 84, 59, 97, 77],
        [66, 76, 98, 66, 95],
        [74, 100, 80, 66, 77]
    ]
    
    D = [76,79,79,75,79,79,80,78,80,75]
    f = [16,61,23,14,5,91,68,11,21,26]
    w = [53,47,42,49,46,35,50,47,52,36]
    p = 4
    q = 2
    v = 1
    U = [254,190,189,191,131]
    d1ik = [
        [35,44,	98,	87,	61],
        [70,91,	84,	77,	95],
        [86,89,	30,	63,	91],
        [57,98,	90,	95,	85],
        [79,99,	45,	41,	99],
        [62,68,	79,	42,	70],
        [61,69,	79,	52,	77],
        [84,89,	50,	57,	42],
        [74,40,	49,	91,	41],
        [59,37,	39,	50,	64]]
    d2kj = [
        [43	,38,82],
        [54	,71,59],
        [100,78,68],
        [59	,96,58],
        [38	,66,50]]
    C1 = [148,132,163,140,158]
    C2 = [257,244,253,342,123]
    O = [1.0,0.7,0.8,0.8,0.5]

    # # Set Covering
    set_covering = Set_Covering(I,J,d,D,f)
    set_covering.model()
    set_covering.print_solution()

    # Maximal Covering
    maximal_covering = Maximal_Covering(I,J,d,D,w,p)
    maximal_covering.model()
    maximal_covering.print_solution()

    # P-Center
    p_center = P_Center(I,J,d,D,w,p)
    p_center.model()
    p_center.print_solution()

    # P-Median
    p_median = P_Median(I,J,d,w,p)
    p_median.model()
    p_median.print_solution()

    # Fixed Charge
    fixed_charge = Fixed_Charge(I,J,d,f,v,U,w)
    fixed_charge.model()
    fixed_charge.print_solution()

    # Hierarchical
    J = ["D", "E", "F"]  # 5 candidate locations
    hierarchical = Hierarchical(I,J,K,d1ik,d2kj,w,p,q,C1,C2,O)
    hierarchical.model()
    hierarchical.print_solution()
