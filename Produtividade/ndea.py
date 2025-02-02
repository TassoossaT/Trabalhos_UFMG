import numpy as np
from mip import Model, xsum,  minimize, INTEGER,maximize,MAXIMIZE, MINIMIZE,CBC, OptimizationStatus, BINARY
import sys
import pandas as pd
import os
import re
from math import ceil,floor
'''
DEA models for extended two-stage network structures
Yongjun Li a, Yao Chen b, Liang Liang a, Jianhui Xie
Omega 40 (2012) 611–618


Network Data Envelopment Analysis: Foundations and Extensions
Second Edition

Chiang Kao
Chapter 11.3.2  Efﬁciency Aggregation
page 263

'''
def main():
    #data = open('Produtividade\labx.csv')
    #assert len(sys.argv) == 2, 'please, provide a instance file'
    dt = DEAData('Produtividade\labx.csv')

    #dt.to_latex()
    ts = NDEATwoStage(dt)
    ts.run()
    ts.print_solution()

    avg = WeightedAverageNDEA(dt)
    avg.run()
    avg.print_solution()

class WeightedAverageNDEA():
    def __init__(self, dt): 
        self.dt = dt
        self.create_model()
        self.is_ok = False

    def create_model(self):
        dt = self.dt
        I,II,O,OO,D = dt.I,dt.II,dt.O,dt.OO,dt.D

        m = Model('NDEATP10',sense=MAXIMIZE,solver_name=CBC)
        eps = 1e-5
        u = [m.add_var(lb=eps,var_type='C',obj=0,name='u(%d)' % (i)) for i in I]
        w = [m.add_var(lb=eps,var_type='C',obj=0,name='w(%d)' % (o)) for o in O]

        s = [m.add_var(lb=eps,var_type='C',obj=0,name='s(%d)' % (i)) for i in II]
        v = [m.add_var(lb=eps,var_type='C',obj=0,name='v(%d)' % (o)) for o in OO]

        m.objective = xsum(v[o] for o in OO)
        m.verbose = 0

        for d in D: 
            m += xsum(dt.Y[d][o] * w[o] for o in O) \
               - xsum(dt.X[d][i] * u[i] for i in I) <= 0, 'no1dmu(%d)'% (d)
            
        for d in D: 
            m += xsum(dt.YY[d][o] * v[o] for o in OO) \
               - xsum(dt.XX[d][i] * s[i] for i in II)\
               - xsum(dt.Y[d][o] * w[o] for o in O) <= 0, 'no2dmu(%d)'% (d)
        self.m,self.u,self.v,self.s,self.w = m,u,v,s,w
        self.eff = np.zeros((dt.nd,3),dtype=float)
        self.theta = np.zeros((dt.nd,2),dtype=float)
        #m.write('m.lp')

    def run(self):
        dt = self.dt
        I,II,O,OO,D = dt.I,dt.II,dt.O,dt.OO,dt.D
        m,u,v,s,w = self.m,self.u,self.v,self.s,self.w

        for d in D:
            m.objective = xsum(dt.YY[d][o] * v[o] for o in OO) + xsum(dt.Y[d][o] * w[o] for o in O)
            nc = m.add_constr(xsum(dt.X[d][i] * u[i] for i in I)\
                  + xsum(dt.XX[d][i] * s[i] for i in II)\
                  + xsum(dt.Y[d][o] * w[o] for o in O) == 1, name='norm_constr')
            #m.write('m.lp')
            status = m.optimize()

            if status == OptimizationStatus.OPTIMAL:
               # guardo a eficiencia obtida para dmu d
               self.eff[d][0]  = m.objective_value
               den =  sum(dt.X[d][i] * u[i].x for i in I)\
                    + sum(dt.XX[d][i] * s[i].x for i in II) \
                    + sum(dt.Y[d][o] * w[o].x for o in O) 
               theta1 = sum(dt.X[d][i] * u[i].x for i in I) / den
               theta2 = sum(dt.XX[d][i] * s[i].x for i in II) \
                        + sum(dt.Y[d][o] * w[o].x for o in O) / den 

               self.theta[d][0] = theta1
               self.theta[d][1] = theta2

               leff1 = sum(dt.Y[d][o] * w[o].x for o in O)/\
                       sum(dt.X[d][i] * u[i].x for i in I) 
               self.eff[d][1] = leff1
               
               leff2 = sum(dt.YY[d][o] * v[o].x for o in OO)/\
                      (sum(dt.XX[d][i] * s[i].x for i in II) \
                      + sum(dt.Y[d][o] * w[o].x for o in O) ) 
               self.eff[d][2] = leff2
            else:
               print(f"Error solving CCRIOMW model for DMU %d " %(d))
               sys.exit()

            m.remove(nc)
        self.is_ok = True
    
    def print_solution(self):
          if self.is_ok == True:
             dt = self.dt
             D = dt.D
             print()
             print('Weighted Average Model Efficiency ')
             print( '{:3s} '.format('dmu'),end='')
             print( '{:20s} '.format('names'),end='')
             print( '{:6s} '.format('global'),end='')
             print( '{:6s} '.format('E1'),end='')
             print('({:6s}) '.format('theta1'),end='')
             print ('{:6s} '.format('E2'),end='')
             print('({:6s}) '.format('theta2'),end='')
             print( '{:6s} '.format('E1 x E2'),end='')
             print()
             for d in D:
                 print(f'{d:3d} ',end='')
                 print(f'{self.dt.names[d][:20]:20s} ',end='')
                 print(f'{self.eff[d][0]:6.4f} ',end='')
                 print(f'{self.eff[d][1]:6.4f} ',end='')
                 print(f'({self.theta[d][0]:6.4f}) ',end='')
                 print(f'{self.eff[d][2]:6.4f} ',end='')
                 print(f'({self.theta[d][1]:6.4f}) ',end='')
                 print(f'{self.eff[d][1]*self.eff[d][2]:6.4f}',end='')
                 print()
class NDEATwoStage():
    def __init__(self,dt):
        self.dt = dt
        fs = NDEAMaxTheta(dt)
        fs.run()
        #fs.print_solution()
        self.fs = fs
        self.create_model() 
        self.is_ok = False

    def create_model(self):
        dt = self.dt
        I,II,O,OO,D = dt.I,dt.II,dt.O,dt.OO,dt.D
        m = Model('2ndStage',sense=MAXIMIZE,solver_name=CBC)
        eps = 0.0#1e-8
        u = [m.add_var(lb=eps,var_type='C',obj=0.0,name=f'u({i})') for i in I]
        w = [m.add_var(lb=eps,var_type='C',obj=0.0,name=f'w({o})') for o in O]
        q = [m.add_var(lb=eps,var_type='C',obj=0.0,name=f'q({i})') for i in II]
        v = [m.add_var(lb=eps,var_type='C',obj=0.0,name=f'v({o})') for o in OO]
        m.objective = xsum(v[o] for o in OO)
        m.verbose = 0
        for d in D:
            m += xsum(dt.Y[d][o] * w[o] for o in O) - xsum(dt.X[d][i] * u[i] for i  in I) <= 0, f'1st({d})'
        for d in D:
            m += xsum(dt.YY[d][o] * v[o] for o in OO)\
                 - xsum(dt.XX[d][i] * q[i] for i  in II)\
                 - xsum(dt.Y[d][o] * w[o] for o in O) <= 0, f'2st({d})'
        self.eff = np.zeros((dt.nd,3),dtype=float)
        self.m, self.u,self.w,self.q,self.v = m, u,w,q,v

    def run(self):
        dt = self.dt
        I,II,O,OO,D = dt.I,dt.II,dt.O,dt.OO,dt.D
        m,u,w,q,v = self.m,self.u,self.w,self.q,self.v
        maxtheta = self.fs.maxtheta
        for d in D:
            besttheta = -float('inf')
            bestobj   = -float('inf')
            nc0 = m.add_constr(xsum(dt.XX[d][i] * q[i] for i in II) + xsum(dt.Y[d][o] * w[o] for o in O) == 1, name='norm_constr2')

            Theta = np.flip(np.linspace(0,maxtheta[d],num=ceil(maxtheta[d]/1e-2)))
            h = 0
            for theta in Theta:
                #t = (maxtheta[d] - theta)
                t = theta
                m.objective = t * xsum(dt.YY[d][o] * v[o] for o in OO)
                nc1 = m.add_constr(xsum(dt.Y[d][o] * w[o] for o in O) - t * xsum(dt.X[d][i] * u[i] for i in I) == 0, name='norm_constr1')
                status = m.optimize()
                #m.write(f'm1st{d}.lp')
                if status == OptimizationStatus.OPTIMAL:
                    obj = m.objective_value 
                    if  bestobj < obj:
                        bestobj = obj
                        besttheta = theta
                    #else:
                    #    break
                else:
                    print(f"Error solving max theta for 1st stage model for DMU {d} ")
                    sys.exit()
                h += 1 
                m.remove(nc1)
            m.remove(nc0)
            self.eff[d][0] = bestobj 
            self.eff[d][1] = besttheta
            self.eff[d][2] = bestobj/besttheta
        self.is_ok = True

    def print_solution(self):
        if self.is_ok == True:
            print()
            print('Centralized Model Efficiency ')
            dt = self.dt
            D = dt.D
            print('{:3s} '.format('dmu'),end='')
            print('{:20s} '.format('names'),end='')
            print('{:10s} '.format('global'),end='')
            print('{:10s} '.format('E1'),end='')
            print('{:10s} '.format('E2'),end='')
            print('{:10s} '.format('E1 x E2'),end='')
            print()
            for d in D:
                print(f'{d:3d} ',end='')
                print(f'{self.dt.names[d][:20]:20s} ',end='')
                print(f'{self.eff[d][0]:10.8f} ',end='')
                print(f'{self.eff[d][1]:10.8f} ',end='')
                print(f'{self.eff[d][2]:10.8f} ',end='')
                print(f'{self.eff[d][1]*self.eff[d][2]:10.8f}',end='')
                print()

class NDEAMaxTheta():
      def __init__(self, dt):
          self.dt = dt
          self.create_model()

      def create_model(self):
          dt = self.dt
          I,II,O,OO,D = dt.I,dt.II,dt.O,dt.OO,dt.D

          m = Model('1stStage',sense=MAXIMIZE,solver_name=CBC)
          eps=0.0
          #eps=1e-8
          u = [m.add_var(lb=eps,var_type='C',obj=0.0,name=f'u({i})') for i in I]
          w = [m.add_var(lb=eps,var_type='C',obj=0.0,name=f'w({o})') for o in O]

          q = [m.add_var(lb=eps,var_type='C',obj=0.0,name=f'q({i})') for i in II]
          v = [m.add_var(lb=eps,var_type='C',obj=0.0,name=f'v({o})') for o in OO]

          m.objective = xsum(v[o] for o in OO)
          m.verbose = 0
          for d in D:
              m += xsum(dt.Y[d][o] * w[o] for o in O) - xsum(dt.X[d][i] * u[i] for i  in I) <= 0, f'1st({d})'

          for d in D:
              m += xsum(dt.YY[d][o] * v[o] for o in OO)\
                 - xsum(dt.XX[d][i] * q[i] for i  in II)\
                 - xsum(dt.Y[d][o] * w[o] for o in O) <= 0, f'2st({d})'

          self.maxtheta = np.zeros(dt.nd,dtype=float)
          self.m, self.u,self.w,self.q,self.v = m, u,w,q,v

      def run(self):
          dt = self.dt
          I,II,O,OO,D = dt.I,dt.II,dt.O,dt.OO,dt.D
          m,u,w,q,v = self.m,self.u,self.w,self.q,self.v

          for d in D:
              m.objective = xsum(dt.Y[d][o] * w[o] for o in O)
              nc = m.add_constr(xsum(dt.X[d][i] * u[i] for i in I) == 1, name='norm_constr')

              status = m.optimize()
              #m.write(f'm1st{d}.lp')
               
              if status == OptimizationStatus.OPTIMAL:
                 self.maxtheta[d] = m.objective_value 
              else:
                 print(f"Error solving max theta for 1st stage model for DMU {d} ")
                 sys.exit()
          
              m.remove(nc)

          self.is_ok = True

      def print_solution(self):
          if self.is_ok == True:
             print('Max theta')
             dt = self.dt
             D = dt.D
             for d in D:
                 print(f'{d:3d} {self.maxtheta[d]:10.8f}')

class DEAData():
      def __init__(self,file_name): 
        self.file_name = file_name
        self.X     = None
        self.XX    = None
        self.Y     = None
        self.YY    = None
        self.names = None
        self.df    = None
        self.read_csv()

      def to_latex(self):
          if self.df is not None:
             tex = self.df.to_latex(index=False)
             print(tex)
 
      def read_csv(self):
          assert os.path.isfile(self.file_name), f'file {self.file_name} not found'
          
          df = pd.read_csv(self.file_name)

          self.names = df['name'].to_list()
          columns = df.columns[2:]
          dfnorm = df[columns]/df[columns].mean()

          I  = [ val for val in columns if re.match(r'[X]\d',val)]
          II = [ val for val in columns if re.match(r'[X]{2}\d',val)]
          O  = [ val for val in columns if re.match(r'[Y]\d',val)]
          OO = [ val for val in columns if re.match(r'[Y]{2}\d',val)]
          

          self.ni,self.nii,self.no,self.noo,self.nd = len(I),len(II),len(O),len(OO),dfnorm.shape[0]
          self.I,self.II,self.O,self.OO,self.D = range(self.ni),range(self.nii),range(self.no),range(self.noo),range(self.nd)

          self.X  = dfnorm[I].to_numpy()
          self.XX = dfnorm[II].to_numpy()
          self.Y  = dfnorm[O].to_numpy()
          self.YY = dfnorm[OO].to_numpy()
          self.df = df

if __name__ == '__main__':
    main()



