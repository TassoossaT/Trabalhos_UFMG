#include "../include/graph.hpp"
#include <iostream>
#include <string>

bool isComplete(Grafo& grafo)
{
    int n = grafo.QuantidadeVertices();
    int m = grafo.QuantidadeArestas();
    return m == (n * (n - 1)) / 2;
}

int main(int argc, char* argv[])
{
    if (argc < 2)
    {
        std::cerr << "Usage: " << argv[0] << " <operation>" << std::endl;
        return 1;
    }

    std::string operation = argv[1];
    Grafo grafo;
    int n, m, vizinho;

    std::cin >> n;

    for (int i = 0; i < n; ++i)
    {
        grafo.InsereVertice();
    }

    for (int i = 0; i < n; ++i)
    {
        std::cin >> m;
        for (int j = 0; j < m; ++j)
        {
            std::cin >> vizinho;
            grafo.InsereAresta(i, vizinho);
        }
    }

    if (operation == "-d")
    {
        std::cout << grafo.QuantidadeVertices() << std::endl;
        std::cout << grafo.QuantidadeArestas() << std::endl;
        std::cout << grafo.GrauMinimo() << std::endl;
        std::cout << grafo.GrauMaximo() << std::endl;
    }
    else if (operation == "-n")
    {
        for (int i = 0; i < n; ++i)
        {
            grafo.ImprimeVizinhos(i);
        }
    }
    else if (operation == "-k")
    {
        std::cout << (isComplete(grafo) ? 1 : 0) << std::endl;
    }
    else
    {
        std::cerr << "Invalid operation: " << operation << std::endl;
        return 1;
    }

    return 0;
}
