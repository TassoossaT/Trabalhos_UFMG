import sys
from itertools import product
import os
import math
import numpy as np
import json 
import random
from time import time
#from ilsvnd import *
from dotmap import DotMap
from mip import Model, xsum, maximize, minimize, CBC, MAXIMIZE, MINIMIZE,OptimizationStatus, BINARY,Column,ConstrList
# ------------------------------ 
#
# ------------------------------ 
#same_limit = 10
#h_limit = 500
# ------------------------------ 
#
# ------------------------------ 
def main():
   dt = read_data("gap.dat")   

   # martello and toth's heuristic
   ub,_x = mth(dt)

   # dantzig and wolfe: pricing problem has the assignment constraints 
   dw_assignment(dt,ub,_x)

#    # dantzig and wolfe: pricing problem has the knapsack constraints 
#    dw_knapsack(dt,ub,_x)

#    # dantzig and wolfe: Lagrangian decomposition 
#    #dw_lagrangian_decomposition(dt,ub,_x)

#    #column generation
#    column_generation_savelsbergh(dt,ub,_x)
#    # mip model
#    model_gap(dt)

# ------------------------------ 
# pricing uses the assignment constraints
# ------------------------------ 
def dw_assignment(dt,ub,_x):
    def create_master_problem_assignment_pricing(dt,ub,_x):
        J,I,c,b,t = dt.J, dt.I, dt.c, dt.b, dt.t
      
        mod = Model('dwmpassign',sense=MINIMIZE,solver_name=CBC)
        mod.verbose = 0
      
        mod.e = mod.add_var(lb=0.0,obj=dt.BigM,name='_e',var_type='C')
        mod.lambdaa = [mod.add_var(lb=0.0,obj=ub,var_type='C',name=f'll(0)')]
      
        mod.add_constr(mod.lambdaa[0] == 1,name='norm')
        for j in J:
            coeff = sum(t[i][j] for i in I if _x[i] == j)
            #print(j,coeff,b[j])
            mod.add_constr( coeff * mod.lambdaa[0] - mod.e <= b[j],name=f'r{j}')
        #mod.write('dw1.lp')
        #sys.exit()
        return mod

    def print_info(it,mpobj,lb,lbinf,rc):
        print(f'{it:4d} ',end='')
        print(f'{mpobj:18.2f} ',end='')
        print(f'{lb:18.2f} ',end='')
        print(f'{lbinf:18.2f} ',end='')
        print(f'{rc:18.2f} ',end='')
        print()
    
    def solve_pricing(_u,_u0):
        #print('u,u0',_u,_u0)
        #print('c',c)
        #print('t',t)
        pricecoeffs = c - _u * t 
        #print('coeffs',pricecoeffs)
        minj = np.argmin(pricecoeffs,axis=1)
        #print('minj',minj)
        x[:,:] = 0
        #print('x0',x)
        #print('arange',np.arange(ni))
        x[np.arange(ni),minj] = 1
        #print('x',x)
        rc = (pricecoeffs * x).sum() - _u0
        #print('rc',rc)
        #sys.exit()
        return rc

    def solve_master_problem():
        status = mp.optimize()
        assert status == OptimizationStatus.OPTIMAL, 'Error solving the master program'
        _u0 = mp.constrs[0].pi
        _u = np.array([r.pi for r in mp.constrs[1:]])
        return mp.objective_value,_u,_u0

    print("pricing uses the assignment constraints")
    nj,ni,J,I,c,b,t = dt.nj, dt.ni, dt.J, dt.I, np.array(dt.c), np.array(dt.b), np.array(dt.t)

    mp = create_master_problem_assignment_pricing(dt,ub,_x)
    # ---------------------------------
    # main loop 
    # ---------------------------------
    x = np.zeros((ni,nj))
    it,lb,rc = 0,0.0, -1
    while rc < -1e-6:
        it += 1
        # solving the master program
        # getting the objective and dual values
        mpobj,_u,_u0 = solve_master_problem()

        # solving the pricing problem
        rc = solve_pricing(_u,_u0)

        # adding new column
        #print('t',t)
        #print('x',x)
        #print('tx',t*x)
        _col = (t * x).sum(axis=0)
        #print(_col)

        obj = (c * x).sum()
        col = Column(constrs= mp.constrs, coeffs=[1] + _col.tolist()) 
        mp.add_var(lb=0.0,obj=obj,column=col,name=f'll({it})')
        #mp.write('newcol.lp')
        #sys.exit()
        #computing the lower bound
        lbinf = rc + (b * _u).sum() + _u0
        lb = max(lb,lbinf)

        print_info(it,mpobj,lb,lbinf,rc)
        #mp.write('mp.lp')
    print_info(it,mpobj,lb,lbinf,rc)

# ------------------------------ 
# pricing uses the knapsack constraints
# ------------------------------ 
def dw_knapsack(dt,ub,_x):
    def create_master_problem_knapsack_pricing(dt,ub,_x):
        J,I,c,b,t = dt.J, dt.I, dt.c, dt.b, dt.t
      
        mod = Model('dwmpknapsack',sense=MINIMIZE,solver_name=CBC)
        mod.verbose = 0
      
        mod.ep = [mod.add_var(lb=0.0,obj=dt.BigM,name='ep',var_type='C') for i in I]
        mod.en = [mod.add_var(lb=0.0,obj=dt.BigM,name='en',var_type='C') for i in I]
        mod.lambdaa = [mod.add_var(lb=0.0,obj=ub,var_type='C',name=f'll(0)')]
      
        mod.add_constr(mod.lambdaa[0] == 1,name='norm')
        for i in I:
            mod.add_constr( sum(1 for j in J if _x[i] == j) * mod.lambdaa[0] + mod.ep[i] - mod.en[i] == 1.0,name=f'r{i}')
        return mod

    def solve_pricing_knapsack(dt,_u,_u0):
        J,I,c,b,t = dt.J, dt.I, dt.c, dt.b, dt.t
        rc = -_u0
        for j in J:
            p = c[:,j] - _u[:]
            w = t[:,j]
            g = b[j]
            obj, _x = knapsack(p,w,g)
            x[:,j] = _x[:]
            rc += obj
        return rc
    def knapsack(p,w,g):
        n = len(p)
        N = range(n)
        mod = Model('knapsack',sense=MINIMIZE,solver_name=CBC)
        mod.verbose = 0
        vx = [mod.add_var(var_type=BINARY,obj=p[i]) for i in N] 
        mod += xsum(w[i] * vx[i] for i in N) <= g
        status = mod.optimize() 
        assert status == OptimizationStatus.OPTIMAL, 'Error solving the knapsack pricing problem '
        of = mod.objective_value
        _x = np.array([v.x for v in vx])
        return of,_x

    def print_info(it,mpobj,lb,lbinf,rc):
        print(f'{it:4d} ',end='')
        print(f'{mpobj:18.2f} ',end='')
        print(f'{lb:18.2f} ',end='')
        print(f'{lbinf:18.2f} ',end='')
        print(f'{rc:18.2f} ',end='')
        print()
    
    def solve_master_problem():
        status = mp.optimize()
        assert status == OptimizationStatus.OPTIMAL, 'Error solving the master program'
        _u0 = mp.constrs[0].pi
        _u = np.array([r.pi for r in mp.constrs[1:]])
        return mp.objective_value,_u,_u0

    print("pricing uses the knapsack constraints")
    nj,ni,J,I,c,b,t = dt.nj, dt.ni, dt.J, dt.I, np.array(dt.c), np.array(dt.b), np.array(dt.t)
 
    mp = create_master_problem_knapsack_pricing(dt,ub,_x)
    # ---------------------------------
    # main loop 
    # ---------------------------------
    x = np.zeros((ni,nj))
    it,lb,rc = 0,0.0, -1
    while rc < -1e-6:
        it += 1
        # solving the master program
        # getting the objective and dual values
        mpobj,_u,_u0 = solve_master_problem()

        # solving the pricing problem
        rc = solve_pricing_knapsack(dt,_u,_u0)

        # adding new column
        _col = x.sum(axis=1)
        obj = (c * x).sum()
        col = Column(constrs= mp.constrs, coeffs=[1] + _col.tolist()) 
        mp.add_var(lb=0.0,obj=obj,column=col,name=f'll({it})')

        #computing the lower bound
        lbinf = rc + _u.sum() + _u0
        lb = max(lb,lbinf)

        print_info(it,mpobj,lb,lbinf,rc)
        #mp.write('mp.lp')
    print_info(it,mpobj,lb,lbinf,rc)

# ------------------------------ 
# Martin Savelsbergh, (1997) A Branch-and-Price Algorithm for the Generalized Assignment Problem. 
# Operations Research
# 45(6):831-841.
# ------------------------------ 
def column_generation_savelsbergh(dt,ub,_x):
    def create_master_problem_lagrangian_decomposition(dt,ub,_x):
        J,I,c,b,t = dt.J, dt.I, dt.c, dt.b, dt.t
        mod = Model('colgensavelsbergh',sense=MINIMIZE,solver_name=CBC)
        mod.verbose = 0
        
        mod.e = [mod.add_var(lb=0.0,obj=dt.BigM,name=f'_e({i})',var_type='C') for i in I]
        mod.lambdaa = [mod.add_var(lb=0.0,obj=sum([dt.c[i][j] for i in I if _x[i] == j]),name=f'll({j})',var_type='C') for j in J]
        for i in I:
            mod.add_constr(mod.e[i] + xsum( mod.lambdaa[j] if _x[i] == j else 0.0 for j in J ) == 1,name=f'ri({i})')
        for j in J:
            mod.add_constr(mod.lambdaa[j] <= 1,name=f'rj({j})')
        #mod.write('cg.lp')
        #sys.exit()
        return mod

    def solve_pricing_knapsack(dt,_u):
        J,ni = dt.J,dt.ni
        bestobj,bestj = float('inf'),-1
        for j in J:
            p = c[:,j] - _u[:ni]
            w = t[:,j]
            g = b[j]

            obj, _x = knapsack(p,w,g)

            zkp = obj - _u[ni+j]
            x[:,j] = _x[:]
            if bestobj > zkp: 
                bestobj = zkp
                bestj = j
        return bestobj,bestj

    def knapsack(p,w,g):
        n = len(p)
        N = range(n)
        mod = Model('knapsack',sense=MINIMIZE,solver_name=CBC)
        mod.verbose = 0
        vx = [mod.add_var(var_type=BINARY,obj=p[i]) for i in N] 
        mod += xsum(w[i] * vx[i] for i in N) <= g
        status = mod.optimize() 
        assert status == OptimizationStatus.OPTIMAL, 'Error solving the knapsack pricing problem '
        of = mod.objective_value
        _x = np.array([v.x for v in vx])
        return of,_x

    def print_info(it,mpobj,lb,lbinf,rc):
        print(f'{it:4d} ',end='')
        print(f'{mpobj:18.2f} ',end='')
        print(f'{lb:18.2f} ',end='')
        print(f'{lbinf:18.2f} ',end='')
        print(f'{rc:18.2f} ',end='')
        print()
    
    def solve_master_problem(nj):
        status = mp.optimize()
        assert status == OptimizationStatus.OPTIMAL, 'Error solving the master program'
        _u = np.array([r.pi for r in mp.constrs])
        return mp.objective_value,_u,

    print("column generation Savelsbergh")
    nj,ni,J,I,c,b,t = dt.nj, dt.ni, dt.J, dt.I, np.array(dt.c), np.array(dt.b), np.array(dt.t)
    mp = create_master_problem_lagrangian_decomposition(dt,ub,_x)
    # ---------------------------------
    # main loop 
    # ---------------------------------
    x = np.zeros((ni,nj))
    it,lb,stop,rc = 0,0.0, False,-1
    while rc < -1e-6:
        it += 1
        # solving the master program
        # getting the objective and dual values
        #mpobj,_u,_u0,_v0 = solve_master_problem(nj)
        mpobj,_u = solve_master_problem(nj)

        # solving the pricing problem
        rc,bestj = solve_pricing_knapsack(dt,_u)

        # adding new column
        objll = (dt.c[:,bestj] * x[:,bestj]).sum()
        _colll = np.zeros(nj + ni)

        for i in I:
            if x[i,bestj] > 0.9:
                _colll[i] = 1.0
        _colll[ni + bestj] = 1.0

        colll = Column(constrs= mp.constrs, coeffs= _colll.tolist()) 
        mp.add_var(lb=0.0,obj=objll,column=colll,name=f'l({it+nj})')
        #mp.write('newcolcg.lp')
        #sys.exit()
        #computing the lower bound
        lbinf = rc + _u.sum() 
        lb = max(lb,lbinf)

        print_info(it,mpobj,lb,lbinf,rc)
        #mp.write('mp.lp')
    print_info(it,mpobj,lb,lbinf,rc)
    mp.write('mp.lp')

def model_gap(dt):
    print("solving the gap using CBC")
    ni = dt.ni
    nj = dt.nj
    J = range(nj)
    I = range(ni)
    IJ = product(I,J)
    c = dt.c
    b = dt.b
    t = dt.t
    
    mod = Model('gap',sense=MINIMIZE,solver_name=CBC)
    mod.verbose = 0

    x = {(i,j) : mod.add_var(var_type=BINARY,obj=c[i][j]) for (i,j) in IJ}
    for i in I:
        mod += xsum(x[i,j] for j in J) == 1
    for j in J:
        mod += xsum(t[i][j] *  x[i,j] for i in I) <= b[j]

    mod.optimize(relax=True)
    lb = mod.objective_value
    #print(mod.solution.get_status_string())
    print("linear relaxation : {:.2f}".format(lb))
    mod.optimize(relax=False)
    ub = mod.objective_value
    print("solution          : {:.2f}".format(ub))
    print("linear gap        : {:.2f} %".format(100.0*(ub-lb)/ub))

def mth(dt):
    ni = dt.ni
    nj = dt.nj
    J = dt.J 
    I = list(dt.I)
    IJ = [(i,j) for j in J for i in I]
    c = dt.c
    b = list(dt.b)
    t = dt.t
   
    L = [sorted([(j,c[i][j]) for j in J],key = lambda t: t[1]) for i in I] 
    x = [ -1 for i in I]
    of = 0.0
    while len(I) > 0:
         i,w = max([(i,L[i][1][1] - L[i][0][1]) if len(L[i]) > 1 else (i,L[i][0][1]) for i in I],key = lambda t : t[1]) 
         j = L[i][0][0]
         if (b[j] - t[i][j] < 0):
            for i in I:
                for jj,v in L[i]:
                    if jj == j:
                       L[i].remove((jj,v))
         else: 
            of += c[i][j]
            x[i] = j
            b[j] -= t[i][j]
            I.remove(i)

    I = dt.I
    best = (of,-1,-1,-1)
    stop = False
    while(stop == False):
       stop = True
       for i in I:
           for j in J:
              if x[i] != j:
                 dcap = b[j] - t[i][j]
                 if dcap  >= 0:
                    delta = c[i][j] - c[i][x[i]] 
                    if delta < 0:
                       stop = False
                       best = (of + delta,i,j,x[i])
       if stop == False:
          (of,i,j,oj) = best
          b[oj] += t[i][oj] 
          b[j] -= t[i][j]
          x[i] = j
    print("ub : {:.2f}".format(best[0]))
    return best[0],x
# ------------------------------ 
#
# ------------------------------ 
def read_data(fileName):
    if (os.path.isfile(fileName) == False):
       print('file {:s} not found'.format(fileName))
       sys.exit(-1)
    with open(fileName) as fl:
         dt = json.load(fl)
 
    dt = DotMap(dt) 
    dt.I = list(range(dt.ni))
    dt.J = list(range(dt.nj))
    dt.x = [0 for i in dt.I]
    dt.BigM = np.array(dt.c).sum()
    dt.c = np.array(dt.c)
    dt.t = np.array(dt.t)
    dt.b = np.array(dt.b)
    return dt

if __name__ == "__main__":
   main() 

