from deapy import DEAData, DEAPY, CCROOENVModel, CCRIOENVModel #pegar eficiencias provisão
import matplotlib.pyplot as plt #gerar histogramas 


def main():
    provisao = DEAData() #Lista de inputs e outputs para o modelo de provisão
    # nome das DMUs
    provisao.dmu_names = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16']
    # nome dos inputs (X)
    provisao.input_names = ['I1','I2']
    # nome dos outputs (Y)
    provisao.output_names = ['O1']
    # input values (X)
    provisao.input_values = [
        [2293 , 72171.21 ],
        [2591 , 146518.28],
        [11123, 263100.00],
        [4624 , 192794.20],
        [6628 , 233570.00],
        [3457 , 208376.27],
        [102  , 47361.27 ],
        [4850 , 67062.03 ],
        [19796, 318679.56],
        [3762 , 39530.20 ],
        [6074 , 151181.43],
        [2047 , 29546.20 ],
        [438  , 223231.27],
        [2789 , 83140.66 ],
        [4620 , 331446.69],
        [4897 , 121950.00]]   
    # Output values (Y)
    provisao.output_values = [
            [130286.13 ],
            [146835.32 ],
            [347077.29 ],
            [214015.81 ],
            [272924.25 ],
            [273694.47 ],
            [28341.84  ],
            [150907.71 ],
            [270079.57 ],
            [72925.43  ],
            [173682.44 ],
            [41526.70  ],
            [212861.25 ],
            [78402.48  ],
            [104410.41 ],
            [290655.89 ]]
    
    distribuicao = DEAData()
    #nome das DMUs
    distribuicao.dmu_names = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16']
    # nome dos inputs (X)
    distribuicao.input_names = ['I1','I2','I3']
    # nome dos outputs (Y)
    distribuicao.output_names = ['O1','O2']
    # nome dos outputs (Y)
    distribuicao.input_values = [
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
                [18460,   2906589,    7647835.29]]
    #input values. (/8654892.94
    distribuicao.output_values = [
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
                [14645900   , 2340509]]
    # Output values (Y)
    
    dea = DEAPY(distribuicao) # Dist
    dea.ccroomw()
    dea.ccriomw()
    dea.ccrioenv()
    dea.ccrooenv()
    dea.ccriosenv()
    dea.ccroosenv()
        #Eficiencia 
    #eficiencia = CCROOENVModel(provisao)
    #eficiencia.run()
    #for dmu, sol in eficiencia.solution.items():
    #    print(f"A eficiência reversa da DMU {sol.dmu_name} é de {sol.inverse_efficiency}")
#
    #for dmu, sol in eficiencia.solution.items():
    #    print(f"\n {sol.dmu_name} \n")
    #    for d in range(len(provisao.dmu_names)):
    #        print(sol.llambda[d])
#
    #    #Eficiencia Inversa 
    #eficiencia = CCRIOENVModel(provisao)
    #eficiencia.run()
    #for dmu, sol in eficiencia.solution.items():
    #    print(f"A eficiência da DMU {sol.dmu_name} é de {sol.efficiency}")
#
    #for dmu, sol in eficiencia.solution.items():
    #    print(f"\n {sol.dmu_name} \n")
    #    for d in range(len(provisao.dmu_names)):
    #        print(sol.llambda[d])




if __name__ == "__main__":
    main()
    
# a eficiência das DMUs 
# histograma das eficiências
# identifique as DMUs dentro das eficiências do histograma

# os benchmarks para cada DMU
# os pesos relativos dos inputs e outputs
# identifique as DMUs fortemente e fracamente eficientes
# apresente as projeções e metas para os inputs e outputs