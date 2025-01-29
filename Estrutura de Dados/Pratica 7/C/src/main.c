#include "../include/graph.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int isComplete(Grafo* grafo) {
    int n = QuantidadeVertices(grafo);
    int m = QuantidadeArestas(grafo);
    return m == (n * (n - 1)) / 2;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <operation>\n", argv[0]);
        return 1;
    }

    char* operation = argv[1];
    Grafo* grafo = NovoGrafo();
    int n, m, vizinho;

    scanf("%d", &n);

    for (int i = 0; i < n; ++i) {
        InsereVertice(grafo);
    }

    for (int i = 0; i < n; ++i) {
        scanf("%d", &m);
        for (int j = 0; j < m; ++j) {
            scanf("%d", &vizinho);
            InsereAresta(grafo, i, vizinho);
        }
    }

    if (strcmp(operation, "-d") == 0) {
        printf("%d\n", QuantidadeVertices(grafo));
        printf("%d\n", QuantidadeArestas(grafo));
        printf("%d\n", GrauMinimo(grafo));
        printf("%d\n", GrauMaximo(grafo));
    } else if (strcmp(operation, "-n") == 0) {
        for (int i = 0; i < n; ++i) {
            ImprimeVizinhos(grafo, i);
        }
    } else if (strcmp(operation, "-k") == 0) {
        printf("%d\n", isComplete(grafo) ? 1 : 0);
    } else {
        fprintf(stderr, "Invalid operation: %s\n", operation);
        DeletaGrafo(grafo);
        return 1;
    }

    DeletaGrafo(grafo);
    return 0;
}