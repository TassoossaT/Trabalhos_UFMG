#include "../include/heap.h"
#include <stdio.h>
#include <stdlib.h>

int main() {
    int n;
    scanf("%d", &n);

    Heap* heap = NovoHeap(n);

    for (int i = 0; i < n; ++i) {
        int element;
        scanf("%d", &element);
        Inserir(heap, element);
    }

    while (!Vazio(heap)) {
        printf("%d ", Remover(heap));
    }

    DeletaHeap(heap);
    return 0;
}