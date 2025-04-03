entrada = 1

class queueMMm:
    def __init__(self, TaxaEnt, TempAtt, m):
        self.λ = 1/(TaxaEnt/60)#convertendo para minutos
        self.𝜇 = 1/(TempAtt/60)
        self.m = m
    def 𝜌(self):#𝜌
        return self.λ/(self.𝜇*self.m)
    def lq(self):# número médio de usuários em fila.
        𝜌 = self.𝜌()
        return 𝜌*𝜌/(1-𝜌)
    def ls(self):# número médio de usuários em serviço.
        return self.𝜌()
    def L(self):# número médio de usuários no sistema.
        return self.lq() + self.ls()
    def wq(self): # tempo médio de cada usuários em fila.
        return self.lq()/self.λ
    def S(self):# tempo médio de cada usuários em serviço.
        return 1/self.𝜇
    def W(self):# tempo médio de cada usuários no sistema.
        return self.wq() + self.S()
    # def Little(self):
    #     return self.λ*self.W()

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    temps = []
    cad_wq = []
    mass_wq = []
    carCentr_wq = []
    centri_wq = []
    carEstr_wq = []
    estrat_wq = []
    for tempochegada in range(64, 301):#se chegar uma a menos do que 61s não entra em equilibrio
        # corteRabo       = queueMMm(tempochegada, 2, 1)#muito rapido para gravar 
        cadastro        = queueMMm(tempochegada, 24, 1)
        massagem        = queueMMm(tempochegada, 190, 3)#pode ter até 3 pessoas massageando pelo que deu pra ver
        # pesagem         = queueMMm(tempochegada*12, 10, 1)
        carCentrifuga   = queueMMm(tempochegada*12, 120, 1)#espera chegar 12 bolsas para centrifugar
        centrifuga      = queueMMm(tempochegada*12, 1142, 5)
        carEstratora    = queueMMm(tempochegada, 60, 1)
        estratora       = queueMMm(tempochegada, 306, 14)
        
        temps.append(tempochegada)
        cad_wq.append(cadastro.wq())
        mass_wq.append(massagem.wq())
        carCentr_wq.append(carCentrifuga.wq())
        centri_wq.append(centrifuga.wq())
        carEstr_wq.append(carEstratora.wq())
        estrat_wq.append(estratora.wq())
        tempotot = cadastro.wq() + massagem.wq() + carCentrifuga.wq() + centrifuga.wq() + carEstratora.wq() + estratora.wq()
        print(f"tempochegada: {tempochegada:.2f}, Fila total: {tempotot:.2f} cadastro: {cadastro.wq():.2f} massagem: {massagem.wq():.2f} carCentrifuga: {carCentrifuga.wq():.2f} centrifuga: {centrifuga.wq():.2f} carEstratora: {carEstratora.wq():.2f} estratora: {estratora.wq():.2f}")
    # plt.plot(temps, cad_wq, label="Cadastro")
    # plt.plot(temps, mass_wq, label="Massagem")
    # plt.plot(temps, carCentr_wq, label="Car_Centrifuga")
    # plt.plot(temps, centri_wq, label="Centrifuga")
    # plt.plot(temps, carEstr_wq, label="Car_Estratora")
    # plt.plot(temps, estrat_wq, label="Estratora")
    # plt.xlabel("Tempochegada (s)")
    # plt.ylabel("Tempo médio em fila")
    # plt.legend()
    # plt.show()
    # temps = []
    # cad_wq = []
    # mass_wq = []
    # carCentr_wq = []
    # centri_wq = []
    # carEstr_wq = []
    # estrat_wq = []
    # for tempochegada in range(6334, 6450):#se chegar uma a menos do que 61s não entra em equilibrio
    #     tempochegada = tempochegada/100
    #     # corteRabo       = queueMMm(tempochegada, 2, 1)#muito rapido para gravar 
    #     cadastro        = queueMMm(tempochegada, 24, 1)
    #     massagem        = queueMMm(tempochegada, 190, 3)#pode ter até 3 pessoas massageando pelo que deu pra ver
    #     # pesagem         = queueMMm(tempochegada*12, 10, 1)
    #     carCentrifuga   = queueMMm(tempochegada*12, 120, 1)#espera chegar 12 bolsas para centrifugar
    #     centrifuga      = queueMMm(tempochegada*12, 1142, 5)
    #     carEstratora    = queueMMm(tempochegada, 60, 1)
    #     estratora       = queueMMm(tempochegada, 306, 14)
        
    #     temps.append(tempochegada)
    #     cad_wq.append(cadastro.S())
    #     mass_wq.append(massagem.S())
    #     carCentr_wq.append(carCentrifuga.S())
    #     centri_wq.append(centrifuga.S())
    #     carEstr_wq.append(carEstratora.S())
    #     estrat_wq.append(estratora.wq())
    # plt.plot(temps, cad_wq, label="Cadastro")
    # plt.plot(temps, mass_wq, label="Massagem")
    # plt.plot(temps, carCentr_wq, label="Car_Centrifuga")
    # plt.plot(temps, centri_wq, label="Centrifuga")
    # plt.plot(temps, carEstr_wq, label="Car_Estratora")
    # plt.plot(temps, estrat_wq, label="Estratora")
    # plt.xlabel("Tempochegada (s)")
    # plt.ylabel("Tempo médio em fila")
    # plt.legend()
    # plt.show()