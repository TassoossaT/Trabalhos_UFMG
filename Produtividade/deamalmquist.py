import numpy as np
import sys
import pandas as pd
import os
from math import ceil,floor
import re
from math import ceil,floor
from mip import Model, xsum,  minimize, INTEGER,maximize,MAXIMIZE, MINIMIZE,CBC, OptimizationStatus, BINARY
from itertools import product
from dotmap import DotMap

EPS = 1e-3

def main():
   #assert len(sys.argv) == 2, 'please, provide a instance file'
   dt = DEAData(file_name='Produtividade\malmquist-data.csv')

   for p in dt.P:
      if p < dt.np - 1:
         Xcur,Ycur,Xnext,Ynext,names=dt.X[p],dt.Y[p],dt.X[p+1],dt.Y[p+1],dt.names
         panel = CCRIOMWModel(p,Xcur,Ycur,Xnext,Ynext,names)
         panel.run(data_type = 'current')
         panel.run(data_type = 'next')
         panel.run_cross_periods(cross_type = 'cur2next')
         panel.run_cross_periods(cross_type = 'next2cur')
         panel.print_solution()

class DEAData():
      def __init__(self,file_name): 
         self.file_name = file_name
         self.X = {}
         self.Y = {}
         self.names = None
         self.df = None
         self.read_csv()

      def to_latex(self,df,filename):
         if df is not None:
            with open(filename,'w') as wf:
               tex = df.to_latex(buf=wf,index=False)
               print(f'{filename} generated')

      def read_csv(self):
         assert os.path.isfile(self.file_name), f'file {self.file_name} not found'
         
         df = pd.read_csv(self.file_name)
         self.to_latex(df,'panel.tex')

         periods = df['periods'].unique()
         periods.sort()

         columns = df.columns[3:]
         
         # dealing with bad output
         maxO2 = df['Y2'].max()
         meanO2 = df['Y2'].mean()
         dfmean = df[columns]/df[columns].mean()
         dfmean['Y2'] = ceil(maxO2/meanO2) - dfmean['Y2'] 

         dfmean['name'] = df['name']
         dfmean['dmu'] = df['dmu']
         dfmean['periods'] = df['periods'] 

         I = [ val for val in columns if re.match(r'[X]\d',val)]
         O = [ val for val in columns if re.match(r'[Y]\d',val)]

         for h,p in enumerate(periods):
            X = dfmean[dfmean['periods'] == p][I].to_numpy()
            self.X.update({h:X})
            Y = dfmean[dfmean['periods'] == p][O].to_numpy()
            self.Y.update({h:Y})

         names = df['name'].unique().tolist()
         self.names = names

         self.ni,self.no,self.nd,self.np = len(I),len(O),len(names),len(periods) 
         self.P,self.I,self.O,self.D,self.P = range(self.np),range(self.ni),range(self.no),range(self.nd),range(self.np)
         
         self.df = dfmean

class CCRIOMWModel():
   def __init__(self, p,Xcur,Ycur, Xnext, Ynext,names):
      self.names = names 
      self.p = p
      self.I,self.O,self.D=range(len(Xcur[0])),range(len(Ycur[0])),range(len(Xcur))
      self.Xcur,self.Ycur=Xcur,Ycur
      self.Xnext,self.Ynext=Xnext,Ynext
      self.create_model_cur()
      self.create_model_next()
      self.is_ok = False

      self.solution = {d : DotMap({'name': names[d], 'tt' : 0.0, 'tt1':0.0,'t1t':0.0,'t1t1':0.0}) for d in self.D }

   def create_model_cur(self):
      Xcur,Ycur,names=self.Xcur,self.Ycur,self.names
      I,O,D=self.I,self.O,self.D

      m = Model('CCRIOMWcur',sense=MAXIMIZE,solver_name=CBC)
      u = [m.add_var(lb=EPS,var_type='C',obj=0,name='u(%d)' % (i)) for i in I]
      v = [m.add_var(lb=EPS,var_type='C',obj=0,name='v(%d)' % (o)) for o in O]

      m.objective = xsum(v[o] for o in O)
      m.verbose = 0
      for dmu in D: 
            m += xsum(Ycur[dmu][o] * v[o] for o in O) \
               - xsum(Xcur[dmu][i] * u[i] for i in I) <= 0, 'dmu(%d)'% (dmu)
      self.mcur,self.ucur,self.vcur = m,u,v
      #m.write('m.lp')

   def create_model_next(self):
      Xnext,Ynext,names=self.Xnext,self.Ynext,self.names
      I,O,D=self.I,self.O,self.D

      m = Model('CCRIOMWnext',sense=MAXIMIZE,solver_name=CBC)
      u = [m.add_var(lb=EPS,var_type='C',obj=0,name='u(%d)' % (i)) for i in I]
      v = [m.add_var(lb=EPS,var_type='C',obj=0,name='v(%d)' % (o)) for o in O]

      m.objective = xsum(v[o] for o in O)
      m.verbose = 0
      for dmu in D: 
            m += xsum(Ynext[dmu][o] * v[o] for o in O) \
               - xsum(Xnext[dmu][i] * u[i] for i in I) <= 0, 'dmu(%d)'% (dmu)
      self.mnext,self.unext,self.vnext = m,u,v
      #m.write('m.lp')

   def run_cross_periods(self,cross_type = 'cur2next'):
      Xnext,Ynext=self.Xnext,self.Ynext
      Xcur,Ycur,names=self.Xcur,self.Ycur,self.names
      I,O,D=self.I,self.O,self.D
      if cross_type == 'cur2next':
         m,u,v = self.mnext,self.unext,self.vnext
      else:
         m,u,v = self.mcur,self.ucur,self.vcur

      for d in D:
            if cross_type == 'cur2next':
               m.objective = xsum(Ycur[d][o] * v[o] for o in O)
               nc = m.add_constr(xsum(Xcur[d][i] * u[i] for i in I) == 1, name='norm_constr')
            else:
               m.objective = xsum(Ynext[d][o] * v[o] for o in O)
               nc = m.add_constr(xsum(Xnext[d][i] * u[i] for i in I) == 1, name='norm_constr')

            status = m.optimize()
            if status == OptimizationStatus.OPTIMAL:
               # guardo a eficiencia obtida para dmu d
               sol = self.solution[d]
               if cross_type == 'cur2next':
                  sol.t1t  = m.objective_value
               else:
                  sol.tt1  = m.objective_value
            else:
               print(f"Error solving CCRIOMW model for DMU {d} ")
               sys.exit()

            m.remove(nc)
      self.is_ok = True

   def run(self,data_type = 'current'):
      I,O,D=self.I,self.O,self.D
      if data_type == 'current':
         X,Y,names=self.Xcur,self.Ycur,self.names
         m,u,v = self.mcur,self.ucur,self.vcur
      else:
         X,Y,names=self.Xnext,self.Ynext,self.names
         m,u,v = self.mnext,self.unext,self.vnext

      for d in D:
            m.objective = xsum(Y[d][o] * v[o] for o in O)
            nc = m.add_constr(xsum(X[d][i] * u[i] for i in I) == 1, name='norm_constr')
            status = m.optimize()

            #m.write('run.lp')

            if status == OptimizationStatus.OPTIMAL:
               # guardo a eficiencia obtida para dmu d
               sol = self.solution[d]
               if data_type == 'current':
                  sol.tt = m.objective_value
               else:
                  sol.t1t1  = m.objective_value
            else:
               print(f"Error solving model for DMU {d} ")
               sys.exit()

            m.remove(nc)
      self.is_ok = True

   def print_solution(self):
      D=self.D
      if self.is_ok == True:
            print(f'{self.p:3d} {self.p+1:3d}:')
            print('{:3s} '.format('dmu'),end='')
            print('{:20s} '.format('name'),end='')
            print('{:10s} '.format('tt'),end='')
            print('{:10s} '.format('tt1'),end='')
            print('{:10s} '.format('t1t'),end='')
            print('{:10s} '.format('t1t1'),end='')
            print()
            for d in D:
               sol = self.solution[d]
               print(f'{d+1:3d} ',end='')
               print(f'{self.names[d][:20]:20s} ',end='')
               print(f'{sol.tt:10.8f} ',end='')
               print(f'{sol.tt1:10.8f} ',end='')
               print(f'{sol.t1t:10.8f} ',end='')
               print(f'{sol.t1t1:10.8f} ',end='')
               print()
   def malquist(self):
      D = self.D
      malquist = {d: {'malquist': 0.0} for d in D}
      if self.is_ok == True:
         for d in D:
               sol = self.solution[d]
               malquist[d]['malquist'] = ((sol.tt1 * sol.t1t1) / (sol.tt * sol.t1t)) ** 0.5
      df = pd.DataFrame([( m['malquist']) for m in malquist.values()], columns=[ 'Malquist'])
      return df
   def AT(self):
      D = self.D
      AT = {d: {'AT': 0.0} for d in D}
      if self.is_ok == True:
         for d in D:
               sol = self.solution[d]
               AT[d]['AT'] = sol.t1t1*sol.tt
      df = pd.DataFrame([( m['AT']) for m in AT.values()], columns=[ 'AT'])
      return df
   def MF(self):
      D = self.D
      MF = {d: {'AT': 0.0} for d in D}
      if self.is_ok == True:
         for d in D:
               sol = self.solution[d]
               MF[d]['MF'] =((sol.tt*sol.tt1) / (sol.t1t * sol.t1t1))**0.5
      df = pd.DataFrame([( m['MF']) for m in MF.values()], columns=[ 'MF'])
      return df
   def at_mf_malq(self):
      D=self.D
      if self.is_ok == True:
            print(f'{self.p:3d} {self.p+1:3d}:')
            print('{:3s} '.format('dmu'),end='')
            print('{:20s} '.format('name'),end='')
            print('{:10s} '.format('AT'),end='')
            print('{:10s} '.format('MF'),end='')
            print('{:10s} '.format('malquist'),end='')
            print()
            for d in D:
               sol = self.solution[d]
               AT = sol.t1t1*sol.tt
               MF = ((sol.tt*sol.tt1) / (sol.t1t * sol.t1t1))**0.5
               malquist = ((sol.tt1*sol.t1t1) / (sol.tt * sol.t1t))**0.5
               print(f'{d+1:3d} ',end='')
               print(f'{self.names[d][:20]:20s} ',end='')
               print(f'{AT:10.8f} ',end='')
               print(f'{MF:10.8f} ',end='')
               print(f'{malquist:10.8f} ',end='')
               print()
if __name__ == "__main__":
   main()
