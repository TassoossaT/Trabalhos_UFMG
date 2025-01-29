# TP1 - Ordenação Indireta

## Descrição do Projeto

Este projeto tem como objetivo implementar e comparar diferentes algoritmos de ordenação indireta. A ordenação indireta é uma técnica onde os dados não são movidos diretamente, mas sim através de índices ou ponteiros que referenciam os dados originais.

## Algoritmos Implementados

1. **InsertionQuickSort**: Combinação dos algoritmos de Insertion Sort e Quick Sort.
2. **QuickSort**: Algoritmo de ordenação rápida.
3. **HeapSort**: Algoritmo de ordenação baseado em heap.

## Estrutura dos Dados

Os dados são armazenados em uma lista sequencial (`SequentialList`) de objetos `DataRow`. Cada `DataRow` contém os seguintes campos:

- `name`: Nome do registro.
- `id`: Identificador do registro.
- `address`: Endereço do registro.
- `payload`: Dados adicionais do registro.

## Entrada e Saída

### Entrada

O programa lê os dados de um arquivo de entrada cujo nome é passado como argumento na linha de comando. O arquivo de entrada deve seguir o seguinte formato:

- As primeiras 5 linhas são ignoradas.
- A sexta linha contém o número de elementos.
- As linhas subsequentes contêm os dados dos registros, separados por vírgulas.

### Saída

Para cada combinação de algoritmo de ordenação e chave de ordenação (`name`, `id`, `address`), o programa gera um arquivo de log na pasta `output/<algoritmo>/<chave>.log`.

## Como Executar

Para compilar e executar o programa, utilize os seguintes comandos:
