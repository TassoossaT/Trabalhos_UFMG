#include <stdio.h>
#include <stdlib.h>

int main(int argc, char** argv){
    int i;
    int *a = malloc(sizeof(int) * 10);
    if (!a) return -1; /*malloc failed*/
    for (i = 0; i < 10; i++){//i até 10, ou seja o loop vai de 0 a 9
        a[i] = i;
    }
    free(a);
    return 0;
}
