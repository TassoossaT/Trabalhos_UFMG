import numpy as np
from matplotlib import pyplot as plt
from numpy.linalg import inv, norm

class Solution:
    def __init__(self, x=None, fx=None, iter=None, aval=None, xhist=None,
                 fxhist=None):
        self.x = x.reshape(x.size)
        self.fx = fx
        self.iter = iter
        self.aval = aval
        self.xhist = xhist
        self.fxhist = fxhist

    def resultados(self, func, xlim, ylim, levels=None):
    
        # Malha para plotar contorno
        x1, x2 = np.meshgrid(np.linspace(xlim[0], xlim[1]),
                             np.linspace(ylim[0], ylim[1]))

        # Avalia função para plotar contorno
        f = np.zeros(x1.shape)
        for i in range(x1.shape[0]):
            for j in range(x1.shape[1]):
                f[i, j] = func(np.array([x1[i, j], x2[i, j]]))

        # Plota trajetória
        _, axis = plt.subplots(ncols=2, figsize=[2*6.4, 4.8])
        if levels is not None:
            axis[0].contour(x1, x2, f, levels=levels)
        else:
            
            
            
            axis[0].contour(x1, x2, f, levels=30)
        axis[0].plot(self.xhist[:, 0], self.xhist[:, 1], '--*r')
        axis[0].set_xlabel(r'$x_1$')
        axis[0].set_ylabel(r'$x_2$')
        axis[0].set_title('Problema')
        axis[0].grid()

        # Plota convergencia
        axis[1].plot(self.fxhist, '--*')
        axis[1].set_xlabel('Iterações')
        axis[1].set_ylabel(r'$f(\mathbf{x})$')
        axis[1].set_title('Convergência')
        axis[1].grid()

        plt.tight_layout()
        plt.show()
    
    def __str__(self):
        mensagem = ''
        mensagem += 'Solução ótima: ' + str(self.x) + '\n'
        mensagem += 'Número de iterações: %d\n' % self.iter
        mensagem += 'Número de avaliações: %d' % self.aval
        return mensagem

class Unidimensional:
    def __init__(self):
        pass
    def solve(self):
        pass

class Eliminacao(Unidimensional):

    def __init__(self, passo=1e-2, aceleracao=1.5, maxaval=100):
        self.passo = passo
        self.aceleracao = aceleracao
        self.maxaval = maxaval

    def resolva(self, func):
        # Intervalo inicial
        passo = self.passo
        a = 0
        b = passo
        
        # Avaliação do intervalo inicial
        fa = func(a)
        fb = func(b)
        avaliacoes = 2
        
        # Marca o limite inferior anterior
        anterior = 0
        
        # Enquanto eu estiver descendo
        while fb < fa:
            
            # Salvo o valor do limite inferior anterior
            anterior = a
            
            # Novo limite inferior é o atual limite máximo
            a = b
            fa = fb
            
            # Acelero o passo
            passo = passo*self.aceleracao
            
            # Dou um passo a frente no intervalo
            b += passo
            fb = func(b)
            avaliacoes += 1
                    
        # Retorno o intervalo final
        return anterior, b, avaliacoes

class Exaustiva(Eliminacao):

    def __init__(self, npontos=8, precisao=1e-3, passo=0.01, aceleracao=1.5,
                 maxaval=100):
        super().__init__(passo, aceleracao, maxaval=maxaval)
        self.precisao = precisao
        self.npontos = npontos

    def resolva(self, func):
        a, b, avaliacoes = super().resolva(func)  
        fa = func(a)
        fb = func(b)
        avaliacoes += 2
        
        # Enquanto o meu intervalo não for reduzido
        # a um tamanho suficientemente pequeno
        while (b-a) > self.precisao and avaliacoes < self.maxaval:
            
            # Divide o intervalo em npontos equidistantes
            x = np.linspace(a, b, self.npontos)
            
            # Vetor que vai carregar a avaliação de cada ponto
            fx = np.zeros(x.size)
            
            # O primeiro e o último pontos são a e b
            fx[0] = fa
            fx[-1] = fb
            
            # Avalia todos os outros pontos
            for n in range(1, self.npontos-1):
                fx[n] = func(x[n])
                avaliacoes += 1
                
            # Acha quem é o menor
            n = np.argmin(fx)
            
            # O novo limite inferior é o ponto anterior do menor
            a = x[n-1]
            fa = fx[n-1]

            # O novo limite superior é o ponto anterior do menor
            b = x[n+1]
            fb = fx[n+1]
                
        # A aproximação do meu ótimo é o meio do meu intervalo
        return (a+b)/2, avaliacoes

class Dicotomica(Eliminacao):

    def __init__(self, precisao=1e-3, passo=0.01, aceleracao=1.5, maxaval=100):
        super().__init__(passo=passo, aceleracao=aceleracao, maxaval=maxaval)
        self.precisao = precisao

    def resolva(self, func):
        a, b, avaliacoes = super().resolva(func)        

        # Enquanto o meu intervalo não for reduzido
        # a um tamanho suficientemente pequeno
        while (b-a) > self.precisao and avaliacoes < self.maxaval:
            
            # Calcula o comprimento do intervalo
            L = b-a
            
            # Calcula o valor de delta
            delta = .25*L
            
            # Determina os dois pontos intermediarios
            u = a + L/2-delta/2
            v = a + L/2+delta/2
            fu = func(u)
            fv = func(v)
            avaliacoes += 2
            
            # Se fv for maior que fu, então v é o novo b
            if fu < fv:
                b = v
                fb = fv
                
            # Se fu for maior que fv, então u é o novo a
            else:
                a = u
                fa = fu
        
        # A aproximação do meu ótimo é o meio do meu intervalo
        return (a+b)/2, avaliacoes

class Bissecao(Eliminacao):

    def __init__(self, precisao=1e-3, passo=0.01, aceleracao=1.5, maxaval=100):
        super().__init__(passo=passo, aceleracao=aceleracao, maxaval=maxaval)
        self.precisao = precisao

    def resolva(self, func):
        a, b, avaliacoes = super().resolva(func)        

        # Calcula e avalia o ponto no meio do intervalo
        c = (a+b)/2
        fc = func(c)
        avaliacoes += 1

        # Enquanto o meu intervalo não for reduzido
        # a um tamanho suficientemente pequeno
        while (b-a) > self.precisao and avaliacoes < self.maxaval:        
            
            # Calcula o comprimento do intervalo
            L = b-a
            
            # Ponto médio entre a e c
            u = a + L/4
            
            # Ponto médio entre c e b
            v = a + L*3/4
            
            # Avaliações
            fu = func(u)
            fv = func(v)
            avaliacoes += 2
            
            # Se fu é o menor, então excluímos o intervalo (c, b)
            if fu < fc and fc < fv:
                b, fb = c, fc
                c, fc = u, fu

            # Se fv é o menor, então excluímos o intervalo (a, c)
            elif fu > fc and fc > fv:
                a, fa = c, fc
                c, fc = v, fv
            
            # Se fc é o menor, então excluímos os intervalos (a, u) e (v, c)
            elif fu > fc and fv > fc:
                a, fa = u, fu
                b, fb = v, fv
            
        # A aproximação do meu ótimo é o meio do meu intervalo
        return (a+b)/2, avaliacoes

class Fibonacci(Eliminacao):

    def __init__(self, maxiter=100, precisao=1e-3, passo=0.01, aceleracao=1.5,
                 maxaval=100):
        super().__init__(passo=passo, aceleracao=aceleracao, maxaval=maxaval)
        self.precisao = precisao
        self.maxiter = maxiter

    def resolva(self, func):
        a, b, avaliacoes = super().resolva(func)        

        # Contador de termos de Fibonacci
        k = 1
        
        # Calcula o comprimento do intervalo
        L = b-a
        
        # Calcula a sequência de Fibonacci
        F = np.zeros(self.maxiter+1)
        F[:2] = 1.
        for i in range(2, F.size):
            F[i] = F[i-1] + F[i-2]
        F = F[::-1]
        
        # Determina dois pontos médios
        u = b - F[k]/F[k-1]*L
        v = a + F[k]/F[k-1]*L
        
        # Avalia
        fu = func(u)
        fv = func(v)
        avaliacoes += 2
        
        # Avança para o próximo termo
        k += 1

        # Enquanto o meu intervalo não for reduzido
        # a um tamanho suficientemente pequeno
        while (k <= self.maxiter and (b-a) > self.precisao
               and avaliacoes < self.maxaval):        
            
            # Exclui intervalo (v, c)
            if fu < fv:
                b, fb = v, fv
                v, fv = u, fu
                L = b-a
                u = b - F[k]/F[k-1]*L
                fu = func(u)
            
            # Exclui intervalo (a, u)
            else:
                a, fa = u, fu
                u, fu = v, fv
                L = b-a
                v = a + F[k]/F[k-1]*L
                fv = func(v)
            
            avaliacoes += 1
            
            # Avança para o próximo termo
            k += 1
        
        # A aproximação do meu ótimo é o meio do meu intervalo
        return (a+b)/2, avaliacoes

class SecaoAurea(Eliminacao):

    def __init__(self, precisao=1e-3, passo=0.01, aceleracao=1.5, maxaval=100):
        super().__init__(passo=passo, aceleracao=aceleracao, maxaval=maxaval)
        self.precisao = precisao

    def resolva(self, func):
        a, b, avaliacoes = super().resolva(func)        

        # Calcula o comprimento do intervalo
        L = b-a
        
        # Determina dois pontos médios
        u = b - .618*L
        v = a + .618*L
        
        # Avalia
        fu = func(u)
        fv = func(v)
        avaliacoes += 2

        # Enquanto o meu intervalo não for reduzido
        # a um tamanho suficientemente pequeno
        while (b-a) > self.precisao and avaliacoes < self.maxaval:        
            
            if fu < fv:
                
                # Exclui o intervalo (v, b)
                b = v
                
                # Atualiza o novo comprimento do intervalo
                L = b-a
                
                # Faz de u o novo v
                v, fv = u, fu
                
                # Calcula o novo u
                u = b -.618*L
                fu = func(u)
            
            # Se fu > fv
            else:
                
                # Exclui o intervalo (a, u)
                a = u
                
                # Atualiza o novo comprimento do intervalo
                L = b-a
                
                # Faz de v o novo u
                u, fu = v, fv
                
                # Calcula o novo u
                v = a + .618*L
                fv = func(v)
            
            avaliacoes += 1
        
        # A aproximação do meu ótimo é o meio do meu intervalo
        return (a+b)/2, avaliacoes

class Interpolacao(Unidimensional):

    def __init__(self, precisao=1e-3, maxaval=100):
        self.precisao = precisao
        self.maxaval = maxaval
    
    def resolva(self, func, x0=None):
        if x0 is None:
            x0 = np.zeros(2)  
        return func(x0)

class Quadratica(Interpolacao):
    def __init__(self, precisao=1e-3, passo=1e-5, maxaval=100):
        super().__init__(precisao=precisao, maxaval=maxaval)
        self.passo = passo
    
    def resolva(self, func):
        f0 = super().resolva(func)
        
        # O ponto inicial é sempre zero
        A, fA = 0., f0
        
        # O ponto do meio é um passo
        B, fB = self.passo, func(self.passo)
        
        # O terceiro são dois passos
        C, fC = 2*self.passo, func(2*self.passo)
        avaliacoes = 2
        
        # Termos do polinômio equivalente: a + b*x + c*x^2
        a = (fA*B*C*(C-B) + fB*C*A*(A-C) + fC*A*B*(B-A))/((A-B)*(B-C)*(C-A))
        b = (fA*(B*B-C*C) + fB*(C*C-A*A) + fC*(A*A-B*B))/((A-B)*(B-C)*(C-A))
        c = - (fA*(B-C) + fB*(C-A) + fC*(A-B))/((A-B)*(B-C)*(C-A))
        
        # Ponto de ótimo do polinômio aproximado
        xopt = -b/2/c
        fopt = func(xopt)
        avaliacoes += 1
        
        # Enquanto a avaliação do mínimo do polinônio aproximado
        # não for suficientemente igual ao f(x)
        while (np.abs((a+b*xopt+c*xopt**2 - fopt)/fopt) > self.precisao
               and avaliacoes < self.maxaval):
            
            # Atualização dos três pontos de interpolação
            if xopt > B and fopt < fB:
                A, fA = B, fB
                B, fB = xopt, fopt
            elif xopt > B and fopt > fB:
                C, fC = xopt, fopt
            elif xopt < B and fopt < fB:
                C, fC = B, fB
                B, fB = xopt, fopt
            elif xopt < B and fopt > fB:
                A, fA = xopt, fopt
        
            # Novos termos do polinômio equivalente: a + b*x + c*x^2
            a = (fA*B*C*(C-B) + fB*C*A*(A-C) + fC*A*B*(B-A))/((A-B)*(B-C)*(C-A))
            b = (fA*(B*B-C*C) + fB*(C*C-A*A) + fC*(A*A-B*B))/((A-B)*(B-C)*(C-A))
            c = - (fA*(B-C) + fB*(C-A) + fC*(A-B))/((A-B)*(B-C)*(C-A))
            
            # Novo ponto de ótimo do polinômio aproximado
            xopt = -b/2/c
            fopt = func(xopt)
            avaliacoes += 1
        
        return xopt, avaliacoes

class QuasiNewton(Interpolacao):
    def __init__(self, precisao=1e-3, pertubacao=1e-8, maxiter=200,
                 maxaval=100):
        super().__init__(precisao=precisao, maxaval=maxaval)
        self.pertubacao = pertubacao
        self.maxiter = maxiter
    
    def resolva(self, func):
        f0 = super().resolva(func)
        
        # Pertubação pequena para estimativa da derivada
        delta = self.pertubacao
        
        # Ponto inicial
        x, fx = 0., f0
        
        # Calcula f(x+delta) e f(x-delta)
        fxm = func(x-delta)
        fxp = func(x+delta)
        avaliacoes = 2

        # Estima a primeira derivada
        fp = (fxp-fxm)/(2*delta)
        
        # Estima a segunda derivada
        fpp = (fxp-2*fx+fxm)/(delta**2)
        
        # Enquanto a primeira derivada não for
        # tão próxima de zero
        k = 0
        while (np.abs(fp) > self.precisao and k < self.maxiter
               and avaliacoes < self.maxaval):
            
            # Fórmula de Newton
            x = x - delta*fp/fpp
        
            # Recalcula f(x+delta) e f(x-delta) para novo ponto
            fxm = func(x-delta)
            fxp = func(x+delta)
            avaliacoes += 2

            # Estima a primeira derivada
            fp = (fxp-fxm)/(2*delta)
            
            # Estima a segunda derivada
            fpp = (fxp-2*fx+fxm)/(delta**2)
            
            k += 1
        
        return x, avaliacoes

class Secante(Interpolacao):
    def __init__(self, precisao=1e-3, pertubacao=1e-8, maxaval=100):
        super().__init__(precisao=precisao, maxaval=maxaval)
        self.pertubacao = pertubacao
    
    def resolva(self, func):
        f0 = super().resolva(func)
        
        # Pertubação pequena para estimativa da derivada
        delta = self.pertubacao
        
        # Ponto inicial
        A, fA = 0, f0
        
        # Derivada no ponto inicial
        fD = func(delta)
        fpA = (fD-fA)/delta
        
        # Segundo ponto e sua derivada
        t0, fpt0 = delta, (func(2*delta)-fD)/delta
        avaliacoes = 2
        
        # Enquanto a derivada do segundo ponto não estiver acima de zero
        while fpt0 < 0 and avaliacoes < self.maxaval:
            
            # O primeiro ponto é atualizado
            A, fpA = t0, fpt0
            
            # É dado um novo passo e calculado a sua derivada
            t0 = 2*t0
            fpt0 = (func(t0+delta)-func(t0))/delta
            avaliacoes += 2

        # O ponto A é um ponto com derivada negativa
        # enquanto o ponto B é um ponto com derivada positiva
        B, fpB = t0, fpt0
        
        while True:
            
            # Atualização de x:
            # O ponto onde a reta que une os dois pontos (secante)
            # toca o zero no eixo-y da derivada
            x = A - (fpA*(B-A))/(fpB-fpA)
            
            # Reavalia a derivada
            fpx = (func(x+delta)-func(x))/delta
            avaliacoes += 2
            
            # Se a derivada for suficientemente
            # próxima de zero
            if np.abs(fpx) <= self.precisao:
                break
            elif avaliacoes >= self.maxaval:
                break
            
            # A derivada está acima de zero,
            # então atualiza B
            if fpx >= 0:
                B, fpB = x, fpx
            
            # A derivada está abaixo de zero,
            # então atualiza B
            else:
                A, fpA = x, fpx
            
        return x, avaliacoes

class Metodo:

    def __init__(self, maxit=10000, maxaval=10000):
        self.maxit = maxit
        self.maxaval = maxaval

    def resolva(self, func, x0):
        # Definição inicial das variáveis do processo iterativo
        # if type(x0) is list:
        #     x = np.array(x0, dtype=float).reshape((-1, 1))
        # else:
        #     x = np.array(x0, dtype=float).reshape((-1, 1))
        x = np.array(x0, dtype=float).reshape((-1, 1))
        fx = func(x)
        if isinstance(fx, float):
            fx = np.array(fx)
        '''
        Eu estava tendo um problema com o formato de dados em um ponto específico, isso é para debug
        o problema era muito simples:
                if isinstance(fx, float):
                fx = np.array([fx])
        basicamente o primeiro fx me retornava um array 2D com uma linha e três colunas, e os proximos fx me retornava um array 1D com três elementos
        '''
        xhist = [np.copy(x)]
        fxhist = [fx]
        iter = 0
        aval = 1
        
        return x, fx, xhist, fxhist, iter, aval


class DirecoesAleatorias(Metodo):

    def __init__(self, unidimensional, maxit=10000, maxaval=10000):
        super().__init__(maxit=maxit, maxaval=maxaval)
        self.unidimensional = unidimensional

    def resolva(self, func, x0):
        x, fx, xhist, fxhist, iter, aval = super().resolva(func, x0)

        # Critério de parada
        while iter < self.maxit and aval < self.maxaval:
        
            # Define a direção de busca aleatoriamente
            d = np.random.normal(size=x.shape)
            
            # Se a direção obtida não aponta para minimização
            if func(x + 1e-15*d) > fx:
                d = -d
            aval += 1
                
            # A função que representará nossa otimização unidimensional
            def theta(alpha):
                fx = func(x + alpha*d)
                return fx

            # Otimização unidimensional para determinar o passo na direção d
            alpha, na = self.unidimensional.resolva(theta)
            aval += na
                
            # Atualiza
            x = x + alpha*d
            fx = func(x)
            aval += 1
            iter += 1
                
            xhist.append(np.copy(x))
            fxhist.append(fx)

        xhist = np.array(xhist)
        fxhist = np.array(fxhist)

        return Solution(x=x, fx=fx, iter=iter, aval=aval, xhist=xhist,
                        fxhist=fxhist)

# Calculo numérico das derivadas
def gradiente(x, func, fx=None, metodo='progressiva', delta=1e-10):

    avaliacoes = 0

    if fx is None:
        fx = func(x)
        avaliacoes +=1

    # Inicializa o vetor gradiente
    grad = np.zeros((x.size, 1))
    
    # Para cada variável
    for n in range(x.size):
        
        # Vetor com 1 na posição da variável onde a derivada será calculada
        e = np.zeros(x.size)
        e[n] = 1
        
        # Estima a derivada no ponto
        if metodo == 'regressiva':
            grad[n] = (fx - func(x.flatten() - delta*e))/delta # O(delta)
            avaliacoes += 1
        elif metodo == 'central':
            grad[n] = (func(x.flatten() + delta*e) - func(x.flatten() - delta*e))/(2*delta) # O(delta**2)
            avaliacoes += 2
        else:
            grad[n] = (func(x.flatten() + delta*e)-fx)/delta # O(delta)
            avaliacoes += 1
    
    return grad, avaliacoes
class Gradiente(Metodo):
    def __init__(self, unidimensional, diferenca='progressiva', maxit=10000,
                 maxaval=10000, precisao=1e-3):
        super().__init__(maxit=maxit, maxaval=maxaval)
        self.unidimensional = unidimensional
        self.diferenca = diferenca
        self.precisao = precisao

    def resolva(self, func, x0):
        x, fx, xhist, fxhist, iter, aval = super().resolva(func, x0)
        # --- BLOCO DE VERIFICAÇÃO ADICIONADO AQUI ---

        grad = 2*self.precisao*np.ones(x.size)
        
        # Critério de parada
        while (iter < self.maxit and aval < self.maxaval and norm(grad) > self.precisao):
        
            # Define a direção de busca baseado no gradiente
            grad, na = gradiente(x, func, fx=fx, metodo=self.diferenca)
            aval += na
            d = -grad

            # A função que representará nossa otimização unidimensional
            def theta(alpha):
                fx = func(x.flatten() + alpha*d.flatten())
                return fx

            # Otimização unidimensional para determinar o passo na direção d
            alpha, na = self.unidimensional.resolva(theta)
            aval += na
                
            # Atualiza

            x = x + alpha*d
            fx = func(x)
            aval += 1
            iter += 1

            xhist.append(np.copy(x))
            fxhist.append(fx)

        xhist = np.array(xhist)
        fxhist = np.array(fxhist)

        return Solution(x=x, fx=fx, iter=iter, aval=aval, xhist=xhist,fxhist=fxhist)

def hessiana(x, func, fx=None, grad=None, delta=1e-10):
    
    if grad is None:
        grad, navaliacoes = gradiente(x, func, fx=fx, delta=delta)
    else:
        navaliacoes = 0
    
    # A Hessiana é uma matriz quadrada do tamanho do número de variáveis
    H = np.zeros((x.size, x.size))    
    
    # Para cada variável...
    for n in range(x.size):
        
        # Perturbação na n-ésima variável
        e = np.zeros(x.shape)
        e[n] = 1

        # Calcula o gradiente nesse ponto perturbado
        gpert, nava = gradiente(x + delta*e, func)
        
        navaliacoes += nava

        # Calcula uma coluna da Hessiana
        H[:, n] = (gpert.flatten()-grad.flatten())/delta

    return H, navaliacoes

class Newton(Metodo):

    def __init__(self, unidimensional, maxit=10000,
                 maxaval=10000, precisao=1e-3):
        super().__init__(maxit=maxit, maxaval=maxaval)
        self.unidimensional = unidimensional
        self.precisao = precisao

    def resolva(self, func, x0):
        x, fx, xhist, fxhist, iter, aval = super().resolva(func, x0)
        grad = 2*self.precisao*np.ones(x.shape)
        # Critério de parada
        while (iter < self.maxit and aval < self.maxaval
               and norm(grad) > self.precisao):
        
            # Define a direção de busca
            grad, avg = gradiente(x, func, fx=fx)
            H, avh = hessiana(x, func, grad=grad)
            aval += avg + avh

            try:
                d = -inv(H) @ grad
                if d.T @ grad > 0:
                    d = -d
            
            # Matriz singular
            except:
                print("Matriz singular encontrada. Parando o algortimo...")
                xhist = np.array(xhist)
                fxhist = np.array(fxhist)
                return Solution(x=x, fx=fx, iter=iter, aval=aval, xhist=xhist,
                                fxhist=fxhist)

            # A função que representará nossa otimização unidimensional
            def theta(alpha):
                fx = func(x.flatten() + alpha*d.flatten())
                return fx

            # Otimização unidimensional para determinar o passo na direção d
            alpha, na = self.unidimensional.resolva(theta)
            aval += na
                
            # Atualiza
            x = x + alpha*d
            fx = func(x)
            
            aval += 1
            iter += 1
                
            xhist.append(np.copy(x))
            fxhist.append(fx)

        xhist = np.array(xhist)
        fxhist = np.array(fxhist)

        return Solution(x=x, fx=fx, iter=iter, aval=aval, xhist=xhist,
                        fxhist=fxhist)

class DFP(Metodo):

    def __init__(self, unidimensional, maxit=10000, maxaval=10000, precisao=1e-3):
        super().__init__(maxit=maxit, maxaval=maxaval)
        self.unidimensional = unidimensional
        self.precisao = precisao

    def resolva(self, func, x0):
        x, fx, xhist, fxhist, iter, aval = super().resolva(func, x0)
        
        # Aproximação inicial da inversa da matriz hessiana
        Hh = np.eye(x.size)

        # Primeira estimativa do gradiente
        g, na = gradiente(x, func=func, fx=fx)
        aval += na
        
        # Critério de parada
        while (iter < self.maxit and aval < self.maxaval
               and norm(g) > self.precisao):
        
            # Determina a direção de busca
            d = - Hh @ g
            
            # Função de otimização unidimensional
            # A função que representará nossa otimização unidimensional
            def theta(alpha):
                fx = func(x.flatten() + alpha*d.flatten())
                return fx

            # Determina o passo ótimo    
            alpha, na = self.unidimensional.resolva(theta)
            aval += na

            # Grava informações antes do passo
            xanterior = x.copy()
            ganterior = g.copy()
            
            # Atualiza
            x = x + alpha*d
            fx = func(x.flatten())
            aval += 1

            # Estima novo gradiente
            g, na = gradiente(x, func=func, fx=fx) 
            aval += na
            
            xhist.append(np.copy(x))
            fxhist.append(fx)

            # Atualiza vetores v e r
            v = xanterior-x
            r = ganterior-g
            
            # Coloca na forma vetor-coluna
            v = v.reshape((-1, 1))
            r = r.reshape((-1, 1))

            # Atualização de Hh
            Hh = Hh + v@v.T/(v.T@r) - Hh@r@r.T@Hh/(r.T@Hh@r)
            
            iter += 1

        xhist = np.array(xhist)
        fxhist = np.array(fxhist)

        return Solution(x=x, fx=fx, iter=iter, aval=aval, xhist=xhist,
                        fxhist=fxhist)

class BFGS(Metodo):

    def __init__(self, unidimensional, maxit=10000, maxaval=10000, precisao=1e-3):
        super().__init__(maxit=maxit, maxaval=maxaval)
        self.unidimensional = unidimensional
        self.precisao = precisao

    def resolva(self, func, x0):
        x, fx, xhist, fxhist, iter, aval = super().resolva(func, x0)
        
        # Aproximação inicial da inversa da matriz hessiana
        Hh = np.eye(x.size)

        # Primeira estimativa do gradiente
        g, na = gradiente(x, func=func, fx=fx)
        aval += na
        
        # Critério de parada
        while (iter < self.maxit and aval < self.maxaval
               and norm(g) > self.precisao):
        
            # Determina a direção de busca
            d = - Hh @ g
            
            # Função de otimização unidimensional
            # A função que representará nossa otimização unidimensional
            def theta(alpha):
                fx = func(x + alpha*d)
                return fx

            # Determina o passo ótimo    
            alpha, na = self.unidimensional.resolva(theta)
            aval += na

            # Grava informações antes do passo
            xanterior = x.copy()
            ganterior = g.copy()
            
            # Atualiza
            x = x + alpha*d
            fx = func(x)
            aval += 1

            # Estima novo gradiente
            g, na = gradiente(x, func=func, fx=fx) 
            aval += na
            
            xhist.append(np.copy(x))
            fxhist.append(fx)

            # Atualiza vetores v e r
            v = xanterior-x
            r = ganterior-g
            
            # Coloca na forma vetor-coluna
            v = v.reshape((-1, 1))
            r = r.reshape((-1, 1))

            # Atualização de Hh
            Hh = (Hh + (1 + r.T@Hh@r/(r.T@v))*v@v.T/(v.T@r) 
                  - (v@r.T@Hh + Hh@r@v.T)/(r.T@v))

            iter += 1

        xhist = np.array(xhist)
        fxhist = np.array(fxhist)

        return Solution(x=x, fx=fx, iter=iter, aval=aval, xhist=xhist,
                        fxhist=fxhist)        

class QuasiNewton(Metodo):

    def __init__(self, unidimensional, qsi=.5, maxit=10000, maxaval=10000,
                 precisao=1e-3):
        super().__init__(maxit=maxit, maxaval=maxaval)
        self.unidimensional = unidimensional
        self.qsi = qsi
        self.precisao = precisao

    def resolva(self, func, x0):
        x, fx, xhist, fxhist, iter, aval = super().resolva(func, x0)
        
        # Aproximação inicial da inversa da matriz hessiana
        Hh = np.eye(x.size)

        # Primeira estimativa do gradiente
        g, na = gradiente(x, func=func, fx=fx)
        aval += na
        
        # Critério de parada
        while (iter < self.maxit and aval < self.maxaval
               and norm(g) > self.precisao):
        
            # Determina a direção de busca
            d = - Hh @ g
            
            # Função de otimização unidimensional
            # A função que representará nossa otimização unidimensional
            def theta(alpha):
                fx = func(x + alpha*d)
                return fx

            # Determina o passo ótimo    
            alpha, na = self.unidimensional.resolva(theta)
            aval += na

            # Grava informações antes do passo
            xanterior = x.copy()
            ganterior = g.copy()
            
            # Atualiza
            x = x + alpha*d
            fx = func(x)
            aval += 1

            # Estima novo gradiente
            g, na = gradiente(x, func=func, fx=fx) 
            aval += na
            
            xhist.append(np.copy(x))
            fxhist.append(fx)

            # Atualiza vetores v e r
            v = xanterior-x
            r = ganterior-g
            
            # Coloca na forma vetor-coluna
            v = v.reshape((-1, 1))
            r = r.reshape((-1, 1))

            # Atualização de Hh
            C_DFP = v@v.T/(v.T@r) - Hh@r@r.T@Hh/(r.T@Hh@r)
            C_BFGS = ((1 + r.T@Hh@r/(r.T@v))*v@v.T/(v.T@r) 
                      - (v@r.T@Hh + Hh@r@v.T)/(r.T@v))
            
            Hh += (1-self.qsi)*C_DFP + self.qsi*C_BFGS
            iter += 1

        xhist = np.array(xhist)
        fxhist = np.array(fxhist)

        return Solution(x=x, fx=fx, iter=iter, aval=aval, xhist=xhist,
                        fxhist=fxhist)        

class GradienteConjugado(Metodo):

    def __init__(self, unidimensional, formula='fletcher-reeves', maxit=10000,
                 maxaval=10000, precisao=1e-3):
        super().__init__(maxit=maxit, maxaval=maxaval)
        self.unidimensional = unidimensional
        self.formula = formula
        self.precisao = precisao

    def resolva(self, func, x0):
        x, fx, xhist, fxhist, iter, aval = super().resolva(func, x0)
        # Primeira estimativa do gradiente
        g, na = gradiente(x, func=func, fx=fx)
        aval += na
        # Define resíduos e direção de busca
        r = -g
        d = r.copy()
        # Critério de parada
        while (iter < self.maxit and aval < self.maxaval and norm(g) > self.precisao):
            # Função de otimização unidimensional
            def theta(alpha):
                return func(x + alpha*d)
            # Determina o passo ótimo    
            alpha, na = self.unidimensional.resolva(theta)
            aval += na
            # Atualiza
            x = x + alpha*d
            fx = func(x)
            aval += 1
            xhist.append(np.copy(x))
            fxhist.append(fx)
            # Guarda o resíduo anterior
            r_ant = r.copy()
            # Estima novo gradiente
            g, na = gradiente(x, func=func, fx=fx)
            aval += na
            # Novo resíduo
            r = -g
            # Cálculo do conjugado do gradiente
            if self.formula == 'fletcher-reeves':
                beta = float((r.T @ r) / (r_ant.T @ r_ant))
            else: # Polak-Ribière
                beta = float((r.T @ (r - r_ant)) / (r_ant.T @ r_ant))
            # Protege contra beta negativo ou nan
            if np.isnan(beta) or beta < 0 or np.isinf(beta):
                beta = 0.0
            # Atualiza a direção de busca
            d = r + beta*d
            # Reinicia a direção a cada n variáveis (para problemas mal-condicionados)
            if (iter+1) % x.size == 0:
                d = r.copy()
            # Debug prints
            print(f"Iteração {iter+1} | fx: {fx} | ||g||: {norm(g)} | alpha: {alpha} | beta: {beta}")
            iter += 1
        xhist = np.array(xhist)
        fxhist = np.array(fxhist)
        return Solution(x=x, fx=fx, iter=iter, aval=aval, xhist=xhist, fxhist=fxhist)

class HookeJeeves(Metodo):
    
    def __init__(self, passo_coordenada=0.5, passo_direcao=0.1, maxit=10000,
                 maxaval=10000, precisao=1e-3):
        super().__init__(maxit=maxit, maxaval=maxaval)
        self.lamb = passo_coordenada
        self.alpha = passo_direcao
        self.precisao = precisao

    def resolva(self, func, x0):
        x, fx, xhist, fxhist, iter, aval = super().resolva(func, x0)
        
        # Número de variáveis
        N = x.size
        
        lamb = self.lamb
        alpha = self.alpha
        
        while iter < self.maxit and aval < self.maxaval:
                
            """ Busca em cada coordenada """
            y = np.copy(x)
            xt = np.copy(x)
            for n in range(N):
                
                # Dou um passo em um eixo
                xt[n] = x[n] + lamb
                fxt = func(xt)
                aval += 1
                
                # Se eu melhorei dando esse passo
                if fxt < fx:
                    y[n] = xt[n]
                    continue # Salvo esse passo e vou para próxima variável
                
                # Se eu tiver piorado, dou um passo no sentido contrário
                xt[n] = x[n] - lamb
                fxt = func(xt)
                aval += 1
                
                # Se eu melhorei dando esse passo
                if fxt < fx:
                    y[n] = xt[n]
                    continue # Salvo esse passo e vou para próxima variável
                
                # Caso contrário, eu fico com o mesmo valor
                y[n] = x[n]

            """ Busca na direção """
            fy = func(y)
            aval += 1
            
            # Se minha busca por coordenada retornou uma solução melhor
            if fy < fx:
                
                # Tento dar um passo na direção final que eu andei
                z = y + alpha*(y-x)
                fz = func(z)
                aval += 1
                
                # Caso esse passo seja melhor, atualiza 
                if fz < fy:
                    x = z
                    fx = fz
                
                # Fica com o anterior e diminui o passo nessa direção
                else:
                    x = y
                    fx = fy
                    alpha = alpha/2
            
            # Reduz o passo em cada coordenada
            else:
                lamb = lamb/2
            
            xhist.append(np.copy(x))
            fxhist.append(fx)
            iter += 1
            
            if iter > 5 and norm(x-xhist[-5]) < self.precisao:
                break

        xhist = np.array(xhist)
        fxhist = np.array(fxhist)

        return Solution(x=x, fx=fx, iter=iter, aval=aval, xhist=xhist,
                        fxhist=fxhist)  

class NelderMeadSimplex(Metodo):
    
    def __init__(self, reflexao=1.0, contracao=0.5, expansao=2.,
                 encolhimento=0.5, maxit=10000, maxaval=10000, precisao=1e-3):
        super().__init__(maxit=maxit, maxaval=maxaval)
        self.alpha = reflexao
        self.beta = contracao
        self.gamma = expansao
        self.delta = encolhimento
        self.precisao = precisao

    def resolva(self, func, x0):
        x, fx, xhist, fxhist, iter, aval = super().resolva(func, x0)
        
        # Variáveis do método
        num_variaveis = x.size
        num_pontos = num_variaveis + 1

        # Inicialização do simplex
        simplex = self._calcule_simplex_inicial(x)
        valores = np.array([func(ponto) for ponto in simplex]).flatten()
        aval += num_pontos

        # Registros
        xhist = [x.reshape(x.size)]
        fxhist = [fx.item()]
        simplexhist = [simplex.copy()]

        # Critério de parada: número de iterações ou a diferença dos pontos do simplex
        # ser pequena demais
        while iter < self.maxit and aval < self.maxaval:

            # Ordenar o simplex: o primeiro ponto é o melhor e o último é o pior
            ordem = np.argsort(valores)
            simplex = simplex[ordem]
            valores = valores[ordem]

            # Nomes dos pontos
            xb, fb = simplex[0], valores[0] # Melhor ponto
            xs, fs = simplex[-2], valores[-2] # Segundo pior ponto
            xw, fw = simplex[-1], valores[-1] # Pior ponto

            # Calcular o centro do simplex, excluindo o pior ponto
            centroide = np.mean(simplex[:-1], axis=0)
            xh = centroide # Um nome mais curto para o centróide

            # Primeira tentativa: reflexão
            xr = xh + self.alpha*(xh - xw)
            fr = func(xr)
            aval += 1

            # Caso a reflexão seja melhor que o melhor ponto do simplex
            if fr < fb:

                # Segunda tentativa: expansão
                xe = xh + self.gamma*(xr - xh)
                fe = func(xe)
                aval += 1

                # Se a expansão for melhor ainda que a reflexão, fica com a expansão
                if fe < fr:
                    simplex[-1] = xe
                    valores[-1] = fe
                
                # Se a expansão não for melhor que a reflexão, fica com a reflexão
                else:
                    simplex[-1] = xr
                    valores[-1] = fr

            # Caso a reflexão não seja melhor que o melhor ponto do simplex,
            # mas seja pelo menos melhor que o segundo pior ponto
            elif fb <= fr < fs:

                # Fica com a reflexão
                simplex[-1] = xr
                valores[-1] = fr

            # Caso a reflexão seja pior que o segundo pior ponto, mas melhor que o pior 
            # ponto
            elif fs <= fr < fw:
                    
                # Terceira tentativa: contração
                xc = xh + self.beta*(xr - xh)
                fc = func(xc)
                aval += 1
            
                # Se a contração for melhor que o ponto da reflexão, substitui o pior
                # ponto pelo ponto da contração
                if fc < fr:
                    simplex[-1] = xc
                    valores[-1] = fc

                # Se a contração não for melhor que o ponto da reflexão, substitui o
                # pior ponto pelo ponto da reflexão
                else:
                    simplex[-1] = xr
                    valores[-1] = fr

            # Caso a reflexão seja pior que o pior ponto
            else:

                # Encolhimento do simplex
                for i in range(1, num_pontos):
                    simplex[i] = (simplex[i] + xb)*self.delta
                    valores[i] = func(simplex[i])
                    aval += 1

            # Registros
            iter += 1
            xhist.append(simplex[0].reshape(x.size))
            fxhist.append(valores[0])
            simplexhist.append(simplex.copy())
            
            if np.max(np.abs(simplex[1:] - simplex[0])) <= self.precisao:
                break

        xhist = np.array(xhist)
        fxhist = np.array(fxhist)
        solucao = Solution(x=simplex[0].reshape(x.size), fx=valores[0],
                           iter=iter, aval=aval, xhist=xhist, fxhist=fxhist) 
        solucao.simplexhist = np.array(simplexhist)

        return solucao

    def _calcule_simplex_inicial(self, ponto_inicial):
        num_variaveis = ponto_inicial.size
        num_pontos = num_variaveis + 1
        simplex_inicial = [ponto_inicial]
        a = num_pontos
        n = num_variaveis
        p = a/(n*np.sqrt(2))*(np.sqrt(n+1) + n - 1)
        q = a/(n*np.sqrt(2))*(np.sqrt(n+1) - 1)
        u = np.eye(n)
        for i in range(num_variaveis):
            ponto = ponto_inicial.copy()
            ponto += p*u[i, :].reshape(ponto.shape)
            for j in range(n):
                if j != i:
                    ponto += q*u[j, :].reshape(ponto.shape)
            simplex_inicial.append(ponto)
        return np.array(simplex_inicial)
