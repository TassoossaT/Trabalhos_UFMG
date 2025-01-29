set I;  # Conjunto de pontos de demanda
set K;  # Conjunto de localiza��es candidatas para PCFs de n�vel 1
set J;  # Conjunto de localiza��es candidatas para PCFs de n�vel 2
set L;  # Conjunto de localiza��es candidatas para PCFs de n�vel 3
set E;  # Equipes de sa�de dispon�veis

param d1{i in I, k in K};  # Tempo de viagem de i para k (n�vel 1)
param d2{k in K, j in J};  # Tempo de viagem de k para j (n�vel 2)
param d3{j in J, l in L};  # Tempo de viagem de j para l (n�vel 3)

param w{i in I};           # Popula��o em cada ponto de demanda
param O1{k in K};          # Propor��o de pacientes de n�vel 1 referidos ao n�vel 2
param O2{j in J};          # Propor��o de pacientes de n�vel 2 referidos ao n�vel 3
param C1{e in E, k in K};  # Capacidade de n�vel 1 para local k
param C2{e in E, j in J};  # Capacidade de n�vel 2 para local j
param C3{e in E, l in L};  # Capacidade de n�vel 3 para local l
param p;                   # N�mero de PCFs de n�vel 1 a serem estabelecidos
param q;                   # N�mero de PCFs de n�vel 2 a serem estabelecidos
param r;                   # N�mero de PCFs de n�vel 3 a serem estabelecidos

var x1{k in K}, binary;    # 1 se PCF de n�vel 1 � aberto em k
var x2{j in J}, binary;    # 1 se PCF de n�vel 2 � aberto em j
var x3{l in L}, binary;    # 1 se PCF de n�vel 3 � aberto em l
var u{i in I, k in K} >= 0; # Fluxo de i para k (n�vel 1)
var v{k in K, j in J} >= 0; # Fluxo de k para j (n�vel 2)
var t{j in J, l in L} >= 0; # Fluxo de j para l (n�vel 3)

# Fun��o objetivo: minimizar custos
minimize Total_Cost:
    sum {e in E, k in K} C1[e, k] * x1[k] +
    sum {i in I, k in K} d1[i, k] * u[i, k] +
    sum {e in E, j in J} C2[e, j] * x2[j] +
    sum {k in K, j in J} d2[k, j] * v[k, j] +
    sum {e in E, l in L} C3[e, l] * x3[l] +
    sum {j in J, l in L} d3[j, l] * t[j, l];

# Restri��es
# 1. Cada ponto de demanda deve ser atendido
subject to Demand_Flow{i in I}:
    sum {k in K} u[i, k] = w[i];

# 2. Fluxo de n�vel 1 para n�vel 2
subject to Referral_Flow_Level1{k in K}:
    sum {j in J} v[k, j] = O1[k] * sum {i in I} u[i, k];

# 3. Fluxo de n�vel 2 para n�vel 3
subject to Referral_Flow_Level2{j in J}:
    sum {l in L} t[j, l] = O2[j] * sum {k in K} v[k, j];

# 4. Capacidade de n�vel 1
subject to Capacity_Level1{k in K}:
    sum {i in I} u[i, k] <= sum {e in E} C1[e, k] * x1[k];

# 5. Capacidade de n�vel 2
subject to Capacity_Level2{j in J}:
    sum {k in K} v[k, j] <= sum {e in E} C2[e, j] * x2[j];

# 6. Capacidade de n�vel 3
subject to Capacity_Level3{l in L}:
    sum {j in J} t[j, l] <= sum {e in E} C3[e, l] * x3[l];

# 7. N�mero de PCFs de n�vel 1
subject to Open_Level1:
    sum {k in K} x1[k] = p;

# 8. N�mero de PCFs de n�vel 2
subject to Open_Level2:
    sum {j in J} x2[j] = q;

# 9. N�mero de PCFs de n�vel 3
subject to Open_Level3:
    sum {l in L} x3[l] = r;


solve;

# Impress�o dos resultados
printf "\n===========================================\n";
printf "Hierarchical: %.2f\n", sum{i in I, k in K} d1[i,k] * u[i,k] + sum{k in K, j in J} d2[k,j] * v[k,j] + sum{j in J, l in L} d3[j,l] * t[j,l];
printf "Selected Locations in K: %d\n", sum{k in K} x1[k];
printf "Selected Locations in J: %d\n", sum{j in J} x2[j];
printf "Selected Locations in L: %d\n", sum{l in L} x3[l];
printf "\n===========================================\n";

# Exibe as aloca��es de n�vel 1 (ponto de demanda -> localiza��o de n�vel 1)
printf "\nAloca��es de n�vel 1 --> Localiza��es de N�vel 1:\n";
printf{i in I, k in K: u[i,k] > 0}:"[%d] --> [%d]: %.2f km\n", i, k, d1[i,k];
printf "\n===========================================\n";

# Exibe as aloca��es de n�vel 2 (localiza��o de n�vel 1 -> localiza��o de n�vel 2)
printf "\nSegundo N�vel --> Localiza��es de N�vel 2:\n";
printf{k in K, j in J: v[k,j] > 0}:"[%d] --> [%d]: %.2f km\n", k, j, d2[k,j];
printf "\n===========================================\n";

# Exibe as aloca��es de n�vel 3 (localiza��o de n�vel 2 -> localiza��es de n�vel 3)
printf "\nTerceiro N�vel --> Localiza��es de N�vel 3:\n";
printf{j in J, l in L: t[j,l] > 0}:"[%d] --> [%d]: %.2f km\n", j, l, d3[j,l];
printf "\n===========================================\n";

# Exibe as unidades utilizadas (PCF de cada n�vel)
printf "Unidades utilizadas nos PCFs de N�vel 1 (x1[k]):\n";
printf{k in K}:"PCF de N�vel 1 em [%d]: %.2f\n", k, x1[k];
printf "\n===========================================\n";
printf "Unidades utilizadas nos Hospitais de N�vel 2 (x2[j]):\n";
printf{j in J}:"Hospitais de N�vel 2 em [%d]: %.2f\n", j, x2[j];
printf "\n===========================================\n";
printf "Unidades utilizadas nos Centros de Complexidade de N�vel 3 (x3[l]):\n";
printf{l in L}:"Centros de Complexidade de N�vel 3 em [%d]: %.2f\n", l, x3[l];
printf "\n===========================================\n";

# Custo total
printf "Custo total: %.2f\n", Total_Cost;


end;
