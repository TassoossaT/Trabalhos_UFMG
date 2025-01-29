#include "../include/heap.hpp"
#include <iostream>
#include <stdexcept>

Heap::Heap(int maxsize) : tamanho(0) {
    data = new int[maxsize];
}

Heap::~Heap() {
    delete[] data;
}

void Heap::Inserir(int x) {
    if (tamanho == 0) {
        data[0] = x;
        tamanho++;
    } else {
        data[tamanho] = x;
        HeapifyPorCima(tamanho);
        tamanho++;
    }
}

int Heap::Remover() {
    if (Vazio()) {
        throw std::out_of_range("Heap is empty");
    }
    int root = data[0];
    data[0] = data[tamanho - 1];
    tamanho--;
    HeapifyPorBaixo(0);
    return root;
}

bool Heap::Vazio() {
    return tamanho == 0;
}

int Heap::GetAncestral(int posicao) {
    return (posicao - 1) / 2;
}

int Heap::GetSucessorEsq(int posicao) {
    return 2 * posicao + 1;
}

int Heap::GetSucessorDir(int posicao) {
    return 2 * posicao + 2;
}


// esse codigo no lugar dos dois Heapfy inverte ele do maiior para o menor
// void Heap::HeapifyPorBaixo(int posicao) {
//     int esq = GetSucessorEsq(posicao);
//     int dir = GetSucessorDir(posicao);
//     int maior = posicao;

//     if (esq < tamanho && data[esq] > data[maior]) {
//         maior = esq;
//     }

//     if (dir < tamanho && data[dir] > data[maior]) {
//         maior = dir;
//     }

//     if (maior != posicao) {
//         std::swap(data[posicao], data[maior]);
//         HeapifyPorBaixo(maior);
//     }
// }

// void Heap::HeapifyPorCima(int posicao) {
//     int ancestral = GetAncestral(posicao);
//     while (posicao > 0 && data[posicao] > data[ancestral]) {
//         std::swap(data[posicao], data[ancestral]);
//         posicao = ancestral;
//         ancestral = GetAncestral(posicao);
//     }
// }
void Heap::HeapifyPorBaixo(int posicao) {
    int esq = GetSucessorEsq(posicao);
    int dir = GetSucessorDir(posicao);
    int menor = posicao;

    if (esq < tamanho && data[esq] < data[menor]) {
        menor = esq;
    }

    if (dir < tamanho && data[dir] < data[menor]) {
        menor = dir;
    }

    if (menor != posicao) {
        std::swap(data[posicao], data[menor]);
        HeapifyPorBaixo(menor);
    }
}

void Heap::HeapifyPorCima(int posicao) {
    int ancestral = GetAncestral(posicao);
    while (posicao > 0 && data[posicao] < data[ancestral]) {
        std::swap(data[posicao], data[ancestral]);
        posicao = ancestral;
        ancestral = GetAncestral(posicao);
    }
}