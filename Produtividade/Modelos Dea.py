from mip import Model, xsum,  minimize, INTEGER,maximize,MAXIMIZE, MINIMIZE,CBC, OptimizationStatus, BINARY
from itertools import product
import sys
from pprint import pp
from prettytable import PrettyTable as PT
from dotmap import DotMap
EPS = 1e-6
import copy


class DEAData()
    def __init__(self,
                dmu_names       = None,
                dmu_names_print = None,
                input_names     = None,
                output_names    = None,
                input_values    = None,
                output_values   = None ): 
        self.dmu_names      = dmu_names
        self.dmu_names_print = dmu_names_print    
        self.input_names    = input_names  
        self.output_names   = output_names  
        self.input_values   = input_values 
        self.output_values  = output_values
    def print(self):
        I = range(len(self.input_names))
        O = range(len(self.output_names))
        D = range(len(self.dmu_names))
        tb = PT()
        if self.dmu_names_print is not None:
            tb.field_names = ['DMU'] +['codigo']+ self.input_names + self.output_names
            for d in D:
                row =   [self.dmu_names_print[d]] +[self.dmu_names[d]]\
                        +["{:.5}".format(self.input_values[d][i]) for i in I] \
                        +["{:.5}".format(self.output_values[d][o]) for o in O]
                tb.add_row(row)
        else:
            tb.field_names = ['DMU'] + self.input_names + self.output_names
            for d in D:
                row = [self.dmu_names[d]]\
                        +["{:.5}".format(self.input_values[d][i]) for i in I] \
                        +["{:.5}".format(self.output_values[d][o]) for o in O]
                tb.add_row(row)
        return tb
data_prov = DEAData(
        dmu_names      = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16'],
        dmu_names_print      = [  'Air Canada',
                            'ANA All Nippon Airways',
                            'American Airlines',
                            'British Airways',
                            'Delta Air Lines',
                            'Emirates',
                            'Garuda Indonesia',
                            'KLM',
                            'Lufthansa',
                            'Malaysia Airlines',
                            'Qantas',
                            'SAS Scandinavian Airlines',
                            'Singapore Airlines',
                            'TAM',
                            'Thai Airways',
                            'United Airlines'],
        input_names    = ['I1','I2'],
        output_names   = ['O1'],
        input_values   = [  [2293,7217121  ],
                            [2591,14651828 ],
                            [1112,26310000 ],
                            [4624,19279420 ],
                            [6628,23357000 ],
                            [3457,20837627 ],
                            [102  ,4736127 ],
                            [4850,6706203  ],
                            [1979,31867956 ],
                            [3762,3953020  ],
                            [6074,15118143 ],
                            [2047,2954620  ],
                            [438  ,22323127],
                            [2789,8314066  ],
                            [4620,33144669 ],
                            [4897,12195000 ]],
        output_values= [[13028613],
                        [ 14683532],
                        [ 34707729],
                        [ 21401581],
                        [ 27292425],
                        [ 27369447],
                        [ 2834184],
                        [ 15090771],
                        [ 27007957],
                        [ 7292543],
                        [ 17368244],
                        [ 4152670],
                        [ 21286125],
                        [ 7840248],
                        [ 10441041],
                        [ 29065589] ])
data_dist = DEAData(
        dmu_names_print    = ['Air Canada',
                            'ANA All Nippon Airways',
                            'American Airlines',
                            'British Airways',
                            'Delta Air Lines',
                            'Emirates',
                            'Garuda Indonesia',
                            'KLM',
                            'Lufthansa',
                            'Malaysia Airlines',
                            'Qantas',
                            'SAS Scandinavian Airlines',
                            'Singapore Airlines',
                            'TAM',
                            'Thai Airways',
                            'United Airlines'],
        dmu_names      = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16'],
        input_names    = ['I1','I2','I3'],
        output_names   = ['O1','O2'],
        input_values   = [
                [ 8352,   1302813,    3060770.35],    
                [ 6479,   1468332,    2556513.78],    
                [23102,   3470729,    8654892.94],   
                [16563,   2140181,    5304411.47],   
                [17408,   2729225,    7349946.47],   
                [13153,   2736947,    4717271.61],   
                [ 2187,    283484,     676346.53],      
                [ 8101,   1509071,    3027818.18],    
                [33288,   2700757,    5759785.56],   
                [ 5231,    729243,    1606904.02],     
                [12156,   1736844,    3156052.26],   
                [ 4046,    415270,    1108178.33],     
                [ 9467,   2128625,    3513668.99],    
                [ 6810,    784048,    2015096.39],     
                [ 7374,   1044141,    2417856.19],    
                [18460,   2906589,    7647835.29]],
        output_values = [
                [ 6420786   , 1157081],
                [ 4286268   , 2059289],
                [17866791   , 2417898],
                [10079586   , 4438214],
                [14571329   , 1671083],
                [11276662   , 6531110],
                [ 1514745   ,  282129],
                [ 7347192   , 4093466],
                [12398774   , 6928900],
                [ 2997171   , 2072022],
                [ 9945797   , 2623457],
                [ 2304528   ,  344994],
                [ 7733939   , 6559460],
                [ 3935997   ,  155797],
                [ 4725671   , 2157255],
                [14645900   , 2340509]])


def normatize_data(Data: DEAData):
    data = copy.deepcopy(Data)
    I = range(len(data.input_names))
    O = range(len(data.output_names))
    D = range(len(data.dmu_names))
    for i in I:
        avg_input = sum(data.input_values[d][i] for d in D) / len(D)
        for d in D:
            data.input_values[d][i] = data.input_values[d][i] / avg_input if avg_input else 0
    for o in O:
        avg_output = sum(data.output_values[d][o] for d in D) / len(D)
        for d in D:
            data.output_values[d][o] = data.output_values[d][o] / avg_output if avg_output else 0
    return data

class Classificador_Eficiencia:
    def __init__(self, data: DEAData = None, solution: DotMap = None):
        if solution is None:
            if data is None: assert "Sem data"
            model = Model_frabric_Envelope(normatize_data(data),slack=True)
            model.model()
            solution = model.get_solution()
        resultados = DotMap()
        for dmu, sol in solution.items():
            if round(sol.efficiency,3) == 1:
                if any(sol.slack_inputs) or any(sol.slack_outputs):
                    classificacao = 'Fracamente Eficiente'
                else:
                    classificacao = 'Fortemente Eficiente'
            else:
                classificacao = 'Ineficiente'
            resultados[dmu] = DotMap({
                'dmu_name': sol.dmu_name,
                'efficiency': sol.efficiency,
                'classificação': classificacao
            })
        self.result = resultados

    def print(self):
        tb = PT()
        tb.field_names = ['DMU', 'Eficiência', 'Classificação']
        for dmu, resultado in self.result.items():
            eficiencia_formatada = '%.2f%%' % (resultado.efficiency * 100)
            tb.add_row([resultado.dmu_name, eficiencia_formatada, resultado.classificação])
        return tb
class RetornoEscala:
    def __init__(self, Constante: DotMap, Variavel: DotMap, Negative: DotMap, Positive: DotMap):
        resultado = DotMap()
        for dmu, sol in Constante.items():
            resultado[dmu] = DotMap({
                'DMU'      : sol.dmu_name,
                'Escala'   : round(Constante[dmu]['efficiency']/Variavel[dmu]['efficiency'],3),
                'Constante': round(sol.efficiency, 3),
                'Variavel' : round(Variavel[dmu].efficiency, 3),
                'Negative' : round(Negative[dmu].efficiency, 3),
                'Positive' : round(Positive[dmu].efficiency, 3),})
            if   resultado[dmu]['Variavel'] == resultado[dmu]['Constante']: resultado[dmu]['Retorno'] = 'Constante'
            elif resultado[dmu]['Variavel'] == resultado[dmu]['Positive'] : resultado[dmu]['Retorno'] = 'Crescente'
            elif resultado[dmu]['Variavel'] == resultado[dmu]['Negative'] : resultado[dmu]['Retorno'] = 'Decrescente'
        self.result = resultado
    def print(self):
        tb = PT()
        tb.field_names = ['DMU', 'Constante', 'Variavel', 'Negative', 'Positive','Ef Escala', 'Retorno']
        for dmu, res in self.result.items():
            tb.add_row([res.DMU, f"{res.Constante * 100:.2f}%", f"{res.Variavel * 100:.2f}%", f"{res.Negative * 100:.2f}%", f"{res.Positive * 100:.2f}%", f"{res.Escala* 100:.2f}%",res.Retorno])
        return tb
    def get_escala(self):
        resultado = DotMap()
        for dmu, sol in self.result.items(): 
            resultado[dmu] = sol.Retorno
        return resultado
class ComparadorEscala:
    def __init__(self, escalas: list):
        self.escalas = escalas
    def print(self, nome: list):
        tb =  PT()
        dmus = list(self.escalas[0].keys())
        tb.field_names = ['DMU'] + nome
        for dmu in dmus:
            row = [dmu + 1]
            for escala in self.escalas:
                row.append(escala[dmu])
            tb.add_row(row)
        return tb
class Multiplicaadores:
    def __init__(self,data: DEAData,
        name:   str = "",
        mode:   str = "Input",#Input - Output
        scale:  str = "Constante",#No, Const, Positive ou Negative
        ):
        self.name  = name
        self.mode  = mode
        self.scale = scale
        self.data  = data
    def model(self):
        data =  self.data
        name =  self.name
        mode =  self.mode
        scale = self.scale
        sense = "MAX" if mode == "Input" else "MIN"
        
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))
        
        self.solution =  {dmu : DotMap({'dmu_name': data.dmu_names[dmu],\
                                        'efficiency' : 0.0,\
                                        'input_weight' : [0.0 for i in I],\
                                        'output_weight' : [0.0 for o in O] }) for dmu in D}
        
        model = Model(name, sense=sense, solver_name=CBC)
        model.verbose = 0
        
        u = [model.add_var(lb=EPS,var_type='C',obj=0,name='u(%d)' % (i)) for i in I]
        v = [model.add_var(lb=EPS,var_type='C',obj=0,name='v(%d)' % (o)) for o in O]
        w = tuple
        match scale:
            case "Constante":   w = 0
            case "Variavel":    w = model.add_var(lb= -1000,ub=+1000,var_type='C',obj=0,name='w')#por algum motivo se eu não setar um range ele sempre é posi
            case "Positive":    w = model.add_var(lb=0,var_type='C',obj=0,name='w')
            case "Negative":    w = model.add_var(lb = -1000,ub=0,var_type='C',obj=0,name='w')#Tem alguma coisa dando errado no modelo negativ
        _input  = lambda dmu: xsum(data.input_values[dmu][i] * u[i]  for i in I)
        _output = lambda dmu: xsum(data.output_values[dmu][o] * v[o] for o in O)
        match mode:#se for orientado a input ou output muda a objetiva 
            case "Input":
                objective = lambda dmu: _output(dmu) + w 
                restriction = _input
            case "Output":
                objective = lambda dmu: _input(dmu) - w  
                restriction =_output
        # restrição: 
        for dmu in D:
            model  += _output(dmu) - _input(dmu) + w <= 0, 'dmu(%d)'% (dmu)
        for dmu in D:
            model.objective = objective(dmu) 
            nc = model.add_constr(restriction(dmu) == 1, name='norm_constr')
            status = model.optimize()
            #model.write('m%d.lp'%(dmu))
            if status == OptimizationStatus.OPTIMAL:
                sol = self.solution[dmu]
                sol.efficiency  = model.objective_value
                for i in I:
                    # guardo os valores dos pesos de input
                    sol.input_weight[i] = u[i].x
                for o in O:
                    # guardo dos valores dos pesos de output
                    sol.output_weight[o] = v[o].x
            else:
                print(f"Error solving {name} model for DMU {dmu} ")
                sys.exit()
            model.remove(nc)
    def print_solution(self, only_ef: bool = False, no_data: bool = False):
        data = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))
        self.round_solution()
        tb = PT()
        # cabecalho da tabela
        input_weight_names = ['u(%d)' % (i) for i in I]
        output_weight_names = [ 'v(%d)' % (o) for o in O]
        
        if only_ef:
            tb.field_names = ['DMU']\
                            + ['Ef']
            for d,v in self.solution.items():
                row = [data.dmu_names[d]] + ["{:.3%}".format(v.efficiency if self.mode == "Input" else 1/v.efficiency)]
                tb.add_row(row)
            return tb
        elif no_data:
            tb.field_names =['Ef']\
                    + input_weight_names\
                    + output_weight_names
            for d,v in self.solution.items():
                row =   ["{:.3%}".format(v.efficiency if self.mode == "Input" else 1/v.efficiency)]\
                        + v.input_weight\
                        + v.output_weight
                tb.add_row(row)
            return tb
        else:
            tb.field_names = ['DMU']\
                    + ['Ef']\
                    + ['InvEf']\
                    + input_weight_names\
                    + output_weight_names
                    
            for d,v in self.solution.items():
                row = [data.dmu_names[d]]\
                        +  ["{:.3%}".format(v.efficiency if self.mode == "Input" else 1/v.efficiency)]\
                        +  ["{:.3%}".format(1/v.efficiency if self.mode == "Input" else v.efficiency)]\
                        + v.input_weight\
                        + v.output_weight
                tb.add_row(row)
            return tb
    def get_solution(self):#não precisa disso, da pra pegar direto sem um metodo
        #o ideal seria colocar a variavel is_ok para confirmar que rodou tudo de boa, mas não vou botar não
        return self.solution
    def round_solution(self):
        data = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))
        for d,v in self.solution.items():
            for i in I:
                v.input_weight[i] = round(v.input_weight[i],3)
            for o in O:
                v.output_weight[o] = round(v.output_weight[o],3)
class Envelope:
    def __init__(self,data: DEAData,
        name:   str = "",
        mode:   str = "Input",#Input - Output
        scale:  str = "Constante",#No, Const, Positive ou Negative
        slack:  bool = False, #True para adicionar as folgas
        var:    str = "C",#C constante, B binario
        ):
        self.data = data
        self.name = name
        self.mode = mode
        self.scale = scale
        self.slack = slack
        self.var = var
    def model(self):
        data  = self.data
        name  = self.name
        mode  = self.mode
        scale = self.scale
        slack = self.slack
        var= self.var
        sense = "MAX" if mode == "Output" else "MIN"
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))
        
        self.solution = {d : DotMap({'dmu_name': data.dmu_names[d],\
                                    'efficiency' : 0.0,\
                                    'llambda' : [0.0 for d in D],\
                                    'slack_inputs': [0.0 for i in I],\
                                    'slack_outputs' : [0.0 for o in O]}) for d in D }
        
        model = Model(name, sense=sense, solver_name=CBC)
        model.verbose = 0
        theta = model.add_var(var_type='C',obj=1.0,name='theta')
        match mode:
            case "Input":
                t, n = (theta, 1)
                e = -1e-3
            case "Output":
                t, n = (1, theta)
                e = 1e-3
            
        ll = [model.add_var(lb=0.0,var_type=var,obj=0,  name='ll(%d)' % (d)) for d in D]
        _input  = lambda d, i: data.input_values[d][i] * ll[d] 
        _output = lambda d,o: data.output_values[d][o] * ll[d]
        match scale:
            case "Constante":
                pass
            case "Variavel":
                model += xsum(ll[dmu] for dmu in D) == 1
            case "Positive":
                model += xsum(ll[dmu] for dmu in D) >= 1
            case "Negative":
                model += xsum(ll[dmu] for dmu in D) <= 1
        if slack: 
            si = [model.add_var(lb=0.0,var_type='C',obj=0,  name='si(%d)' % (i)) for i in I]
            so = [model.add_var(lb=0.0,var_type='C',obj=0,  name='so(%d)' % (o)) for o in O]
            model.objective = theta + e * (xsum( si[i] for i in I) + xsum( so[o] for o in O))
            for r in D:
                cnstrs = []
                for i in I:
                    cnstrs.append(model.add_constr(xsum(_input(d,i)  for d in D) + si[i] == data.input_values[r][i] * t,name='input_cnstr(%d)'%(i)))
                for o in O:
                    cnstrs.append(model.add_constr(xsum(_output(d,o) for d in D) - so[o] == data.output_values[r][o] *n, name='output_cnstr(%d)'%(o)))
                status = model.optimize()
                if status == OptimizationStatus.OPTIMAL:
                    sol = self.solution[r]
                    sol.efficiency = model.objective_value
                    for d in D:
                        sol.llambda[d] = ll[d].x
                    for i in I:
                        sol.slack_inputs[i] = si[i].x
                    for o in O:
                        sol.slack_outputs[o] = so[o].x
                else:
                    print(f"Error solving {name} model for DMU {r}")
                    sys.exit()
                for cc in cnstrs:
                    model.remove(cc)
        else:
            model.objective = theta
            for r in D:
                cnstrs = []
                for i in I:
                    cnstrs.append(model.add_constr(xsum(_input(d,i)  for d in D) <= data.input_values[r][i] * t,name='input_cnstr(%d)'%(i)))
                for o in O:
                    cnstrs.append(model.add_constr(xsum(_output(d,o) for d in D) >= data.output_values[r][o] *n, name='output_cnstr(%d)'%(o)))
                status = model.optimize()
                if status == OptimizationStatus.OPTIMAL:
                    sol = self.solution[r]
                    sol.efficiency = model.objective_value
                    for d in D:
                        sol.llambda[d] = ll[d].x
                else:
                    print(f"Error solving {name} model for DMU {r}")
                    sys.exit()
                for cc in cnstrs:                  
                    model.remove(cc)
    def print_solution(self,print_ll: bool=True, no_data: bool=False):
        #isso ta pirando toda vez que eu volto aqui
        #Eu fiz muita coisa errada e ruim aqui, se algum dia eu tiver tempo eu vou refazer isso aqui com  menos if else
        data = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))
        if self.var == 'C': self.round_solution()
        tb = PT()
        
        if no_data:
            if self.slack:
                slack_input_names = ['si(%d)' % i for i in I]
                slack_output_names = ['so(%d)' % o for o in O]
                tb.field_names =  data.dmu_names + slack_input_names + slack_output_names
                for d, v in self.solution.items():
                    row = v.llambda + v.slack_inputs + v.slack_outputs
                    tb.add_row(row)
                return tb
            else: 
                tb.field_names =  data.dmu_names
                for d, v in self.solution.items():
                    row = v.llambda
                    tb.add_row(row)
                return tb
        elif print_ll:
            if self.slack:
                slack_input_names = ['si(%d)' % i for i in I]
                slack_output_names = ['so(%d)' % o for o in O]
                tb.field_names = ['DMU'] + data.input_names + data.output_names + ['Ef']+ ['InvEf'] + data.dmu_names + slack_input_names + slack_output_names
                for d, v in self.solution.items():
                    row =[data.dmu_names[d]]+ data.input_values[d] + data.output_values[d] + ["{:.3%}".format(v.efficiency if self.mode == "Input" else 1/v.efficiency)] + ["{:.3%}".format(1/v.efficiency if self.mode == "Input" else v.efficiency)] + v.llambda + v.slack_inputs + v.slack_outputs
                    tb.add_row(row)
                return tb
            else: 
                tb.field_names = ['DMU'] + data.input_names + data.output_names + ['Ef']+ ['InvEf']  + data.dmu_names
                for d, v in self.solution.items():
                    row = [data.dmu_names[d]]+ data.input_values[d] + data.output_values[d] + ["{:.3%}".format(v.efficiency if self.mode == "Input" else 1/v.efficiency)] + ["{:.3%}".format(1/v.efficiency if self.mode == "Input" else v.efficiency)] + v.llambda
                    tb.add_row(row)
                return tb
        else:
            if self.slack:
                slack_input_names = ['si(%d)' % i for i in I]
                slack_output_names = ['so(%d)' % o for o in O]
                tb.field_names = ['DMU'] +  + data.output_names + ['Ef']+ ['InvEf'] + data.dmu_names + slack_input_names + slack_output_names
                for d, v in self.solution.items():
                    row =[data.dmu_names[d]]+ data.input_values[d] + data.output_values[d] + ["{:.3%}".format(v.efficiency if self.mode == "Input" else 1/v.efficiency)] + ["{:.3%}".format(1/v.efficiency if self.mode == "Input" else v.efficiency)] + v.llambda + v.slack_inputs + v.slack_outputs
                    tb.add_row(row)
                return tb
            else: 
                tb.field_names = ['DMU'] + data.input_names + data.output_names + ['Ef']+ ['InvEf']  + data.dmu_names
                for d, v in self.solution.items():
                    row = [data.dmu_names[d]]+ data.input_values[d] + data.output_values[d] + ["{:.3%}".format(v.efficiency if self.mode == "Input" else 1/v.efficiency)] + ["{:.3%}".format(1/v.efficiency if self.mode == "Input" else v.efficiency)] + v.llambda
                    tb.add_row(row)
                return tb
    def get_solution(self):#não precisa disso, da pra pegar direto sem um metodo
        #o ideal seria colocar a variavel is_ok para confirmar que rodou tudo de boa, mas não vou botar não
        return self.solution
    def goal(self,lamda: bool=True):
        data = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))
        self.goals =   {d: {'dmu_name': data.dmu_names[d],
                            'meta_outputs':[0.0 for o in O],
                            'meta_inputs': [0.0 for i in I]} for d in D}
        if lamda:
            for dmu in D:
                ll = self.solution[dmu]['llambda']
                for i in I:
                    self.goals[dmu]['meta_inputs'][i]  = sum( data.input_values[d][i] * ll[d] for d in D)
                for o in O:
                    self.goals[dmu]['meta_outputs'][o] = sum(data.output_values[d][o] * ll[d]for d in D) 
                #print(f"DMU: {dmu} - Meta-Inputs: {self.goals[dmu]['meta_inputs']}, Meta-Outputs: {self.goals[dmu]['meta_outputs']}")
        else:
            if self.mode == "Input":
                for d in self.solution:
                    dmu = self.solution[d]
                    theta = dmu.efficiency #no input é a eficiencia
                    self.goals[d]['meta_inputs']  = [theta * x - s for x, s in zip(data.input_values[d], dmu.slack_inputs)]
                    self.goals[d]['meta_outputs'] = [y + s         for y, s in zip(data.output_values[d], dmu.slack_outputs)]
                    #print(f"DMU: {d} - Meta-Inputs: {self.goals[d]['meta_inputs']}, Meta-Outputs: {self.goals[d]['meta_outputs']}")
            elif self.mode == "Output":
                for d in self.solution:
                    dmu = self.solution[d]
                    theta = dmu.efficiency #no output é 1/eficiencia 
                    self.goals[d]['meta_outputs'] = [theta * y + s for y, s in zip(data.output_values[d], dmu.slack_outputs)]
                    self.goals[d]['meta_inputs']  = [x - s         for x, s in zip(data.input_values[d], dmu.slack_inputs)]
                    #print(f"DMU: {d} - Meta-Inputs: {self.goals[d]['meta_inputs']}, Meta-Outputs: {self.goals[d]['meta_outputs']}")
            else:
                raise ValueError("Modo desconhecido. 'self.mode' deve ser 'Input' ou 'Output'.")
    def print_goal(self):
        self.goal()
        data = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))
        tb = PT()
        goal_input = ['Meta-Inputs(%d)' % (i) for i in I]
        goal_output = ['Meta-Outputs(%d)' % (o) for o in O]
        tb.field_names = ['DMU'] + goal_input + goal_output
        for d in D:
            dmu_name = data.dmu_names[d]
            meta_inputs  = self.goals[d]['meta_inputs']
            meta_outputs = self.goals[d]['meta_outputs']
            percent_change_input = [((meta - value) / value) * 100 for (meta, value) in zip(meta_inputs, data.input_values[d])]
            percent_change_output = [((meta - value) / value) * 100 for (meta, value) in zip(meta_outputs, data.output_values[d])]
            row = [dmu_name] + ['%.2f%%' % p for p in percent_change_input] + ['%.2f%%' % p for p in percent_change_output]
            tb.add_row(row)
        return tb
    def round_solution(self):
        for dmu in self.solution:
            self.solution[dmu]['llambda'] = [round(l, 3) for l in self.solution[dmu]['llambda']]
            self.solution[dmu]['slack_inputs'] = [round(s, 3) for s in self.solution[dmu]['slack_inputs']]
            self.solution[dmu]['slack_outputs'] = [round(s, 3) for s in self.solution[dmu]['slack_outputs']]
    def get_goal(self):
        self.goal()
        data = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))
        goals_ = self.goals
        for d in D:
            goals_[d]['meta_inputs']  = [((meta - value) / value) for (meta, value) in zip(goals_[d]['meta_inputs'] , data.input_values[d])]
            goals_[d]['meta_outputs'] = [((meta - value) / value) for (meta, value) in zip(goals_[d]['meta_outputs'], data.output_values[d])]
        return goals_

    def print(self):
        tb = PT()
        tb.field_names = ['DMU', 'Eficiência', 'Classificação']
        for dmu, resultado in self.result.items():
            eficiencia_formatada = '%.2f%%' % (resultado.efficiency * 100)
            tb.add_row([resultado.dmu_name, eficiencia_formatada, resultado.classificação])
        return tb
class Model_add:
    def __init__(self,
                data: DEAData,
                name: str = "",
                mode: str = "Weigth", #Envelope
                scale: str = "Constante"):
        self.name = name
        self.data = data
        self.mode = mode
        self.scale = scale
    def model(self):
        name = self.name
        data  = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))
        if self.mode == "Weigth":
            self.solution =  {dmu : DotMap({'dmu_name': data.dmu_names[dmu],\
                                        'efficiency' : 0.0,\
                                        'input_weight' : [0.0 for i in I],\
                                        'output_weight' : [0.0 for o in O] }) for dmu in D}
            model = Model(self.name, sense="MIN", solver_name=CBC)
            model.verbose = 0
            u = [model.add_var(lb=EPS,var_type='C',obj=0,name='u(%d)' % (i)) for i in I]
            v = [model.add_var(lb=EPS,var_type='C',obj=0,name='v(%d)' % (o)) for o in O]
            w = 0
            match self.scale:
                case "Constante": w = 0
                case "Variavel":  w = model.add_var(lb= -1,ub=+1,var_type='C',obj=0,name='w')#por algum motivo se eu não setar um range ele sempre é posi
                case "Positive":  w = model.add_var(lb=0        ,var_type='C',obj=0,name='w')
                case "Negative":  w = model.add_var(lb = -1,ub=0,var_type='C',obj=0,name='w') #Tem alguma coisa dando errado no modelo negativo
            for dmu in D:
                model  += xsum(data.input_values[dmu][i] * u[i]  for i in I) - xsum(data.output_values[dmu][o] * v[o] for o in O) + w >= 0, 'dmu(%d)'% (dmu)
            for dmu in D:
                model.objective = xsum(data.input_values[dmu][i] * u[i]  for i in I) - xsum(data.output_values[dmu][o] * v[o] for o in O) + w
                status = model.optimize()
                #model.write('m%d.lp'%(dmu))
                if status == OptimizationStatus.OPTIMAL:
                    sol = self.solution[dmu]
                    sol.efficiency  = model.objective_value
                    for i in I:
                        sol.input_weight[i] = u[i].x
                    for o in O:
                        sol.output_weight[o] = v[o].x
                else:
                    print(f"Error solving {name} model for DMU {dmu} ")
                    sys.exit()
        elif self.mode == "Envelope":
            self.solution = {d : DotMap({'dmu_name': data.dmu_names[d],\
                                    'efficiency' : 0.0,\
                                    'llambda' : [0.0 for d in D],\
                                    'slack_inputs': [0.0 for i in I],\
                                    'slack_outputs' : [0.0 for o in O]}) for d in D }
            model = Model(self.name, sense="MAX", solver_name=CBC)
            model.verbose = 0
            
            si = [model.add_var(lb=0.0,var_type='C',obj=0,  name='si(%d)' % (i)) for i in I]
            so = [model.add_var(lb=0.0,var_type='C',obj=0,  name='so(%d)' % (o)) for o in O]
            ll = [model.add_var(lb=0.0,var_type='C',obj=0,  name='ll(%d)' % (d)) for d in D]
            match self.scale:
                case "Constante":   pass
                case "Variavel":    model += xsum(ll[dmu] for dmu in D) == 1
                case "Positive":    model += xsum(ll[dmu] for dmu in D) >= 1
                case "Negative":    model += xsum(ll[dmu] for dmu in D) <= 1
            model.objective = xsum(si[i] for i in I) + xsum(so[o] for o in O)
            for r in D:
                cnstrs = []
                for i in I:
                    cnstrs.append(model.add_constr(xsum(data.input_values[d][i] * ll[d] for d in D) + si[i] == data.input_values[r][i] ,name='input_cnstr(%d)'%(i)))
                for o in O:
                    cnstrs.append(model.add_constr(xsum(data.output_values[d][o] * ll[d] for d in D) - so[o] == data.output_values[r][o], name='output_cnstr(%d)'%(o)))
                status = model.optimize()
                if status == OptimizationStatus.OPTIMAL:
                    sol = self.solution[r]
                    sol.efficiency = model.objective_value
                    for d in D: sol.llambda[d] = ll[d].x
                    for i in I: sol.slack_inputs[i] = si[i].x
                    for o in O: sol.slack_outputs[o] = so[o].x
                else:
                    print(f"Error solving {name} model for DMU {r}")
                    sys.exit()
                for cc in cnstrs:                  
                    model.remove(cc)
        else:
            print("Mode deve ser Weigth ou Envelope")
            sys.exit()
    def print_solution(self, print_slack: bool = False):
        data = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))
        tb = PT()
        if self.mode == "Envelope":
            if print_slack:
                slack_input_names = ['si(%d)' % i for i in I]
                slack_output_names = ['so(%d)' % o for o in O]
                tb.field_names = ['DMU'] + ['Obj'] + slack_input_names + slack_output_names
                for d, v in self.solution.items():
                    tb.add_row([data.dmu_names[d]] +  [f"{round(v.efficiency,5) :.2}"] +[f"{round(w,7):.2}"for w in v.slack_inputs] + [f"{round(w,7):.2}"for w in v.slack_outputs])
                return tb
            else:
                tb.field_names = ['DMU'] + data.dmu_names 
                for d, v in self.solution.items():
                    tb.add_row([data.dmu_names[d]] +[f"{round(w,7):.2}"for w in v.llambda])
                return tb

        elif self.mode == "Weigth":
            input_weight_names = ['u(%d)' % (i) for i in I]
            output_weight_names = [ 'v(%d)' % (o) for o in O]
            tb.field_names = ['DMU']+ ['Obj'] + input_weight_names+ output_weight_names
            for d,v in self.solution.items():
                tb.add_row([data.dmu_names[d]] + [f"{round(v.efficiency,5) :.2}"] + [f"{w:.3}" for w in v.input_weight] + [f"{w:.3}"for w in v.output_weight])
            return tb
    def print_fator_escala(self):
        data = self.data
        tb = PT()
        tb.field_names = ['DMU', 'Constante', 'Variável', 'Negativo', 'Positivo']
        escalas = ["Constante", "Variavel", "Positive", "Negative"]
        solucoes = {}
        for escala in escalas:
            modelo = Model_add(data=data, mode=self.mode, scale=escala)
            modelo.model()
            solucoes[escala] = modelo.get_solution()
        resultado = DotMap()
        for dmu, sol in solucoes['Constante'].items():
            resultado[dmu] = DotMap({
                'DMU': sol.dmu_name,
                'Constante': solucoes['Constante'][dmu].efficiency,
                'Variavel' : solucoes['Variavel'][dmu].efficiency ,
                'Positive' : solucoes['Positive'][dmu].efficiency ,
                'Negative' : solucoes['Negative'][dmu].efficiency 
            })
        for d, v in resultado.items():
            tb.add_row([
                v.DMU,
                f"{v.Constante :.2}" ,
                f"{v.Variavel  :.2}" ,
                f"{v.Positive  :.2}" ,
                f"{v.Negative  :.2}" 
            ])
        self.resultado = resultado
        return tb
    def get_solution(self):
        return self.solution
    def get_resultado(self):
        return self.resultado
    def goal(self):
        data = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))
        self.goals =   {d: {'dmu_name': data.dmu_names[d],
                            'meta_outputs':[0.0 for o in O],
                            'meta_inputs': [0.0 for i in I]} for d in D}
        for dmu in D:
            ll = self.solution[dmu]['llambda']
            for i in I:
                self.goals[dmu]['meta_inputs'][i]  = sum( data.input_values[d][i] * ll[d] for d in D)
            for o in O:
                self.goals[dmu]['meta_outputs'][o] = sum(data.output_values[d][o] * ll[d]for d in D) 
    def print_goal(self):
        self.goal()
        data = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))
        tb = PT()
        goal_input = ['Meta-Inputs(%d)' % (i) for i in I]
        goal_output = ['Meta-Outputs(%d)' % (o) for o in O]
        tb.field_names = ['DMU'] + goal_input + goal_output
        for d in D:
            dmu_name = data.dmu_names[d]
            meta_inputs  = self.goals[d]['meta_inputs']
            meta_outputs = self.goals[d]['meta_outputs']
            percent_change_input = [((meta - value) / value) * 100 for (meta, value) in zip(meta_inputs, data.input_values[d])]
            percent_change_output = [((meta-value) / value) * 100 for (meta, value) in zip(meta_outputs, data.output_values[d])]
            row = [dmu_name] + ['%.2f%%' % p for p in percent_change_input] + ['%.2f%%' % p for p in percent_change_output]
            tb.add_row(row)
        return tb

    def get_goal(self):
        self.goal()
        data = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))
        goals_ = self.goals
        for d in D:
            goals_[d]['meta_inputs']  = [((meta - value) / value) for (meta, value) in zip(goals_[d]['meta_inputs'] , data.input_values[d])]
            goals_[d]['meta_outputs'] = [((meta - value) / value) for (meta, value) in zip(goals_[d]['meta_outputs'], data.output_values[d])]
        return goals_
class Model_SBM:#Não fiz por multiplicadores
    def __init__(self,
                    data: DEAData,
                    mode:  str = "No",#Input, #Output
                    scale: str = "Constante",
                    name:  str = ""):
        self.data  = data
        self.mode  = mode
        self.scale = scale
        self.name  = name
    def model(self):
        data = self.data
        I = range(len(data.input_names))  # Índices dos inputs
        O = range(len(data.output_names)) # Índices dos outputs
        D = range(len(data.dmu_names))    # Índices das DMUs
        self.solution = {d : DotMap({'dmu_name': data.dmu_names[d],\
                                    'efficiency' : 0.0,\
                                    'llambda' : [0.0 for d in D],\
                                    'slack_inputs': [0.0 for i in I],\
                                    'slack_outputs' : [0.0 for o in O],\
                                    't':0.0}) for d in D }
        if   self.mode == "No":
            model = Model(sense='MIN', solver_name='CBC')
            t  = model.add_var(name='t', lb=EPS)
            si = [model.add_var(name='si(%d)' % (i), lb=0.0) for i in I]
            so = [model.add_var(name='so(%d)' % (o), lb=0.0) for o in O]
            ll = [model.add_var(name='ll(%d)' % (d), lb=0.0) for d in D]
            match self.scale:
                case "Constante": pass
                case "Variavel" :model += (xsum(ll[d] for d in D)) == t
                case "Positive" :model += (xsum(ll[d] for d in D)) >= t
                case "Negative" :model += (xsum(ll[d] for d in D)) <= t
            for r in D:
                model.objective = t - (1/len(I)) * xsum(si[i]/data.input_values[r][i] for i in I)
                model += t + (1/len(O)) * xsum(so[o]/data.output_values[r][o] for o in O) == 1
                cnstrs = []
                for i in I:
                    cnstrs.append(model.add_constr(xsum(data.input_values[d][i] * ll[d] for d in D) + si[i] == data.input_values[r][i] * t ,name='input_cnstr(%d)'%(i)))
                for o in O:
                    cnstrs.append(model.add_constr(xsum(data.output_values[d][o] * ll[d] for d in D) - so[o] == data.output_values[r][o] * t, name='output_cnstr(%d)'%(o)))
                status = model.optimize()
                if status == OptimizationStatus.OPTIMAL:
                    sol = self.solution[r]
                    sol.efficiency = model.objective_value
                    for d in D: sol.llambda[d]       = ll[d].x
                    sol.t                = t.x
                    for i in I: sol.slack_inputs[i]  = si[i].x
                    for o in O: sol.slack_outputs[o] = so[o].x
                else:
                    print(f"Error solving {self.name} model for DMU {r}")
                    sys.exit()
                for cc in cnstrs:                  
                    model.remove(cc)
        elif self.mode == "Input" or self.mode ==  "Output":
            if self.mode == "Input": sense = 'MIN'
            else: sense = 'MAX'
            model = Model(sense=sense, solver_name='CBC')
            t  = model.add_var(name='t', lb=EPS)
            si = [model.add_var(name='si(%d)' % (i), lb=0.0) for i in I]
            so = [model.add_var(name='so(%d)' % (o), lb=0.0) for o in O]
            ll = [model.add_var(name='ll(%d)' % (d), lb=0.0) for d in D]
            for r in D:
                if self.mode == "Input":
                    model.objective = 1 - (1/len(I)) * xsum(si[i]/data.input_values[r][i] for i in I)
                else: model.objective = 1 + (1/len(O)) * xsum(so[o]/data.output_values[r][o] for o in O)
                cnstrs = []
                for i in I:
                    cnstrs.append(model.add_constr(xsum(data.input_values[d][i] * ll[d] for d in D) + si[i] == data.input_values[r][i] ,name='input_cnstr(%d)'%(i)))
                for o in O:
                    cnstrs.append(model.add_constr(xsum(data.output_values[d][o] * ll[d] for d in D) - so[o] == data.output_values[r][o], name='output_cnstr(%d)'%(o)))
                status = model.optimize()
                if status == OptimizationStatus.OPTIMAL:
                    sol = self.solution[r]
                    sol.efficiency = model.objective_value
                    for d in D: sol.llambda[d]       = ll[d].x
                    for i in I: sol.slack_inputs[i]  = si[i].x
                    for o in O: sol.slack_outputs[o] = so[o].x
                else:
                    print(f"Error solving {self.name} model for DMU {r}")
                    sys.exit()
                for cc in cnstrs:                  
                    model.remove(cc)
        #elif self.mode == "Multiplicadores":
    def print_solution(self,print_slack: bool = True):
        data = self.data
        I = range(len(data.input_names)) 
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))  
        tb = PT()
        if print_slack:
            slack_input_names = ['si(%d)' % i for i in I]
            slack_output_names = ['so(%d)' % o for o in O]
            tb.field_names = ['DMU'] + ['Obj']+['t'] + slack_input_names + slack_output_names
            for d, v in self.solution.items():
                tb.add_row([data.dmu_names[d]] + [f"{(v.efficiency):.2%}" if self.mode != "Output" else f"{1/v.efficiency:.2%}"] + [v.t] + [f"{round(w,7):.2}"for w in v.slack_inputs] + [f"{round(w,7):.2}"for w in v.slack_outputs])
            return tb
        else:
            tb.field_names = ['DMU'] + data.dmu_names 
            for d, v in self.solution.items():
                tb.add_row([data.dmu_names[d]] +[f"{round(w,7):.2}"for w in v.llambda])
            return tb
    def goal(self):
        data = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))
        self.goals =   {d: {'dmu_name': data.dmu_names[d],
                            'meta_outputs':[0.0 for o in O],
                            'meta_inputs': [0.0 for i in I]} for d in D}
        for dmu in D:
            t  = self.solution[dmu]['t']
            ll = self.solution[dmu]['llambda']
            for i in I:
                self.goals[dmu]['meta_inputs'][i]  = sum( data.input_values[d][i] * ll[d]/t for d in D)
            for o in O:
                self.goals[dmu]['meta_outputs'][o] = sum(data.output_values[d][o] * ll[d]/t for d in D) 
    def print_goal(self):
        self.goal()
        data = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))
        tb = PT()
        goal_input = ['Meta-Inputs(%d)' % (i) for i in I]
        goal_output = ['Meta-Outputs(%d)' % (o) for o in O]
        tb.field_names = ['DMU'] + goal_input + goal_output
        for d in D:
            dmu_name = data.dmu_names[d]
            meta_inputs  = self.goals[d]['meta_inputs']
            meta_outputs = self.goals[d]['meta_outputs']
            percent_change_input = [((meta - value) / value) * 100 for (meta, value) in zip(meta_inputs, data.input_values[d])]
            percent_change_output =[((meta - value) / value) * 100 for (meta, value) in zip(meta_outputs, data.output_values[d])]
            row = [dmu_name] + ['%.2f%%' % p for p in percent_change_input] + ['%.2f%%' % p for p in percent_change_output]
            tb.add_row(row)
        return tb
    def get_solution(self):
        self.model()
        return self.solution
    def get_goal(self):
        self.goal()
        data = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))
        goals_ = self.goals
        for d in D:
            goals_[d]['meta_inputs']  = [((meta - value) / value) for (meta, value) in zip(goals_[d]['meta_inputs'] , data.input_values[d])]
            goals_[d]['meta_outputs'] = [((meta - value) / value) for (meta, value) in zip(goals_[d]['meta_outputs'], data.output_values[d])]
        return goals_
class Model_ERM:
    def __init__(self,data: DEAData, 
                scale:str = 'Constante'):
        self.data = data
        self.scale = scale
    def model(self):
        data  = self.data
        scale = self.scale
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))
        
        self.solution = {d : DotMap({'dmu_name': data.dmu_names[d],\
                                    'efficiency'          :0.0,\
                                    'inp_efficiency'  : [0.0 for i in I],\
                                    'out_efficiency':[0.0 for o in O],\
                                    'llambda'     : [0.0 for d in D],\
                                    't'           : 0.0}) for d in D }
        
        model = Model("ERM Fracionado", sense="MIN", solver_name=CBC)
        model.verbose = 0
        theta   = [model.add_var(var_type='C',obj=1.0,name='theta(%d)' %(i)) for i in I]
        n       = [model.add_var(var_type='C',obj=1.0,name='n(%d)' %(o)) for o in O]
        ll      = [model.add_var(lb=0.0,var_type='C',obj=0,  name='ll(%d)' % (d)) for d in D]
        match scale:
            case "Constante":
                pass
            case "Variavel":
                model += xsum(ll[dmu] for dmu in D) == 1
            case "Positive":
                model += xsum(ll[dmu] for dmu in D) >= 1
            case "Negative":
                model += xsum(ll[dmu] for dmu in D) <= 1

        model.objective = xsum(theta[i] for i in I)/len(I)
        model += xsum(n[o] for o in O)/len(O) == 1
        
        t = model.add_var(lb=0.0, ub=1.0, var_type='C', name='t')
        for i in I:
            model.add_constr(theta[i]  <= t, name='theta_constraint_%s' % i)
        for j in O:
            model.add_constr(n[j]  >= t, name='eta_constraint_%s' % j)

        for r in D:
            cnstrs = []
            for i in I:
                cnstrs.append(model.add_constr(xsum(data.input_values[dmu][i]*ll[dmu] for dmu in D) <= theta[i]*data.input_values[r][i],name='input_cnstr(%d)'%(i)))
            for o in O:
                cnstrs.append(model.add_constr(xsum(data.output_values[dmu][o]*ll[dmu] for dmu in D) >= n[o]*data.output_values[r][o] , name='output_cnstr(%d)'%(o)))
            status = model.optimize()
            if status == OptimizationStatus.OPTIMAL:
                sol = self.solution[r]
                sol.efficiency = model.objective_value
                sol.t = t.x
                for i in I:
                    sol.inp_efficiency[i] = theta[i].x
                for o in O:
                    sol.out_efficiency[o] = n[o].x
                for d in D:
                    sol.llambda[d] = ll[d].x
            else:
                print(f"Error solving ERM model for DMU {r}")
                sys.exit()
            for cc in cnstrs:
                model.remove(cc)
    def print_solution(self, print_ll: bool = True):
        data = self.data
        I = range(len(data.input_names))  
        O = range(len(data.output_names)) 
        D = range(len(data.dmu_names))    
        tb = PT()
        if print_ll:
            tb.field_names = ['DMU'] + ['EF'] + ['inp_ef(%d)' % (i) for i in I]+ ['1/out_ef(%d)' % (o) for o in O] + ['t']
            for d, v in self.solution.items():
                tb.add_row([data.dmu_names[d]] + [f"{(v.efficiency):.2%}"] + [f"{v.inp_efficiency[i]:.2%}" for i in I] + [f"{1/v.out_efficiency[o]:.2%}" for o in O]+[v.t] )
            return tb
        else:
            tb.field_names = ['DMU'] + data.dmu_names
            for d, v in self.solution.items():
                tb.add_row([data.dmu_names[d]] + [f"{round(w,7):.2}"for w in v.llambda])
            return tb
    def goal(self):
        data = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))
        self.goals =   {d: {'dmu_name': data.dmu_names[d],
                            'meta_outputs':[0.0 for o in O],
                            'meta_inputs': [0.0 for i in I]} for d in D}
        for dmu in D:
            ll = self.solution[dmu]['llambda']
            t = self.solution[dmu]['t']
            for i in I:
                self.goals[dmu]['meta_inputs'][i]  = sum( data.input_values[d][i] * ll[d] for d in D)/t
            for o in O:
                self.goals[dmu]['meta_outputs'][o] = sum(data.output_values[d][o] * ll[d]for d in D)/t
    def print_goal(self):
        self.goal()
        data = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))
        tb = PT()
        goal_input = ['Meta-Inputs(%d)' % (i) for i in I]
        goal_output = ['Meta-Outputs(%d)' % (o) for o in O]
        tb.field_names = ['DMU'] + goal_input + goal_output
        for d in D:
            dmu_name = data.dmu_names[d]
            meta_inputs  = self.goals[d]['meta_inputs']
            meta_outputs = self.goals[d]['meta_outputs']
            percent_change_input = [((meta - value) / value) * 100 for (meta, value) in zip(meta_inputs, data.input_values[d])]
            percent_change_output = [((meta- value) / value) * 100 for (meta, value) in zip(meta_outputs, data.output_values[d])]
            row = [dmu_name] + ['%.2f%%' % p for p in percent_change_input] + ['%.2f%%' % p for p in percent_change_output]
            tb.add_row(row)
        return tb
    def get_goal(self):
        self.goal()
        data = self.data
        I = range(len(data.input_names))
        O = range(len(data.output_names))
        D = range(len(data.dmu_names))
        goals_ = self.goals
        for d in D:
            goals_[d]['meta_inputs']  = [((meta - value) / value) for (meta, value) in zip(goals_[d]['meta_inputs'] , data.input_values[d])]
            goals_[d]['meta_outputs'] = [((meta - value) / value) for (meta, value) in zip(goals_[d]['meta_outputs'], data.output_values[d])]
        return goals_
    def get_solution(self):
        return self.solution
