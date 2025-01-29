# Relatório de Caracterização de Localidade de Referência

## Avaliação Qualitativa do Programa

O programa `matop` realiza operações com matrizes, como soma, multiplicação, transposição e criação de matrizes aleatórias. Em termos de acessos de memória, espera-se que o programa apresente um comportamento intensivo em leitura e escrita de dados, especialmente nas operações de soma e multiplicação de matrizes. A localidade de referência pode ser avaliada tanto em termos temporais quanto espaciais, dado que as operações de matriz geralmente acessam elementos adjacentes na memória.

**Estruturas de Dados Críticas:**

- Matrizes (`mat_tipo`): Acessos frequentes e intensivos durante operações de soma, multiplicação e transposição.
- Variáveis globais e locais: Utilizadas para armazenar dimensões e resultados intermediários.

**Segmentos de Código Críticos:**

- Funções de operações de matrizes (`somaMatrizes`, `multiplicaMatrizes`, `transpoeMatriz`): Executam a maior parte dos acessos de memória.
- Funções de inicialização e destruição de matrizes (`inicializaMatrizAleatoria`, `destroiMatriz`): Acessos iniciais e finais aos elementos das matrizes.

## Plano de Caracterização de Localidade de Referência

**Execuções e Ferramentas:**

- **Cachegrind**: Para analisar a eficiência do cache e os padrões de acesso à memória.
- **Callgrind**: Para obter um perfil detalhado das chamadas de função e identificar os segmentos de código mais custosos.

**Parâmetros do Programa:**

- Matrizes de tamanho médio (e.g., 100x100) para garantir que o programa não execute por muito ou pouco tempo, mas o suficiente para entender o comportamento do algoritmo.

## Execução com Cachegrind

1. Compile o programa:

   ```sh
   make
   ```

2. Execute o código com Cachegrind:

   ```sh
   valgrind --tool=cachegrind ./matop -m -x 5 -y 5
   ```

3. Anote os resultados:

   ```sh
   cg_annotate cachegrind.out.<número do processo>
   ```

## Execução com Callgrind

1. Execute o código com Callgrind:

   ```sh
   valgrind --tool=callgrind ./matop -m -x 5 -y 5
   ```

2. Anote os resultados:

   ```sh
   callgrind_annotate callgrind.out.<número do processo>
   ```

## Avaliação das Saídas do Cachegrind/Callgrind

**Comportamento de Memória:**

- **Cachegrind**: Avaliar a taxa de acertos e falhas de cache, identificando se o programa está utilizando eficientemente o cache.
- **Callgrind**: Identificar as funções que mais consomem tempo e acessos de memória, permitindo focar na otimização dessas partes.

**Estruturas de Dados a Serem Caracterizadas:**

- Matrizes (`mat_tipo`): Devido ao alto número de acessos durante as operações.

**Segmentos de Código a Serem Instrumentados:**

- Funções de operações de matrizes (`somaMatrizes`, `multiplicaMatrizes`, `transpoeMatriz`): Para entender melhor os padrões de acesso e identificar possíveis otimizações.

## Informações Adicionais

Inclua capturas de tela das saídas do Cachegrind e Callgrind, bem como trechos de código relevantes e suas anotações. Isso ajudará a ilustrar os pontos críticos e as áreas de melhoria.
