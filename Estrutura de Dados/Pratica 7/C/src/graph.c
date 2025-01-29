#include <stdio.h>
#include <stdlib.h>
#include "graph.h"

typedef struct s_node {
    int vertex;
    struct s_node* next;
} Node;

struct s_grafo {
    int numVertices;
    int numEdges;
    Node** adjLists;
};

Grafo* NovoGrafo() {
    Grafo* g = (Grafo*)malloc(sizeof(Grafo));
    g->numVertices = 0;
    g->numEdges = 0;
    g->adjLists = NULL;
    return g;
}

void DeletaGrafo(Grafo* g) {
    for (int i = 0; i < g->numVertices; i++) {
        Node* temp = g->adjLists[i];
        while (temp) {
            Node* toDelete = temp;
            temp = temp->next;
            free(toDelete);
        }
    }
    free(g->adjLists);
    free(g);
}

void InsereVertice(Grafo* g) {
    g->numVertices++;
    g->adjLists = (Node**)realloc(g->adjLists, g->numVertices * sizeof(Node*));
    g->adjLists[g->numVertices - 1] = NULL;
}

void InsereAresta(Grafo* g, int v, int w) {
    Node* newNode = (Node*)malloc(sizeof(Node));
    newNode->vertex = w;
    newNode->next = g->adjLists[v];
    g->adjLists[v] = newNode;
    g->numEdges++;
}

int QuantidadeVertices(Grafo* g) {
    return g->numVertices;
}

int QuantidadeArestas(Grafo* g) {
    return g->numEdges;
}

int GrauMinimo(Grafo* g) {
    int min = 10000;
    for (int i = 0; i < g->numVertices; i++) {
        int degree = 0;
        Node* temp = g->adjLists[i];
        while (temp) {
            degree++;
            temp = temp->next;
        }
        if (degree < min) {
            min = degree;
        }
    }
    return min;
}

int GrauMaximo(Grafo* g) {
    int max = 0;
    for (int i = 0; i < g->numVertices; i++) {
        int degree = 0;
        Node* temp = g->adjLists[i];
        while (temp) {
            degree++;
            temp = temp->next;
        }
        if (degree > max) {
            max = degree;
        }
    }
    return max;
}

void ImprimeVizinhos(Grafo* g, int v) {
    if (v >= g->numVertices) return;

    Node* edges = g->adjLists[v];
    if (!edges) return;

    // Find the length of the edge list
    int length = 0;
    Node* temp = edges;
    while (temp) {
        length++;
        temp = temp->next;
    }

    // Print the edges in reverse order
    for (int i = length - 1; i >= 0; --i) {
        temp = edges;
        for (int j = 0; j < i; ++j) {
            temp = temp->next;
        }
        printf("%d ", temp->vertex);
    }
    printf("\n");
}
