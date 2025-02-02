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
from mip import Model, xsum, maximize, minimize, CBC, MAXIMIZE, MINIMIZE,OptimizationStatus, BINARY
# ------------------------------ 
#
# ------------------------------ 
same_limit = 10
h_limit = 500
# ------------------------------ 
#
# ------------------------------ 
def main(sys):
   # Estrutura dos dados
   gaps = {
      "gap1": {"1": 336 , "2": 327  , "3": 339  , "4": 341  , "5": 326  },
      "gap2": {"1": 434 , "2": 436  , "3": 420  , "4": 419  , "5": 428  },
      "gap3": {"1": 580 , "2": 564  , "3": 573  , "4": 570  , "5": 564  },
      "gap4": {"1": 656 , "2": 644  , "3": 673  , "4": 647  , "5": 664  },
      "gap5": {"1": 563 , "2": 558  , "3": 564  , "4": 568  , "5": 559  },
      "gap6": {"1": 761 , "2": 759  , "3": 758  , "4": 752  , "5": 747  },
      "gap7": {"1": 942 , "2": 949  , "3": 968  , "4": 945  , "5": 951  },
      "gap8": {"1": 1133, "2": 1134 , "3": 1141 , "4": 1117 , "5": 1127 },
      "gap9": {"1": 709 , "2": 717  , "3": 712  , "4": 723  , "5": 706  },
      "gap10":{"1": 958 , "2": 963  , "3": 960  , "4": 947  , "5": 947  },
      "gap11":{"1": 1139, "2": 1178 , "3": 1195 , "4": 1171 , "5": 1171 },
      "gap12":{"1": 1451, "2": 1449 , "3": 1433 , "4": 1447 , "5": 1446 }
}

   datas = open_atri(r'gap\files.lst','gap')
   alpha = 0.5
   beta = 0.5
   it = 0
   for data in datas:
      it+=1
      p = 0
      for problem in data:
         p+=1
         print(f'resolvendo o problema {p} para a data {it}\n')
         ub = gaps[problem.gap][problem.problem]
         #print("Usando a função lag_rel_assignment\n")
         #lag_rel_assignment(problem,ub)
         #print("Usando a função lag_rel_knapsack\n")
         #lag_rel_knapsack(problem,ub)
         print("Usando meu codigo \n")
         iterations, total_time, final_gap = lagrangian_decomposition(problem, alpha, beta, ub)
         print(f"Total de iterações: {iterations}")
         print(f"Tempo total: {total_time:.2f} segundos")
         print(f"Gap final: {final_gap:.2f}%")
# ------------------------------ 
#
# ------------------------------ 
def lag_rel_assignment(dt,ub):
   print("Dualizing assignment constraints")
   J,I = dt.J,dt.I
   c,b,t = dt.c,dt.b,dt.t
   stop = False

   same = 0
   lb = 0.0 
   mu = 2.0
   h = 0
   
   u = [min([c[i][j] for j in J]) for i in I]
   #u = [0.0 for i in I]
   gap = 100.0
   while (stop == False): 
      ua = u 
      #solving Lagrangian problem
      #x = [[0 for j in J] for i in I]
      grad = [1 for i in I]
      infimum = sum(u)
      for j in J:
         w = [(c[i][j] - u[i])  for i in I]
         s = [t[i][j] for i in I]
         of,_x = knapsack(w,s,b[j])
         infimum += of
         for i in _x:
            grad[i] -= 1
            #x[i][j] = 1 

      if (lb < infimum):
         lb = infimum
         same = 0 
      else:
            same += 1 

      if (same > same_limit):
            mu = mu / 2.0
            same = 0

      # sub gradient
      norm = sum([grad[i]**2 for i in I])

      gap = 100.0 * (ub - lb) / ub
      h += 1       

      if (norm < 0.001) or (mu < 0.005) or (h > h_limit) or (gap < 0.001): 
         stop = True
      else:
         # solving dual Lagrangian problem
         step = mu * (ub - lb)/norm
         u = [u[i] + step * grad[i] for i in I] 
         ax = [ abs(v1 - v2) for v1,v2 in zip(u,ua) ]
         if (sum(ax)  < 0.0001):
            stop = True
      print_stats(h,ub,infimum,lb,gap,mu,norm)

def knapsack(w,s,b):
   n = len(w)
   N = range(n)
   mod = Model('knapsack',sense=MINIMIZE,solver_name=CBC)
   mod.verbose = 0
   x = [mod.add_var(var_type=BINARY,obj=w[i]) for i in N] 
   mod += xsum(s[i] * x[i] for i in N) <= b
   mod.optimize() 
   of = mod.objective_value
   x = [i for i,v in enumerate(x) if v.x > 0.9] 
   return (of,x)
# ------------------------------ 
#
# ------------------------------ 
def lag_rel_knapsack(dt,ub):
   print("Dualizing knapsack constraints")
   J,I = dt.J,dt.I
   c,b,t = dt.c,dt.b,dt.t
   stop = False

   same = 0
   lb = 0.0 
   mu = 2.0
   h = 0
   v = [0.0  for j in J]
   gap = 100.0
   while (stop == False): 
      va = v 
      #solving Lagrangian problem
      #x = [[0 for j in J] for i in I]
      grad = [-b[j] for j in J]
      infimum = -sum([ b[j] * v[j] for j in J ])
      for i in I:
         of,j = min([( (c[i][j] + v[j] * t[i][j]), j) for j in J], key = lambda t : t[0])
         infimum += of
         grad[j] += t[i][j]
         #x[i][j] = 1 
      if (lb < infimum):
         lb = infimum
         same = 0 
      else:
         same += 1 
      if (same > same_limit):
         mu = mu / 2.0
         same = 0
      # sub gradient
      norm = sum([grad[j]**2 for j in J])
      gap = 100.0 * (ub - lb) / ub
      h += 1       
      if (norm < 0.0001) or (mu < 0.0005) or (h > h_limit) or (gap < 0.0001): 
         stop = True
      else:
         # solving dual Lagrangian problem
         step = mu * (ub - lb)/norm
         v = [max(v[j] + step * grad[j],0.0) for j in J] 
         ax = [ abs(v1 - v2) for v1,v2 in zip(v,va) ]
         if (sum(ax)  < 0.000001):
            stop = True
      print_stats(h,ub,infimum,lb,gap,mu,norm)

def linear_gap(dt):
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
   # print(I,J)
   # print(L[1][0][1])
   #print(len(c),(len(c[0])))
   #print(len(L),len(L[0]),len(L[0][0]))
   x = [ -1 for i in I]
   of = 0.0
   it = 0
   while len(I) > 0:
         it += 1
         print(it,'\n')
         if it == 18:
            print(i)
         for i in I:
            print(len(L[i]))
            print(i,L[i][0])
         print()
         # print(len(I))
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
   return best[0]
# ------------------------------ 
#
# ------------------------------ 
def print_stats(h,ub,infimum,lb,gap,mu,norm):
    print("{:4d} ".format(h), end = '')
    print("{:12,.2f} ".format(ub),end = '')
    print("{:12,.2f} ".format(infimum),end = '')
    print("{:12,.2f} ".format(lb),end = '')
    print("{:12,.2f} %".format(gap),end = '')
    print("{:12,.8f} ".format(mu),end = '')
    print("{:12,.2f} ".format(norm,end = ''))
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
    dt.I = list(range(dt["ni"]))
    dt.J = list(range(dt["nj"]))
    dt.x = [0 for i in dt.I]
    return dt



def lagrangian_decomposition(dt, alpha, beta, ub):
   J, I = dt.J, dt.I
   c, b, t = dt.c, dt.b, dt.t
   same=0
   lambda_ij = [[c[i][j]/(len(I)*len(J)) for j in J] for i in I]
   lambda_ij = [[1 for j in J] for i in I]
   mu = 2.0  # Tamanho do passo inicial
   #ub = mth(dt)
   lb = -float('inf')
   gap = float('inf')
   h = 0

   stop = False
   def solve_subproblem_x(lambda_ij):
      model = Model(sense=MINIMIZE)
      model.verbose = 0
      x = [[model.add_var(var_type=BINARY) for j in J] for i in I]
      for j in J:
          model += xsum(t[i][j] * x[i][j] for i in I) <= b[j]
      model.objective = xsum((alpha * c[i][j] - lambda_ij[i][j]) * x[i][j] for i in I for j in J)
      model.optimize()
      return model, x

   def solve_subproblem_y(lambda_ij):
      # y = [[0 for j in J] for i in I]
      # for i in I:
      #    model,j = min([((beta *c[i][j] + lambda_ij[i][j]), j) for j in J], key = lambda t : t[0])
      #    y[i][j] = 1
      model = Model(sense=MINIMIZE)
      model.verbose = 0
      y = [[model.add_var(var_type=BINARY) for j in J] for i in I]
      for i in I:
         model += xsum(y[i][j] for j in J) == 1
      model.objective = minimize(xsum((beta * c[i][j] + lambda_ij[i][j]) * y[i][j] for i in I for j in J))
      model.optimize()
      return model, y
   
   start_time = time()
   while not stop:
      subgradient = [[0.0 for j in J] for i in I]
      infimum = sum(lambda_ij[i][j] for i in I for j in J)
      model_x, x = solve_subproblem_x(lambda_ij)
      model_y, y = solve_subproblem_y(lambda_ij)
      infimum += model_x.objective_value + model_y.objective_value
      for i in I:
         for j in J:
            subgradient[i][j] =  (y[i][j].x - x[i][j].x) # lambda_ij[i][j]
      #print(subgradient)
      if infimum > lb:
         lb = infimum
      elif lb < infimum:
         lb = infimum
         same = 0 
      else:
         same += 1 
      if (same > same_limit):
         mu = mu / 2.0
         same = 0
         

      norm = sum([subgradient[i][j]**2 for i in I for j in J])
      gap = 100.0 * (ub - lb) / ub
      h += 1       
      if (norm < 0.0001) or (mu < 0.0005) or (h > h_limit) or (gap < 0.0001): 
         print(norm,mu,h,gap)
         stop = True
      else:
         step = mu * (ub - lb)/(norm*10)
         lambda_ij = [[(lambda_ij[i][j] + subgradient[i][j]*step) for j in J] for i in I] 
         # ax = [ abs(v1 - v2) for v1,v2 in zip(lambda_ij,u0) ]
         # if (sum(ax)  < 0.000001):
         #    stop = True
      print(f"Iteração: {h:4d}, {ub:5}, Lb: {lb:12f}, Gap: {gap:6f}%, Mu: {mu:2}, Norm: {norm:4}")
   total_time = time() - start_time
   return h, total_time, gap


def open_atri(file_list_path: str, path: str):
   with open(file_list_path) as file:
      filenames = file.readlines()
   all_data =[]
   for filename in filenames:
      with open(f'{path}\\{filename.strip()}.txt', 'r') as file:
         lines = file.readlines()
      p = int(lines[0].strip().split()[0])
      index = 1
      data_list = []
      for problem in range(p):
         dt = DotMap() 
         dt["problem"] = str(problem +1)
         dt["gap"] = filename.strip()
         n, m = map(int, lines[index].strip().split())
         dt["I"], dt["J"] = list(range(m)), list(range(n))
         index += 1
         c_elements = []
         while len(c_elements) < m * n:
            c_elements.extend(map(int, lines[index].strip().split()))
            index += 1
         dt["c"] = [c_elements[i * n:(i + 1) * n] for i in range(m)]
         aij_elements = []
         while len(aij_elements) < m * n:
            aij_elements.extend(map(int, lines[index].strip().split()))
            index += 1
         dt["t"] = [aij_elements[i * n:(i + 1) * n] for i in range(m)]
         dt["b"] = list(map(int, lines[index].strip().split()))
         index += 1
         data_list.append(dt)
      all_data.append(data_list)
   return all_data
if __name__ == "__main__":
   main(sys) 

