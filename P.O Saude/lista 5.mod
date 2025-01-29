set I;  # Conjunto de pontos de demanda
set K;  # Conjunto de localizações candidatas para PCFs de nível 1
set J;  # Conjunto de localizações candidatas para PCFs de nível 2
set L;  # Conjunto de localizações candidatas para PCFs de nível 3
set E;  # Equipes de saúde disponíveis

param d1{i in I, k in K};  # Tempo de viagem de i para k (nível 1)
param d2{k in K, j in J};  # Tempo de viagem de k para j (nível 2)
param d3{j in J, l in L};  # Tempo de viagem de j para l (nível 3)

param w{i in I};           # População em cada ponto de demanda
param O1{k in K};          # Proporção de pacientes de nível 1 referidos ao nível 2
param O2{j in J};          # Proporção de pacientes de nível 2 referidos ao nível 3
param C1{e in E, k in K};  # Capacidade de nível 1 para local k
param C2{e in E, j in J};  # Capacidade de nível 2 para local j
param C3{e in E, l in L};  # Capacidade de nível 3 para local l
param p;                   # Número de PCFs de nível 1 a serem estabelecidos
param q;                   # Número de PCFs de nível 2 a serem estabelecidos
param r;                   # Número de PCFs de nível 3 a serem estabelecidos

var x1{k in K}, binary;    # 1 se PCF de nível 1 é aberto em k
var x2{j in J}, binary;    # 1 se PCF de nível 2 é aberto em j
var x3{l in L}, binary;    # 1 se PCF de nível 3 é aberto em l
var u{i in I, k in K} >= 0; # Fluxo de i para k (nível 1)
var v{k in K, j in J} >= 0; # Fluxo de k para j (nível 2)
var t{j in J, l in L} >= 0; # Fluxo de j para l (nível 3)

# Função objetivo: minimizar custos
minimize Total_Cost:
    sum {e in E, k in K} C1[e, k] * x1[k] +
    sum {i in I, k in K} d1[i, k] * u[i, k] +
    sum {e in E, j in J} C2[e, j] * x2[j] +
    sum {k in K, j in J} d2[k, j] * v[k, j] +
    sum {e in E, l in L} C3[e, l] * x3[l] +
    sum {j in J, l in L} d3[j, l] * t[j, l];

# Restrições
# 1. Cada ponto de demanda deve ser atendido
subject to Demand_Flow{i in I}:
    sum {k in K} u[i, k] = w[i];

# 2. Fluxo de nível 1 para nível 2
subject to Referral_Flow_Level1{k in K}:
    sum {j in J} v[k, j] = O1[k] * sum {i in I} u[i, k];

# 3. Fluxo de nível 2 para nível 3
subject to Referral_Flow_Level2{j in J}:
    sum {l in L} t[j, l] = O2[j] * sum {k in K} v[k, j];

# 4. Capacidade de nível 1
subject to Capacity_Level1{k in K}:
    sum {i in I} u[i, k] <= sum {e in E} C1[e, k] * x1[k];

# 5. Capacidade de nível 2
subject to Capacity_Level2{j in J}:
    sum {k in K} v[k, j] <= sum {e in E} C2[e, j] * x2[j];

# 6. Capacidade de nível 3
subject to Capacity_Level3{l in L}:
    sum {j in J} t[j, l] <= sum {e in E} C3[e, l] * x3[l];

# 7. Número de PCFs de nível 1
subject to Open_Level1:
    sum {k in K} x1[k] = p;

# 8. Número de PCFs de nível 2
subject to Open_Level2:
    sum {j in J} x2[j] = q;

# 9. Número de PCFs de nível 3
subject to Open_Level3:
    sum {l in L} x3[l] = r;


solve;

# Impressão dos resultados
printf "\n===========================================\n";
printf "Hierarchical: %.2f\n", sum{i in I, k in K} d1[i,k] * u[i,k] + sum{k in K, j in J} d2[k,j] * v[k,j] + sum{j in J, l in L} d3[j,l] * t[j,l];
printf "Selected Locations in K: %d\n", sum{k in K} x1[k];
printf "Selected Locations in J: %d\n", sum{j in J} x2[j];
printf "Selected Locations in L: %d\n", sum{l in L} x3[l];
printf "\n===========================================\n";

# Exibe as alocações de nível 1 (ponto de demanda -> localização de nível 1)
printf "\nAlocações de nível 1 --> Localizações de Nível 1:\n";
printf{i in I, k in K: u[i,k] > 0}:"[%d] --> [%d]: %.2f km\n", i, k, d1[i,k];
printf "\n===========================================\n";

# Exibe as alocações de nível 2 (localização de nível 1 -> localização de nível 2)
printf "\nSegundo Nível --> Localizações de Nível 2:\n";
printf{k in K, j in J: v[k,j] > 0}:"[%d] --> [%d]: %.2f km\n", k, j, d2[k,j];
printf "\n===========================================\n";

# Exibe as alocações de nível 3 (localização de nível 2 -> localizações de nível 3)
printf "\nTerceiro Nível --> Localizações de Nível 3:\n";
printf{j in J, l in L: t[j,l] > 0}:"[%d] --> [%d]: %.2f km\n", j, l, d3[j,l];
printf "\n===========================================\n";

# Exibe as unidades utilizadas (PCF de cada nível)
printf "Unidades utilizadas nos PCFs de Nível 1 (x1[k]):\n";
printf{k in K}:"PCF de Nível 1 em [%d]: %.2f\n", k, x1[k];
printf "\n===========================================\n";
printf "Unidades utilizadas nos Hospitais de Nível 2 (x2[j]):\n";
printf{j in J}:"Hospitais de Nível 2 em [%d]: %.2f\n", j, x2[j];
printf "\n===========================================\n";
printf "Unidades utilizadas nos Centros de Complexidade de Nível 3 (x3[l]):\n";
printf{l in L}:"Centros de Complexidade de Nível 3 em [%d]: %.2f\n", l, x3[l];
printf "\n===========================================\n";

# Custo total
printf "Custo total: %.2f\n", Total_Cost;


end;
