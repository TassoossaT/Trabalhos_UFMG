#include "../include/heap.h"
#include <stdlib.h>
#include <stdio.h>

Heap* NovoHeap(int maxsize) {
    Heap* h = (Heap*)malloc(sizeof(Heap));
    h->tamanho = 0;
    h->dados = (int*)malloc(maxsize * sizeof(int));
    return h;
}

void DeletaHeap(Heap* h) {
    free(h->dados);
    free(h);
}

void Inserir(Heap* h, int x) {
    h->dados[h->tamanho] = x;
    HeapifyPorCima(h, h->tamanho);
    h->tamanho++;
}

int Remover(Heap* h) {
    if (Vazio(h)) {
        return -1; // Heap is empty
    }
    int root = h->dados[0];
    h->dados[0] = h->dados[h->tamanho - 1];
    h->tamanho--;
    HeapifyPorBaixo(h, 0);
    return root;
}

int GetAncestral(Heap* h, int posicao) {
    return (posicao - 1) / 2;
}

int GetSucessorEsq(Heap* h, int posicao) {
    return 2 * posicao + 1;
}

int GetSucessorDir(Heap* h, int posicao) {
    return 2 * posicao + 2;
}

int Vazio(Heap* h) {
    return h->tamanho == 0;
}
// esse codigo no lugar dos dois Heapfy inverte ele do maiior para o menor
// void HeapifyPorBaixo(Heap* h, int posicao) {
//     int esq = GetSucessorEsq(h, posicao);
//     int dir = GetSucessorDir(h, posicao);
//     int maior = posicao;

//     if (esq < h->tamanho && h->dados[esq] > h->dados[maior]) {
//         maior = esq;
//     }
//     if (dir < h->tamanho && h->dados[dir] > h->dados[maior]) {
//         maior = dir;
//     }
//     if (maior != posicao) {
//         int temp = h->dados[posicao];
//         h->dados[posicao] = h->dados[maior];
//         h->dados[maior] = temp;
//         HeapifyPorBaixo(h, maior);
//     }
// }

// void HeapifyPorCima(Heap* h, int posicao) {
//     int ancestral = GetAncestral(h, posicao);
//     while (posicao > 0 && h->dados[posicao] > h->dados[ancestral]) {
//         int temp = h->dados[posicao];
//         h->dados[posicao] = h->dados[ancestral];
//         h->dados[ancestral] = temp;
//         posicao = ancestral;
//         ancestral = GetAncestral(h, posicao);
//     }
// }
void HeapifyPorBaixo(Heap* h, int posicao) {
    int esq = GetSucessorEsq(h, posicao);
    int dir = GetSucessorDir(h, posicao);
    int menor = posicao;

    if (esq < h->tamanho && h->dados[esq] < h->dados[menor]) {
        menor = esq;
    }
    if (dir < h->tamanho && h->dados[dir] < h->dados[menor]) {
        menor = dir;
    }
    if (menor != posicao) {
        int temp = h->dados[posicao];
        h->dados[posicao] = h->dados[menor];
        h->dados[menor] = temp;
        HeapifyPorBaixo(h, menor);
    }
}

void HeapifyPorCima(Heap* h, int posicao) {
    int ancestral = GetAncestral(h, posicao);
    while (posicao > 0 && h->dados[posicao] < h->dados[ancestral]) {
        int temp = h->dados[posicao];
        h->dados[posicao] = h->dados[ancestral];
        h->dados[ancestral] = temp;
        posicao = ancestral;
        ancestral = GetAncestral(h, posicao);
    }
}