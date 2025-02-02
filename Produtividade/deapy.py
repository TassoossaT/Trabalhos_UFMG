from mip import Model, xsum,  minimize, INTEGER,maximize,MAXIMIZE, MINIMIZE,CBC, OptimizationStatus, BINARY
from itertools import product
import sys
from pprint import pp
from prettytable import PrettyTable as PT
from dotmap import DotMap
EPS = 1e-6
class DEAData():
      def __init__(self): 
          self.dmu_names = None
          self.input_names = None
          self.output_name = None
          self.input_values = None
          self.output_values = None

      def print(self):
          print(f" %10s " % (' '),end='')
          for iname in self.input_names:
              print(f" %10s " % (iname[:8]),end='')

          for oname in self.output_names:
              print(f" %10s " % (oname[:8]),end='')

          print()
          for idmu,dmuname in enumerate(self.dmu_names):
              print(f" %10s :" % (dmuname),end='')

              for jinput,inputname in enumerate(self.input_names):
                  print(f" %10.2f " % (self.input_values[idmu][jinput]),end='')

              for joutput,outputname in enumerate(self.output_names):
                  print(f" %10.2f " % (self.output_values[idmu][joutput]),end='')

              print()

class CCRIOMWModel():
    def __init__(self, data : DEAData):
        self.data = data
        self.create_model()
        self.is_ok = False
    def create_model(self):
        data = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))

        self.solution = {d : DotMap({'dmu_name': data.dmu_names[d],\
                'efficiency' : 0.0,\
                'input_weight' : [0.0 for i in I],\
                'output_weight' : [0.0 for o in O] }) for d in D }

        m = Model('CCRIOMW',sense=MAXIMIZE,solver_name=CBC)
        m.max_seconds = 30000
        
        u = [m.add_var(lb=EPS,var_type='C',obj=0,name='u(%d)' % (i)) for i in I]
        v = [m.add_var(lb=EPS,var_type='C',obj=0,name='v(%d)' % (o)) for o in O]

        m.objective = xsum(v[o] for o in O)
        m.verbose = 0
        for dmu in D: 
            m += xsum(data.output_values[dmu][o] * v[o] for o in O) \
               - xsum(data.input_values[dmu][i] * u[i] for i in I) <= 0, 'dmu(%d)'% (dmu)
        self.m,self.u,self.v = m,u,v
        #m.write('m.lp')
    
    def run(self):
        data = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))
        m,u,v = self.m,self.u,self.v
        for d in D:
            m.objective = xsum(data.output_values[d][o] * v[o] for o in O)
            nc = m.add_constr(xsum(data.input_values[d][i] * u[i] for i in I) == 1, name='norm_constr')
            status = m.optimize()
            #m.write('m%d.lp'%(d))
            if status == OptimizationStatus.OPTIMAL:
               # guardo a eficiencia obtida para dmu d
               sol = self.solution[d]
               sol.efficiency  = m.objective_value
               for i in I:
                   # guardo os valores dos pesos de input
                   sol.input_weight[i] = u[i].x
               for o in O:
                   # guardo dos valores dos pesos de output
                   sol.output_weight[o] = v[o].x
            else:
               print(f"Error solving CCRIOMW model for DMU %d " %(d))
               sys.exit()

            m.remove(nc)
        self.is_ok = True
    
    def print_solution(self):
        if self.is_ok == True:
            data = self.data
            I = range(len(data.input_names))
            O = range(len(data.output_names))
            D = range(len(data.dmu_names))
            tb = PT()
            # cabecalho da tabela
            input_weight_names = [ 'u(%d)' % (i) for i in I]
            output_weight_names = [ 'v(%d)' % (o) for o in O]
            for o in output_weight_names: 
                tb.float_format[o] = '8.3'
            for i in input_weight_names: 
                tb.float_format[i] = '8.3'
            tb.float_format['Ef'] = '8.3'

            tb.field_names = ['DMU']\
                    + data.input_names\
                    + data.output_names\
                    + ['Ef']\
                    + input_weight_names\
                    + output_weight_names
               
            for d,v in self.solution.items():
                row = [data.dmu_names[d]]\
                      + data.input_values[d]\
                      + data.output_values[d]\
                      + [v.efficiency]\
                      + v.input_weight\
                      + v.output_weight
                tb.add_row(row)
            print(tb)

class CCROOMWModel():
    def __init__(self, data : DEAData):
        self.data = data
        self.create_model()
        self.is_ok = False
    def create_model(self):
        data = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))

        self.solution = {d : DotMap({'dmu_name': data.dmu_names[d],\
                'inverse_efficiency' : 0.0,\
                'input_weight' : [0.0 for i in I],\
                'output_weight' : [0.0 for o in O] }) for d in D }

        m = Model('CCROOMW',sense=MINIMIZE,solver_name=CBC)
        u = [m.add_var(lb=EPS,var_type='C',obj=0,name='u(%d)' % (i)) for i in I]
        v = [m.add_var(lb=EPS,var_type='C',obj=0,name='v(%d)' % (o)) for o in O]

        m.objective = xsum(u[i] for i in I)
        m.verbose = 0
        for dmu in D: 
            m += xsum(data.output_values[dmu][o] * v[o] for o in O) \
               - xsum(data.input_values[dmu][i] * u[i] for i in I) <= 0, 'dmu(%d)'% (dmu)
        self.m,self.u,self.v = m,u,v
        #m.write('m.lp')
    
    def run(self):
        data = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))
        m,u,v = self.m,self.u,self.v
        for d in D:
            m.objective = xsum(data.input_values[d][i] * u[i] for i in I)
            nc = m.add_constr(xsum(data.output_values[d][o] * v[o] for o in O) == 1, name='norm_constr')
            status = m.optimize()
            #m.write('m%d.lp'%(d))
            if status == OptimizationStatus.OPTIMAL:
               # guardo a eficiencia obtida para dmu d
               sol = self.solution[d]
               sol.inverse_efficiency  = m.objective_value
               for i in I:
                   # guardo os valores dos pesos de input
                   sol.input_weight[i] = u[i].x
               for o in O:
                   # guardo dos valores dos pesos de output
                   sol.output_weight[o] = v[o].x
            else:
               print(f"Error solving CCROOMW model for DMU %d " %(d))
               sys.exit()

            m.remove(nc)
        self.is_ok = True
    
    def print_solution(self):
        if self.is_ok == True:
            data = self.data
            I = range(len(data.input_names))
            O = range(len(data.output_names))
            D = range(len(data.dmu_names))
            tb = PT()
            # cabecalho da tabela
            input_weight_names = [ 'u(%d)' % (i) for i in I]
            output_weight_names = [ 'v(%d)' % (o) for o in O]
            for o in output_weight_names: 
                tb.float_format[o] = '8.3'
            for i in input_weight_names: 
                tb.float_format[i] = '8.3'
            tb.float_format['InvEf'] = '8.3'
            tb.float_format['Ef'] = '8.3'

            tb.field_names = ['DMU']\
                    + data.input_names\
                    + data.output_names\
                    + ['InvEf']\
                    + ['Ef']\
                    + input_weight_names\
                    + output_weight_names
               
            for d,v in self.solution.items():
                row = [data.dmu_names[d]]\
                      + data.input_values[d]\
                      + data.output_values[d]\
                      + [v.inverse_efficiency]\
                      + [1/v.inverse_efficiency]\
                      + v.input_weight\
                      + v.output_weight
                tb.add_row(row)
            print(tb)

class CCRIOENVModel():
    def __init__(self, data : DEAData):
        self.data = data
        self.create_model()
        self.is_ok = False
    def create_model(self):
        data = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))

        self.solution = {d : DotMap({'dmu_name': data.dmu_names[d],\
                'efficiency' : 0.0,\
                'llambda' : [0.0 for d in D]}) for d in D }

        m = Model('CCRIOENV',sense=MINIMIZE,solver_name=CBC)
        theta = m.add_var(var_type='C',obj=1.0,name='theta') 
        ll = [m.add_var(lb=0.0,var_type='C',obj=0,name='ll(%d)' % (d)) for d in D]

        m.objective = theta 
        m.verbose = 0
        self.m,self.ll,self.theta = m,ll,theta
        #m.write('m.lp')
    
    def run(self):
        data = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))
        m,ll,theta = self.m,self.ll,self.theta
        for r in D:
            cnstrs = []
            for i in I:
                cnstrs.append(m.add_constr( xsum( data.input_values[d][i] * ll[d] for d in D ) <= data.input_values[r][i] * theta,name='input_cnstr(%d)'%(i)))
            for o in O:
                cnstrs.append(m.add_constr( xsum( data.output_values[d][o] * ll[d] for d in D ) >= data.output_values[r][o],name='output_cnstr(%d)'%(o)))
            status = m.optimize()
            #m.write('m%d.lp'%(r))
            if status == OptimizationStatus.OPTIMAL:
               # guardo a eficiencia obtida para dmu r
               sol = self.solution[r]
               sol.efficiency  = m.objective_value
               for d in D:
                   # guardo os valores dos lambdas 
                   sol.llambda[d] = ll[d].x
            else:
               print(f"Error solving CCRIOENV model for DMU %d " %(r))
               sys.exit()

            for cc in cnstrs:                  
                m.remove(cc)
        self.is_ok = True
    
    def print_solution(self):
        if self.is_ok == True:
            data = self.data
            I = range(len(data.input_names))
            O = range(len(data.output_names))
            D = range(len(data.dmu_names))
            tb = PT()
            # cabecalho da tabela
            for d in data.dmu_names: 
                tb.float_format[d] = '8.3'
            tb.float_format['Ef'] = '8.3'
            tb.field_names = ['DMU']\
                    + data.input_names\
                    + data.output_names\
                    + ['Ef']\
                    + data.dmu_names
               
            for d,v in self.solution.items():
                row = [data.dmu_names[d]]\
                      + data.input_values[d]\
                      + data.output_values[d]\
                      + [v.efficiency]\
                      + v.llambda
                tb.add_row(row)
            print(tb)

class CCROOENVModel():
    def __init__(self, data : DEAData):
        self.data = data
        self.create_model()
        self.is_ok = False
    def create_model(self):
        data = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))

        self.solution = {d : DotMap({'dmu_name': data.dmu_names[d],\
                'inverse_efficiency' : 0.0,\
                'llambda' : [0.0 for d in D]}) for d in D }

        m = Model('CCROOENV',sense=MAXIMIZE,solver_name=CBC)
        theta = m.add_var(var_type='C',obj=1.0,name='theta') 
        ll = [m.add_var(lb=0.0,var_type='C',obj=0.0,name='ll(%d)' % (d)) for d in D]

        m.objective = theta 
        m.verbose = 0
        self.m,self.ll,self.theta = m,ll,theta
        #m.write('m.lp')
    
    def run(self):
        data = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))
        m,ll,theta = self.m,self.ll,self.theta
        for r in D:
            cnstrs = []
            for i in I:
                cnstrs.append(m.add_constr( xsum( data.input_values[d][i] * ll[d] for d in D ) <= data.input_values[r][i],name='input_cnstr(%d)'%(i)))
            for o in O:
                cnstrs.append(m.add_constr( xsum( data.output_values[d][o] * ll[d] for d in D ) >= data.output_values[r][o]*theta,name='output_cnstr(%d)'%(o)))
            status = m.optimize()
            #m.write('m%d.lp'%(r))
            if status == OptimizationStatus.OPTIMAL:
               # guardo a eficiencia obtida para dmu r
               sol = self.solution[r]
               sol.inverse_efficiency  = m.objective_value
               for d in D:
                   # guardo os valores dos lambdas 
                   sol.llambda[d] = ll[d].x
            else:
               print(f"Error solving CCRIOENV model for DMU %d " %(r))
               sys.exit()

            for cc in cnstrs:                  
                m.remove(cc)
        self.is_ok = True
    
    def print_solution(self):
        if self.is_ok == True:
            data = self.data
            I = range(len(data.input_names))
            O = range(len(data.output_names))
            D = range(len(data.dmu_names))
            tb = PT()
            # cabecalho da tabela
            for d in data.dmu_names: 
                tb.float_format[d] = '8.3'
            tb.float_format['InvEf'] = '8.3'
            tb.float_format['Ef'] = '8.3'
            tb.field_names = ['DMU']\
                    + data.input_names\
                    + data.output_names\
                    + ['InvEf']\
                    + ['Ef']\
                    + data.dmu_names
               
            for d,v in self.solution.items():
                row = [data.dmu_names[d]]\
                      + data.input_values[d]\
                      + data.output_values[d]\
                      + [v.inverse_efficiency]\
                      + [1/v.inverse_efficiency]\
                      + v.llambda
                tb.add_row(row)
            print(tb)

class CCRIOSENVModel():
    def __init__(self, data : DEAData):
        self.data = data
        self.create_model()
        self.is_ok = False
    def create_model(self):
        data = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))

        self.solution = {d : DotMap({'dmu_name': data.dmu_names[d],\
                'efficiency' : 0.0,\
                'llambda' : [0.0 for d in D],\
                'slack_inputs': [0.0 for i in I],\
                'slack_outputs' : [0.0 for o in O]}) for d in D }

        m = Model('CCRIOSENV',sense=MINIMIZE,solver_name=CBC)
        theta =      m.add_var(var_type='C',obj=1.0,name='theta') 
        ll = [m.add_var(lb=0.0,var_type='C',obj=0,  name='ll(%d)' % (d)) for d in D]
        si = [m.add_var(lb=0.0,var_type='C',obj=0,  name='si(%d)' % (i)) for i in I]
        so = [m.add_var(lb=0.0,var_type='C',obj=0,  name='so(%d)' % (o)) for o in O]

        m.verbose = 0
        self.m,self.ll,self.theta,self.si,self.so = m,ll,theta,si,so
        #m.write('m.lp')
    
    def run(self):
        e = 1e-3
        data = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))
        m,ll,theta,si,so = self.m,self.ll,self.theta,self.si,self.so
        for r in D:
            m.objective = theta - e * (xsum( si[i] for i in I) + xsum( so[o] for o in O))
            cnstrs = []
            for i in I:
                cnstrs.append(m.add_constr( xsum( data.input_values[d][i] * ll[d] for d in D ) - data.input_values[r][i] * theta + si[i] == 0.0,name='input_cnstr(%d)'%(i)))
            for o in O:
                cnstrs.append(m.add_constr( xsum( data.output_values[d][o] * ll[d] for d in D ) - so[o] == data.output_values[r][o],name='output_cnstr(%d)'%(o)))
            status = m.optimize()
            #m.write('m%d.lp'%(r))
            if status == OptimizationStatus.OPTIMAL:
               # guardo a eficiencia obtida para dmu r
               sol = self.solution[r]
               sol.efficiency  = m.objective_value
               for d in D:
                   # guardo os valores dos lambdas 
                   sol.llambda[d] = ll[d].x
               for i in I:
                   sol.slack_inputs[i] = si[i].x
               for o in O:
                   sol.slack_outputs[o] = so[o].x
            else:
               print(f"Error solving CCRIOSENV model for DMU %d " %(r))
               sys.exit()

            for cc in cnstrs:                  
                m.remove(cc)
        self.is_ok = True
    
    def print_solution(self):
        if self.is_ok == True:
            data = self.data
            I = range(len(data.input_names))
            O = range(len(data.output_names))
            D = range(len(data.dmu_names))
            tb = PT()
            # cabecalho da tabela
            for d in data.dmu_names: 
                tb.float_format[d] = '8.3'
            tb.float_format['Ef'] = '8.3'
            slack_input_names = ['si(%d)' % (i) for i in I]
            slack_output_names = ['so(%d)' % (o) for o in O]
            for name in slack_input_names:
                tb.float_format[name] = '8.3'
            for name in slack_output_names:
                tb.float_format[name] = '8.3'

            tb.field_names = ['DMU']\
                    + data.input_names\
                    + data.output_names\
                    + ['Ef']\
                    + data.dmu_names\
                    + slack_input_names\
                    + slack_output_names
                       
            for d,v in self.solution.items():
                row = [data.dmu_names[d]]\
                      + data.input_values[d]\
                      + data.output_values[d]\
                      + [v.efficiency]\
                      + v.llambda\
                      + v.slack_inputs\
                      + v.slack_outputs
                tb.add_row(row)
            print(tb)

class CCROOSENVModel():
    def __init__(self, data : DEAData):
        self.data = data
        self.create_model()
        self.is_ok = False
    def create_model(self):
        data = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))

        self.solution = {d : DotMap({'dmu_name': data.dmu_names[d],\
                'inverse_efficiency' : 0.0,\
                'llambda' : [0.0 for d in D],\
                'slack_inputs': [0.0 for i in I],\
                'slack_outputs' : [0.0 for o in O]}) for d in D }

        m = Model('CCROOSENV',sense=MAXIMIZE,solver_name=CBC)
        m.max_seconds = 30000

        theta = m.add_var(var_type='C',obj=1.0,name='theta') 
        ll = [m.add_var(lb=0.0,var_type='C',obj=0.0,name='ll(%d)' % (d)) for d in D]
        si = [m.add_var(lb=0.0,var_type='C',obj=0,name='si(%d)' % (i)) for i in I]
        so = [m.add_var(lb=0.0,var_type='C',obj=0,name='so(%d)' % (o)) for o in O]

        m.objective = theta 
        m.verbose = 0
        self.m,self.ll,self.theta,self.si,self.so = m,ll,theta,si,so
        #m.write('m.lp')
    
    def run(self):
        e = 1e-3
        data = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))
        m,ll,theta,si,so = self.m,self.ll,self.theta,self.si,self.so
        for r in D:
            m.objective = theta + e * (xsum( si[i] for i in I) + xsum( so[o] for o in O))
            cnstrs = []
            for i in I:
                cnstrs.append(m.add_constr( xsum( data.input_values[d][i] * ll[d] for d in D ) + si[i] == data.input_values[r][i],name='input_cnstr(%d)'%(i)))
            for o in O:
                cnstrs.append(m.add_constr( xsum( data.output_values[d][o] * ll[d] for d in D ) - data.output_values[r][o]*theta - so[o] == 0.0,name='output_cnstr(%d)'%(o)))
            status = m.optimize()
            #m.write('m%d.lp'%(r))
            if status == OptimizationStatus.OPTIMAL:
               # guardo a eficiencia obtida para dmu r
               sol = self.solution[r]
               sol.inverse_efficiency  = m.objective_value
               for d in D:
                   # guardo os valores dos lambdas 
                   sol.llambda[d] = ll[d].x
               for i in I:
                   sol.slack_inputs[i] = si[i].x
               for o in O:
                   sol.slack_outputs[o] = so[o].x
            else:
               print(f"Error solving CCRIOENV model for DMU %d " %(r))
               sys.exit()

            for cc in cnstrs:                  
                m.remove(cc)
        self.is_ok = True
    
    def print_solution(self):
        if self.is_ok == True:
            data = self.data
            I = range(len(data.input_names))
            O = range(len(data.output_names))
            D = range(len(data.dmu_names))
            tb = PT()
            # cabecalho da tabela
            for d in data.dmu_names: 
                tb.float_format[d] = '8.3'
            tb.float_format['InvEf'] = '8.3'
            tb.float_format['Ef'] = '8.3'
            slack_input_names = ['si(%d)' % (i) for i in I]
            slack_output_names = ['so(%d)' % (o) for o in O]
            for name in slack_input_names:
                tb.float_format[name] = '8.3'
            for name in slack_output_names:
                tb.float_format[name] = '8.3'
            tb.field_names = ['DMU']\
                    + data.input_names\
                    + data.output_names\
                    + ['InvEf']\
                    + ['Ef']\
                    + data.dmu_names\
                    + slack_input_names\
                    + slack_output_names
               
            for d,v in self.solution.items():
                row = [data.dmu_names[d]]\
                      + data.input_values[d]\
                      + data.output_values[d]\
                      + [v.inverse_efficiency]\
                      + [1/v.inverse_efficiency]\
                      + v.llambda\
                      + v.slack_inputs\
                      + v.slack_outputs
                tb.add_row(row)
            print(tb)

class DEAPY():
    def __init__(self, data : DEAData):
        self.data = data

    def ccriomw(self):
        print()
        print('Running CRS Input Oriented Weight Form')
        model = CCRIOMWModel(self.data)             
        model.run()
        model.print_solution()
    def ccroomw(self):
        print()
        print('Running CRS Output Oriented Weight Form')
        model = CCROOMWModel(self.data)             
        model.run()
        model.print_solution()
    def ccrioenv(self):
        print()
        print('Running CRS Input Oriented Envelope Form')
        model = CCRIOENVModel(self.data)             
        model.run()
        model.print_solution()
    def ccrooenv(self):
        print()
        print('Running CRS Output Oriented Envelope Form')
        model = CCROOENVModel(self.data)             
        model.run()
        model.print_solution()
    def ccriosenv(self):
        print()
        print('Running CRS Input Oriented Slack-based Envelope Form')
        model = CCRIOSENVModel(self.data)             
        model.run()
        model.print_solution()
    def ccroosenv(self):
        print()
        print('Running CRS Output Oriented Slack-based Envelope Form')
        model = CCROOSENVModel(self.data)             
        model.run()
        model.print_solution()
