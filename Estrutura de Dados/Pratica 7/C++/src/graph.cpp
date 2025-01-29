#include "../include/graph.hpp"
#include <iostream>
#include <algorithm>

Grafo::Grafo() : numVertices(0), numArestas(0) {}

Grafo::~Grafo() {}

void Grafo::InsereVertice()
{
    vertices.append(numVertices);
    numVertices++;
}

void Grafo::InsereAresta(int v, int w)
{
    if (v < numVertices && w < numVertices)
    {
        vertices.addEdge(v, w);
        numArestas++;
    }
}

int Grafo::QuantidadeVertices()
{
    return numVertices;
}

int Grafo::QuantidadeArestas()
{
    return numArestas;
}

int Grafo::GrauMinimo()
{
    int grau_min = numVertices;
    for (int i = 0; i < numVertices; i++)
    {
        int grau = 0;
        EdgeNode* edges = vertices.getEdges(i);
        while (edges)
        {
            grau++;
            edges = edges->next;
        }
        if (grau < grau_min)
        {
            grau_min = grau;
        }
    }
    return grau_min;
}

int Grafo::GrauMaximo()
{
    int grau_max = 0;
    for (int i = 0; i < numVertices; i++)
    {
        int grau = 0;
        EdgeNode* edges = vertices.getEdges(i);
        while (edges)
        {
            grau++;
            edges = edges->next;
        }
        if (grau > grau_max)
        {
            grau_max = grau;
        }
    }
    return grau_max;
}

void Grafo::ImprimeVizinhos(int v)
{
    if (v < numVertices)
    {
        EdgeNode* edges = vertices.getEdges(v);
        if (!edges) return;

        // Find the length of the edge list
        int length = 0;
        EdgeNode* temp = edges;
        while (temp)
        {
            length++;
            temp = temp->next;
        }
        for (int i = length - 1; i >= 0; --i)
        {
            temp = edges;
            for (int j = 0; j < i; ++j)
            {
                temp = temp->next;
            }
            std::cout << temp->data << " ";
        }
        std::cout << std::endl;
    }
}
