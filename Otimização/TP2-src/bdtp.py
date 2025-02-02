
# Given a set of locations J and a set of clients I
#  Minimize
#   sum(j in J) f[j] y[j] +
#   sum(i in I)sum(j in J) c[i][j] * x[i][j]
#  Subject to
#   sum(j in J) x[i][j] == 1                    for all i in I
#               x[i][j] <= y[j]                 for all i in I, j in J
#               x[i][j] >= 0                    for all i in i, j in J
#               y[j] in { 0, 1 }                for all j in J
import sys
from mip import Model,xsum,minimize,maximize,CBC,OptimizationStatus,BINARY,CONTINUOUS,ConstrsGenerator,CutPool
import matplotlib.pyplot as plt
from itertools import product
import numpy as np
from time import time

np.random.seed(0)
GRIDSIZE = 1000
EPSILON = 1e-5

class Data():
    def __init__(self,ni,nj):
        self.ni = ni
        self.nj = nj
        self.f = np.random.randint(1000, high=2500, size=nj)
        self.d = np.random.randint(5     , high=30, size=ni)
        self.icoord = np.random.randint(1, high=GRIDSIZE, size=(ni,2))
        self.jcoord = np.random.randint(1, high=GRIDSIZE, size=(nj,2))
        c = self.icoord[:,np.newaxis,:] - self.jcoord[np.newaxis,:,:]
        # Euclidean distance matrix
        self.c = np.linalg.norm(c,axis=-1)
        # argument sort of c : sorted_c has indices
        self.sorted_c = np.argsort(self.c,axis=1)
        sorted_dist = []
        for c in self.c:
            setc = set(c)
            sc = np.sort(list(setc))
            sorted_dist.append(sc)
        self.sorted_dist = np.array(sorted_dist)
        self.K = [len(c) for c in self.sorted_dist]

class BendersPMedian():
    def __init__(self,dat : Data, is_hotstart = False, is_knapsack = False):
        self.dat = dat
        self.create_master_problem()
        self.is_hotstart = is_hotstart
        if is_hotstart == True:
            self.is_knapsack = True
        else:
            self.is_knapsack = is_knapsack

    def create_master_problem(self):
        dat = self.dat
        m = Model(name='PMRPMedian', solver_name=CBC)
        m.verbose = 0
        I,J = range(dat.ni),range(dat.nj)
        
        y = [m.add_var(obj=dat.f[j], var_type=BINARY, name='y(%d)'%j) for j in J]
        #eta = [m.add_var(obj=dat.d[i],var_type=CONTINUOUS,lb=0.0, name=f'eta({i})') for i in I]
        eta = [m.add_var(obj=dat.d[i],lb=dat.sorted_dist[i,0],var_type=CONTINUOUS,name=f'eta({i})') for i in I]
        m.y = y
        m.eta = eta
        m.objective = minimize(xsum(dat.d[i] * eta[i] for i in I) + xsum(dat.f[j] * y[j] for j in J))
        
        m += xsum(y[j] for j in J) >= 1
        #m.write('pmr.lp') 
        self.m = m

    def solve_master_problem(self):
        m = self.m
        dat = self.dat
        I,J = range(dat.ni),range(dat.nj)

        status = m.optimize(relax=self.is_hotstart)

        lb,_eta,_y= -float('inf'),None,None
        #m.write('mp.lp')
        if status == OptimizationStatus.OPTIMAL:
            lb = m.objective_value
            _y = np.array([m.y[j].x for j in J])
            _eta = np.array([m.eta[i].x for i in I])
        return lb,_eta,_y 

    def solve_dual_subproblem(self,_eta,_y):
        def solve_suproblem_i(dat,i,_y):
            
            nk = dat.K[i]
            J,K = range(dat.nj),range(nk)
            c,D = dat.c,dat.sorted_dist
            sd = Model(name='subproblem', solver_name=CBC)
            sd.verbose = 0
            
            v = [sd.add_var(var_type=CONTINUOUS,lb=0.0, name=f'v({k})') for k in K]

            sd.objective = maximize(D[i,0] \
                    + v[0] * (1 - sum(_y[j] for j in J if c[i][j] == D[i,0]))\
                    - xsum(sum(_y[j] for j in J if c[i][j] == D[i,k]) * v[k]  for k in K if k > 0))
            for k in K:
                if k < nk - 1:
                    sd += v[k] - v[k+1] <= D[i,k+1] - D[i,k]

            status = sd.optimize()
            if status == OptimizationStatus.OPTIMAL:
                phi = sd.objective_value
                lv = np.array([v[k].x for k in K])
                return phi, lv
            else:
                print(f'error solving dual subproblem {i}')
                sys.exit()

        dat = self.dat
        ni = dat.ni
        nj = dat.nj
        I = range(ni)
        _v = np.zeros((ni,nj))
        _phi = np.zeros(ni)
        phitotal = 0.0
        for i in I:
            _phi[i], lv = solve_suproblem_i(dat,i,_y)
            _v[i,:] = lv[:]
            phitotal += dat.d[i] * _phi[i]
        return phitotal,_phi,_v

    def add_benders_cuts(self,_v):
        m = self.m
        dat = self.dat
        I,J,K = range(dat.ni),range(dat.nj),dat.K
        D,c = dat.sorted_dist,dat.c
        y,eta = m.y,m.eta
        for i in I:
            m += eta[i] >= D[i,0] + _v[i,0]\
                    - xsum(_v[i,0] * y[j] for j in J if c[i][j]== D[i,0])\
                    - xsum( sum( _v[i,k] for k in range(1,K[i]) if c[i][j]== D[i,k] ) * y[j] for j in J) 

    def run(self):
        print('\n\n\n')
        dat = self.dat
        I,J = range(dat.ni),range(dat.nj)
        ub,lb = float('inf'),-float('inf')
        h = 0
        start_time = time()
        ittype = 'i'
        while (ub - lb > EPSILON):
            h += 1
            
            lb,_eta,_y = self.solve_master_problem()

            assert _y.all() != None, '\n\nerror running the Benders algorithm\n\n'

            phitotal,_phi,_v = self.solve_dual_subproblem(_eta,_y)
            
            self.add_benders_cuts(_v)

            sup = (_y * dat.f).sum() + phitotal

            ub = min(ub,sup)

            run_time = time() - start_time

            self.print_iteration_info(ittype,h,sup,ub,lb,run_time)
            #self.m.write('mp.lp')
            
        #self.print_iteration_info(ittype,h,sup,ub,lb,run_time)

    def print_iteration_info(self,ittype,h,sup,ub,lb,rt):
        gap = 100.0 * (ub - lb) / ub
        print("{:s} ".format(ittype), end = '')
        print("{:3d} ".format(h), end = '')
        print(" | {:15,.2f}".format(sup), end = '')
        print(" | {:15,.2f}".format(ub), end = '')
        print(" | {:15,.2f}".format(lb), end = '')
        print(" | {:6,.2f} %".format(gap), end = '')
        print(" | {:10,.2f} s".format(rt))

class Benders():
    def __init__(self,dat : Data, is_hotstart = False, is_knapsack = False):
        self.dat = dat
        self.create_master_problem()
        self.is_hotstart = is_hotstart
        if is_hotstart == True:
            self.is_knapsack = True
        else:
            self.is_knapsack = is_knapsack


    def create_master_problem(self):
        dat = self.dat
        m = Model(name='PMR', solver_name=CBC)
        m.verbose = 0
        I,J = range(dat.ni),range(dat.nj)
        
        y = [m.add_var(var_type=BINARY, name='y(%d)'%j) for j in J]
        eta = [m.add_var(var_type=CONTINUOUS,lb=0.0, name=f'eta({i})') for i in I]
        m.y = y
        m.eta = eta
        
        m.objective = minimize(xsum(eta[i] for i in I) + xsum(dat.f[j] * y[j] for j in J))
        
        m += xsum(y[j] for j in J) >= 1
        #m.write('pmr.lp') 
        self.m = m

    def run(self):
        print('\n\n\n')
        dat = self.dat
        I,J = range(dat.ni),range(dat.nj)
        ub,lb = float('inf'),-float('inf')
        h = 0
        start_time = time()
        if self.is_hotstart == True:
            ittype = 'h'
        else:
            ittype = 'i'
        while (ub - lb > EPSILON):
            h += 1
            
            lb,_eta,_y = self.solve_master_problem()

            assert _y.all() != None, '\n\nerror running the Benders algorithm\n\n'

            if self.is_knapsack == False:
                phi,_u,_v =  self.solve_dual_subproblem(_y)
            else:
                phi,_u,_v = self.solve_dual_subproblem_knapsack(_y)

            self.add_benders_cuts(_u,_v)
            #verificar depois 
            sup = lb - _eta + phi
            ub = min(ub,sup)

            run_time = time() - start_time

            #self.print_iteration_info(ittype,h,sup,ub,lb,run_time)

            if self.is_hotstart == True and ub - lb < EPSILON:
                self.is_hotstart = False
                ub = float('inf') 
                ittype = 'i'
        self.print_iteration_info(ittype,h,sup,ub,lb,run_time)

    def print_iteration_info(self,ittype,h,sup,ub,lb,rt):
        gap = 100.0 * (ub - lb) / ub
        print("{:s} ".format(ittype), end = '')
        print("{:3d} ".format(h), end = '')
        print(" | {:15,.2f}".format(sup), end = '')
        print(" | {:15,.2f}".format(ub), end = '')
        print(" | {:15,.2f}".format(lb), end = '')
        print(" | {:6,.2f} %".format(gap), end = '')
        print(" | {:10,.2f} s".format(rt))

    def add_benders_cuts(self,_u,_v):
        m = self.m
        dat = self.dat
        I,J = range(dat.ni),range(dat.nj)
        y,eta = m.y,m.eta
        for it in I:
            m += eta[it] >= sum(_u) - xsum(sum(_v[i][j] for i in I) * y[j] for j in J)
    def solve_dual_subproblem(self,_y):
        dat = self.dat
        I,J = range(dat.ni),range(dat.nj)
        c,d = dat.c,dat.d 
        O = [j for j in J if _y[j] > 0.9]
        C = [j for j in J if _y[j] < 0.1]
        u = [min([d[i] * c[i][j] for j in O]) for i in I]
        v = [[max(u[i] - d[i] * c[i][j],0.0) if j in C else 0.0 for j in J] for i in I]
        return sum(u), u, v

    def solve_dual_subproblem_knapsack(self,_y):
        dat = self.dat
        ni,nj=dat.ni,dat.nj
        I,J = range(dat.ni),range(dat.nj)
        c,d = dat.c,dat.d
        u = np.zeros(ni,dtype=float)
        v = np.zeros((ni,nj),dtype=float)
        phi = 0.0
        for i in I:
            sy = _y[dat.sorted_c[i]]
            csum = np.cumsum(sy)
            k = np.argmax(csum>=1)
            _u = dat.d[i] * dat.c[i][dat.sorted_c[i][k]]
            u[i] = _u
            phi += _u
            for p in J:
                if p < k:
                    _j = dat.sorted_c[i][p]
                    _v = max(u[i] - dat.d[i] * dat.c[i][_j],0.0)
                    v[i][_j] = _v
                    phi -= _v * _y[_j]
                else:
                    break
        return phi,u,v

    def solve_master_problem(self):
        m = self.m
        dat = self.dat
        I,J = range(dat.ni),range(dat.nj)
        status = m.optimize(relax=self.is_hotstart)
        lb,_eta,_y= -float('inf'),-float('inf'),None
        if status == OptimizationStatus.OPTIMAL:
            lb = m.objective_value
            _y = np.array([m.y[j].x for j in J])
            # _eta = np.array(m.eta[i].x for i in I)
        else: print('error Benders')
        return lb,_eta,_y 

class BendersMulticut():
    def __init__(self,dat : Data, is_hotstart = False, is_knapsack = False):
        self.dat = dat
        self.create_master_problem()
        self.is_hotstart = is_hotstart
        if is_hotstart == True:
            self.is_knapsack = True
        else:
            self.is_knapsack = is_knapsack

    def create_master_problem(self):
        dat = self.dat
        m = Model(name='PMR', solver_name=CBC)
        m.verbose = 0
        I,J = range(dat.ni),range(dat.nj)
        
        y = [m.add_var(var_type=BINARY, name='y(%d)'%j) for j in J]
        eta = [m.add_var(var_type=CONTINUOUS, lb=0.0,name='eta(%d)'%i) for i in I]
        m.y = y
        m.eta = eta
        
        m.objective = minimize(xsum(eta[i] for i in I) + xsum(dat.f[j] * y[j] for j in J))
        
        m += xsum(y[j] for j in J) >= 1
        #m.write('pmr.lp') 
        self.m = m

    def run(self):
        print('\n\n\n')
        dat = self.dat
        I,J = range(dat.ni),range(dat.nj)
        ub,lb = float('inf'),-float('inf')
        h = 0
        start_time = time()
        if self.is_hotstart == True:
            ittype = 'h'
        else:
            ittype = 'i'
        while (ub - lb > EPSILON):
            h += 1
            if h > 100:
                break
            lb,_eta,_y = self.solve_master_problem()

            assert _y.all() != None, '\n\nerror running the Benders algorithm\n\n'

            if self.is_knapsack == False:
                phi,_u,_v =  self.solve_dual_subproblem(_y)
            else:
                phi,_u,_v = self.solve_dual_subproblem_knapsack(_y)

            self.add_benders_cuts(_u,_v)

            sup = lb - _eta.sum() + phi
            ub = min(ub,sup)

            run_time = time() - start_time

            #self.print_iteration_info(ittype,h,sup,ub,lb,run_time)

            if self.is_hotstart == True and ub - lb < EPSILON:
                self.is_hotstart = False
                ub = float('inf') 
                ittype = 'i'
            self.print_iteration_info(ittype,h,sup,ub,lb,run_time)

    def print_iteration_info(self,ittype,h,sup,ub,lb,rt):
        gap = 100.0 * (ub - lb) / ub
        print("{:s} ".format(ittype), end = '')
        print("{:3d} ".format(h), end = '')
        print(" | {:15,.2f}".format(sup), end = '')
        print(" | {:15,.2f}".format(ub), end = '')
        print(" | {:15,.2f}".format(lb), end = '')
        print(" | {:6,.2f} %".format(gap), end = '')
        print(" | {:10,.2f} s".format(rt))

    def add_benders_cuts(self,_u,_v):
        m = self.m
        dat = self.dat
        I,J = range(dat.ni),range(dat.nj)
        y,eta = m.y,m.eta
        for i in I:
            m += eta[i] >= _u[i] - xsum(_v[i][j] * y[j] for j in J) 

    def solve_dual_subproblem(self,_y):
        dat = self.dat
        I,J = range(dat.ni),range(dat.nj)
        c,d = dat.c,dat.d 
        O = [j for j in J if _y[j] > 0.9]
        C = [j for j in J if _y[j] < 0.1]
        u = [min([d[i] * c[i][j] for j in O]) for i in I]
        v = [[max(u[i] - d[i] * c[i][j],0.0) if j in C else 0.0 for j in J] for i in I]
        return sum(u), u, v

    def solve_dual_subproblem_knapsack(self,_y):
        dat = self.dat
        ni,nj=dat.ni,dat.nj
        I,J = range(dat.ni),range(dat.nj)
        c,d = dat.c,dat.d
        u = np.zeros(ni,dtype=float)
        v = np.zeros((ni,nj),dtype=float)
        phi = 0.0
        for i in I:
            sy = _y[dat.sorted_c[i]]
            csum = np.cumsum(sy)
            k = np.argmax(csum>=1)
            #print(k,sy,csum)
            _u = dat.d[i] * dat.c[i][dat.sorted_c[i][k]]
            u[i] = _u
            phi += _u
            for p in J:
                if p < k:
                    _j = dat.sorted_c[i][p]
                    _v = max(0.0,u[i] - dat.d[i] * dat.c[i][_j])
                    v[i][_j] = _v
                    phi -= _v * _y[_j]
                else:
                    break
        return phi,u,v

    def solve_master_problem(self):
        m = self.m
        dat = self.dat
        I,J = range(dat.ni),range(dat.nj)
        status = m.optimize(relax=self.is_hotstart)
        lb,_eta,_y= -float('inf'),None,None
        if status == OptimizationStatus.OPTIMAL:
           lb = m.objective_value
           _y = np.array([m.y[j].x for j in J])
           _eta = np.array([m.eta[i].x for i in I])
        return lb,_eta,_y 

class BendersCutCutGenerator(ConstrsGenerator):
    def __init__(self, dat: Data,y,eta):
        self.dat = dat
        self.y,self.eta=y,eta
    def generate_constrs(self,model: Model, depth: int=0, npass: int=0):
        dat = self.dat
        I,J = range(dat.ni),range(dat.nj)

        y,eta = self.y,self.eta
        ly,leta = model.translate(y),model.translate(eta)

        _y = np.array([ly[j].x if ly[j] else 0 for j in J]) 
        _eta = np.array([leta[i].x if leta[i] else 0 for i in I]) 

        phi,u,v = self.solve_dual_subproblem_knapsack(_y)
        for i in I:
            if phi[i] - _eta[i] > EPSILON:
               cut = leta[i] >= u[i] - xsum(v[i][j] * ly[j] for j in J)
               model += cut

    def solve_dual_subproblem_knapsack(self,_y):
        dat = self.dat
        ni,nj=dat.ni,dat.nj
        I,J = range(dat.ni),range(dat.nj)
        c,d = dat.c,dat.d
        u = np.zeros(ni,dtype=float)
        v = np.zeros((ni,nj),dtype=float)
        phi = np.zeros(ni,dtype=float)
        for i in I:
            sy = _y[dat.sorted_c[i]]
            csum = np.cumsum(sy)
            k = np.argmax(csum>=1)
            _u = dat.d[i] * dat.c[i][dat.sorted_c[i][k]]
            u[i] = _u
            phi[i] = _u
            for p in J:
                if p < k:
                    _j = dat.sorted_c[i][p]
                    _v = max(0.0,u[i] - dat.d[i] * dat.c[i][_j])
                    v[i][_j] = _v
                    phi[i] -= _v * _y[_j]
                else:
                    break
        return phi,u,v

class BendersBranchAndCut():
    def __init__(self,dat : Data):
        self.dat = dat
        self.create_master_problem()
        print('here')

    def create_master_problem(self):
        dat = self.dat
        m = Model(name='PMR', solver_name=CBC)
        #m.verbose = 0
        I,J = range(dat.ni),range(dat.nj)
        
        y = [m.add_var(var_type=BINARY, name='y(%d)'%j) for j in J]
        eta = [m.add_var(var_type=CONTINUOUS, lb=0.0,name='eta(%d)'%i) for i in I]
        m.y = y
        m.eta = eta
        
        m.objective = minimize(xsum(eta[i] for i in I) + xsum(dat.f[j] * y[j] for j in J))
        
        m += xsum(y[j] for j in J) >= 1

        #m.write('pmr.lp') 
        self.m = m

    def run(self):
        m = self.m
        #m.cuts_generator = BendersCutCutGenerator(self.dat,m.y,m.eta)
        m.lazy_constrs_generator = BendersCutCutGenerator(self.dat,m.y,m.eta)
        print('\n\n\n')
        m.verbose = 0
        start_time = time()
        status = m.optimize()
        self.run_time = time() - start_time
        if status == OptimizationStatus.OPTIMAL:
            self.is_solution = True
            self.print_solution()
    
    def print_solution(self):
        if self.is_solution == True:
           dat = self.dat
           m = self.m
           I,J = range(dat.ni), range(dat.nj)
           print("Custo total              : {:12,.2f}.".format(m.objective_value))
           print("Tempo total              : {:12,.2f}.".format(self.run_time))
           
           print( "facilidades  ")
           for j in J:
               if m.y[j].x > 1e-6:
                  print("{:5d} ".format(j+1),end='')

        else:
            print()
            print('Nao ha solucao disponivel para impressao')
            print()

class PMEDIAN():
    def __init__(self,dat :Data):
        self.is_solution = False
        self.dat = dat
        self.build_model()

    def run(self):
        print('\n\n\n')
        m = self.m
        m.verbose = 0
        start_time = time()
        status = m.optimize()
        self.run_time = time() - start_time
        if status == OptimizationStatus.OPTIMAL:
            self.is_solution = True

    def print_solution(self):
        if self.is_solution == True:
           dat = self.dat
           m = self.m
           I,J = range(dat.ni), range(dat.nj)
           print("Custo total              : {:12,.2f}.".format(m.objective_value))
           print("Tempo total              : {:12,.2f}.".format(self.run_time))
           
        else:
            print()
            print('Nao ha solucao disponivel para impressao')
            print()

    def build_model(self):
       dat = self.dat
       m = Model(name='pmedian', solver_name=CBC)
   
       I = range(dat.ni)
       J = range(dat.nj)
       
       y = [m.add_var(var_type=BINARY, name=f'y({j})') for j in J]
       z = {(i,k) : m.add_var(lb=0.0,name=f'_z({i},{k})') for i in I for k in range(dat.K[i]) }
       m.z = z
       m.y = y
       
       m.objective = minimize(xsum(dat.f[j] * y[j] for j in J) \
                   + xsum(dat.d[i] * (dat.sorted_dist[i][0] + xsum( (dat.sorted_dist[i][k+1] - dat.sorted_dist[i][k]) * z[i,k] for k in range(dat.K[i] - 1))) for i in I))

       for i in I:
          m += z[i,0] + xsum(y[j] for j in J if abs(dat.c[i][j] - dat.sorted_dist[i][0]) < 1e-3) >= 1
          for k in range(1,dat.K[i]): 
             m += z[i,k] - z[i,k-1] + xsum(y[j] for j in J if abs(dat.c[i][j] - dat.sorted_dist[i][k]) < 1e-3) >= 0

       m.write('pmedian.lp')
       self.m = m

class UFLP():
    def __init__(self,dat : Data):
        self.is_solution = False
        self.dat = dat
        self.build_model()

    def run(self):
        print('\n\n\n')
        m = self.m
        m.verbose = 0
        start_time = time()
        status = m.optimize()
        self.run_time = time() - start_time
        if status == OptimizationStatus.OPTIMAL:
            self.is_solution = True

    def print_solution(self):
        if self.is_solution == True:
           dat = self.dat
           m = self.m
           I,J = range(dat.ni), range(dat.nj)
           print("Custo total de instalacao: {:12,.2f}".format(sum([m.y[j].x * dat.f[j] for j in J])))
           print("Custo total de transporte: {:12,.2f} ".format(sum([m.x[i,j].x * dat.d[i] * dat.c[i][j] for (i,j) in product(I,J)])))
           print("Custo total              : {:12,.2f}.".format(m.objective_value))
           print("Tempo total              : {:12,.2f}.".format(self.run_time))
           
           print( "facilidades : demanda : clientes ")
           for j in J:
               if m.y[j].x > 1e-6:
                  print("{:11d} : {:7.0f} : ".format(j+1,sum([m.x[i,j].x * dat.d[i] for i in I])),end='')
                  for i in I:
                      if m.x[i,j].x > 1e-6: 
                         print(" {:d}".format(i+1),end='')
                  print()
        else:
            print()
            print('Nao ha solucao disponivel para impressao')
            print()

    def build_model(self):
       dat = self.dat
       m = Model(name='uflp', solver_name=CBC)
   
       I = range(dat.ni)
       J = range(dat.nj)
       
       y = [m.add_var(var_type=BINARY, name=f'y({j})') for j in J]
       x = {(i,j) : m.add_var(lb=0.0,name='x(%d,%d)' %(i,j)) for j in J for i in I}
       m.x = x
       m.y = y
       
       m.objective = minimize(xsum(dat.f[j] * y[j] for j in J) + xsum(dat.d[i] * dat.c[i][j] * x[i,j] for (i,j) in product(I,J)))
       for i in I:
          m += xsum(x[i,j] for j in J) == 1
       for (i,j) in product(I,J):
          m += x[i,j] <= y[j]

       #m.write('uflp.lp')
       self.m = m

class D:
    def __init__(self,filename:str):
        self.facilidades(filename)
        self.sorted_c = np.argsort(self.c,axis=1)
        sorted_dist = []
        for c in self.c:
            sc = np.sort(list(c))#tirei o set pq tem elementos duplicados em c
            #print(len(sc), len(c))
            sorted_dist.append(sc)
        self.sorted_dist = np.array(sorted_dist)
        self.K = [len(c) for c in self.sorted_dist]
    def facilidades(self,filename:str):
        with open(filename, 'r') as file:
            lines = file.readlines()
        header = lines[0].strip().split()
        nj = int(header[0])
        ni = int(header[1])
        I, J = range(ni), range(nj)
        capacity = []
        f = []
        line_index = 1  # Start reading from the second line
        for _ in J:
            parts = lines[line_index].strip().split()
            capacity.append(float(parts[0]))
            f.append(float(parts[1]))
            line_index += 1
        d = []
        c = []
        for _ in I:
            parts = lines[line_index].strip().split()
            d.append(float(parts[0]))
            cj = []
            while len(cj) < nj:
                line_index += 1
                cj.extend(map(float, lines[line_index].strip().split()))
            line_index+=1
            c.append(list(cj))
        self.ni,self.nj,self.f,self.d,self.c=ni,nj,f,d,c


class BendersP:
    def __init__(self, dat, is_hotstart=False, is_knapsack=False):
        self.dat = dat
        self.create_master_problem()
        self.is_hotstart = is_hotstart
        if is_hotstart:
            self.is_knapsack = True
        else:
            self.is_knapsack = is_knapsack

    def create_master_problem(self):
        dat = self.dat
        m = Model(name='PMRPMedian', solver_name=CBC)
        m.verbose = 0
        I, J = range(dat.ni), range(dat.nj)
        
        y = [m.add_var(obj=dat.f[j], var_type=BINARY, name='y(%d)' % j) for j in J]
        theta = [m.add_var(var_type=CONTINUOUS, lb=0.0, name=f'theta({i})') for i in I]
        
        m.objective = minimize(xsum(theta[i] for i in I))
        
        m += xsum(y[j] for j in J) == 1#dat.p
        
        self.m = m
        m.y = y
        m.theta = theta
    def solve_master_problem(self):
        m = self.m
        dat = self.dat
        I,J = range(dat.ni),range(dat.nj)

        status = m.optimize()

        lb,_eta,_y= -float('inf'),None,None
        #m.write('mp.lp')
        if status == OptimizationStatus.OPTIMAL:
            lb = m.objective_value
            _y = np.array([m.y[j].x for j in J])
            _eta = np.array([m.theta[i].x for i in I])
            # for c in m.constrs:
            #     print(c)
            # print('\n',lb)
        return lb,_eta,_y   
    def k(self,i,y):
        dat = self.dat
        d = dat.c
        D = dat.sorted_dist
        K = range(dat.K[i])
        J = range(dat.nj)
        if sum(y[j] for j in J if d[i][j] == D[i][0])>=1:
            return 0
        else:
            return max(k for k in K if all(y[j] < 1 for j in J if d[i][j] <= D[i][k]))   
    def dual_sub_problem(self, k):
        dat = self.dat
        D = dat.sorted_dist
        I = range(dat.ni)
        v = np.zeros(dat.ni, dtype=float)
        for i in I:
            if k <= dat.K[i]:
                v[i] = D[i][k+1] - D[i][k]
            else: v[i] = 0
        return v
    def sub_problem(self,i,_y,k):
        dat = self.dat
        dat = self.dat
        J = range(dat.nj)
        D = dat.sorted_dist
        d = dat.c
        if k==0:
            return D[i][1]
        else:
            return D[i][k+1]-sum((D[i][k+1]-d[i][j])*_y[j] for j in J if d[i][j] <= D[i][k])
    def benders_cuts(self,y,i,K):
        m = self.m
        #cut_pool = CutPool()
        dat = self.dat
        D = dat.sorted_dist
        d = dat.c
        J = range(dat.nj)
        if K == 0:
            self.m.add_constr(m.theta[i]>=D[i][1])
        else:
            self.m.add_constr(m.theta[i]>= D[i][K+1] - xsum((D[i][K+1] -d[i][j])*m.y[j] for j in J if d[i][j] <= D[i][K]))
    def run(self):
        def algorith_1(y, theta, remove:bool=False):
            cut = False
            ub = 0
            for i in I:
                # print(i)
                k = self.k(i,y)
                opt_sp = self.sub_problem(i,y,k)
                # print(opt_sp)
                ub += opt_sp
                if theta[i]<opt_sp:
                    self.benders_cuts(y,i,k)
                    cut = True
                # print(i, k)
            return cut,ub
        def algorith_2(i,y):
            # coloquei r =0 invez d 1, pois se não ele acessa um valor que não existe por causa do r+1 e r<len(J)
            k_med, r = 0, 0
            sy = lambda R: y[self.dat.sorted_c[i][R]]
            val = 1 - sy(r)
            while val > 0 and r < len(J):
                # print(r)
                if self.dat.c[i][int(sy(r+1))]> self.dat.c[i][int(sy(r))]:
                    k_med +=1
                r+=1
                val= val -sy(r)
            # print(k_med)
            return k_med
        def algorith_3(y, ub,lb,theta):
            cut,ub = algorith_1(y,theta)
            _cut = cut
            while(_cut):
                # print('cut')
                lb,_theta, _y = self.solve_master_problem()
                _cut,_ub = algorith_1(_y,_theta)
                ub = min(ub,_ub)
                #if _ub < ub:
                #    print('ub')
                #    ub = _ub
                #    y = _y
            return lb,ub, y
        print('\n\n\n')
        dat = self.dat
        I,J = range(dat.ni),range(dat.nj)
        ub,lb = float('inf'),-float('inf')
        h = 0
        ittype = 'i'
        start_time = time()
        while (ub - lb > EPSILON):
            h+=1
            lb, theta,y = self.solve_master_problem()
            ub,lb,y = algorith_3(y,ub,lb,theta)
            run_time = time() - start_time
            
            self.print_iteration_info(ittype,h,0,ub,lb,run_time)
            #if(h>100):break

    def print_iteration_info(self, ittype, h, sup, ub, lb, rt):
        gap = 100.0 * (ub - lb) / ub
        print(f"{ittype} {h:3d} | {sup:15,.2f} | {ub:15,.2f} | {lb:15,.2f} | {gap:6,.2f} % | {rt:10,.2f} s")

if __name__ == "__main__":
    # parse args
    #args = sys.argv
    #assert len(args) > 2, f"\n\nuse: %s ni nj\n\n" % args[0]
    dat = D(r'TP2-src\ORLIB-cap\40\cap41.txt')
    print("solving the BD p-median variant ") 
    #bdp = BendersPMedian(dat)
    #bdp.run()
    bend = BendersP(dat)
    bend.run()
    print("solving uflp ") 
    uflp = UFLP(dat)
    uflp.run()
    uflp.print_solution()
#
    print("solving pmedian ") 
    pmedian = PMEDIAN(dat)
    pmedian.run()
    pmedian.print_solution()
    
    # print("solving the Benders") 

    # bd = Benders(dat)
    # bd.run()

    print("solving the BD p-median variant ") 
    bdp = BendersPMedian(dat)
    bdp.run()
# 
    # bd = Benders(dat,is_hotstart=False,is_knapsack=True)
    # bd.run()
    # # 
    # bd = Benders(dat,is_hotstart=True)
    # bd.run()

    print("solving the BendersMulticut") 
    bdmcut = BendersMulticut(dat)
    bdmcut.run()
# 
    # bdmcut = BendersMulticut(dat,is_hotstart=True)
    # bdmcut.run()
# 
    print("solving the BD B&C") 
    bdbc = BendersBranchAndCut(dat) 
    bdbc.run()



