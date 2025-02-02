from deapy import DEAData, DEAPY
import sys

def main():
    data = DEAData()
    # nome das DMUs
    data.dmu_names = ['A','B','C','D','E','F','H']
    # nome dos inputs (X)
    data.input_names = ['I1','I2']
    # nome dos outputs (Y)
    data.output_names = ['O1']

    # input values (X)
    data.input_values = [   [4, 3], 
                            [7, 3], 
                            [8, 1], 
                            [4, 2], 
                            [2, 4], 
                            [10, 1], 
                            [3, 7] ]

    data.output_values = [  [1] ,
                            [1] ,
                            [1] ,
                            [1] ,
                            [1] ,
                            [1] ,
                            [1]]


    data.print() 
    dea = DEAPY(data)
    dea.ccriomw()
    dea.ccroomw()
    dea.ccrioenv()
    dea.ccrooenv()
    dea.ccriosenv()
    dea.ccroosenv()


if __name__ == "__main__":
    main()
