#include "../include/declaration.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <unistd.h>

alg_t algvet[]={
    {ALGINSERTION,"i"},
    {ALGSELECTION,"s"},
    {ALGQSORT,    "q"},
    {ALGQSORT3,   "q3"},
    {ALGQSORTINS, "qi"},
    {ALGQSORT3INS,"q3i"},
    {ALGSHELLSORT,"h"},
    {ALGRECSEL,   "rs"},
    {0,0}
};

int name2num(char * name){
    int i=0;
    while (algvet[i].num){
        if (!strcmp(algvet[i].name,name)) return algvet[i].num;
        i++;
    }
    return 0;
}

char * num2name(int num){
    int i=0;
    while (algvet[i].num){
        if (algvet[i].num==num) return algvet[i].name;
        i++;
    }
    return 0;
}
void uso()
// Descricao: imprime as opcoes de uso
// Entrada: nao tem
// Saida: impressao das opcoes de linha de comando
{
    fprintf(stderr,"sortperf\n");
    fprintf(stderr,"\t-z <int>\t(vector size)\n");
    fprintf(stderr,"\t-s <int>\t(initialization seed)\n");
    fprintf(stderr,"\t-a <s|i|q|q3|qi|q3i|h|rs>\t(algorithm)\n");
    fprintf(stderr,"\t    s\tselection\n");
    fprintf(stderr,"\t    i\tinsertion\n");
    fprintf(stderr,"\t    q\tquicksort\n");
    fprintf(stderr,"\t    q3\tquicksort+median3\n");
    fprintf(stderr,"\t    qi\tquicksort+insertion\n");
    fprintf(stderr,"\t    q3i\tquicksort+median3+insertion\n");
    fprintf(stderr,"\t    h\theapsort\n");
    fprintf(stderr,"\t    rs\trecursive selection\n");
}

void resetcounter(sortperf_t * s){
// Descricao: inicializa estrutura
// Entrada: 
// Saida: s
    s->cmp = 0;
    s->move = 0;
    s->calls = 0;
}

void inccmp(sortperf_t * s, int num){
// Descricao: incrementa o numero de comparacoes em num 
// Entrada: s, num
// Saida: s
    s->cmp += num;
}

void incmove(sortperf_t * s, int num){
// Descricao: incrementa o numero de movimentacoes de dados em num 
// Entrada: s, num
// Saida: s
    s->move += num;
}

void inccalls(sortperf_t * s, int num){
// Descricao: incrementa o numero de chamadas de função em num 
// Entrada: s, num
// Saida: s
    s->calls += num;
}

char * printsortperf(sortperf_t * s, char * str, char * pref){
// Descricao: gera string com valores de sortperf 
// Entrada: s, pref
// Saida: str

    sprintf(str,"%s cmp %d move %d calls %d", pref, s->cmp, s->move, s->calls); 
    return str;
}

void initVector(int * vet, int size){
// Descricao: inicializa vet com valores aleatorios
// Entrada: vet
// Saida: vet
    int i;
    // inicializa a parte alocada da vetor com valores aleatorios
    for (i=0; i<size; i++){
        vet[i] = (int)(drand48()*size);
    }
}

void printVector(int * vet, int size){
// Descricao: inicializa vet com valores aleatorios
// Entrada: vet
// Saida: vet
    int i;
    for (i=0; i<size; i++){
        printf("%d ",vet[i]);
    }
    printf("\n");
}

void swap(int *xp, int *yp, sortperf_t *s){
    int temp = *xp;
    *xp = *yp;
    *yp = temp;
    incmove(s,3);
}

// median of 3 integers
int median (int a, int b, int c) {
    if ((a <= b) && (b <= c)) return b;  // a b c
    if ((a <= c) && (c <= b)) return c;  // a c b
    if ((b <= a) && (a <= c)) return a;  // b a c
    if ((b <= c) && (c <= a)) return c;  // b c a
    if ((c <= a) && (a <= b)) return a;  // c a b
    return b;                            // c b a
}

// recursive selection sort
void recursiveSelectionSort(int *A, int l, int r, sortperf_t * s)
{
    // find the minimum element in the unsorted subarray `[i…n-1]`
    // and swap it with `arr[i]`
    int min = l;
    inccalls(s,1);
    for (int j = l + 1; j <= r; j++)
    {
        // if `arr[j]` is less, then it is the new minimum
        inccmp(s,1);
        if (A[j] < A[min]) {
            min = j;    // update the index of minimum element
        }
    }

    // swap the minimum element in subarray `arr[i…n-1]` with `arr[i]`
    if (min!=l)
        swap(&A[min], &A[l], s);

    if (l + 1 < r) {
        recursiveSelectionSort(A, l + 1, r, s);
    }
}

// shellsort
void shellSort(int *A, int n, sortperf_t * s)
{
    inccalls(s,1);// chamada for 
    for (int h = n / 2; h > 0; h /= 2)
    {
        inccalls(s,1);// chamada for 
        for (int i = h; i < n; i += 1) 
        {
            incmove(s,1);
            int temp = A[i];
            int j;
            inccalls(s,1);// chamada for 
            for (j = i; j >= h && A[j-h] > temp; j-= h)
            {
                incmove(s,1);
                A[j] = A[j - h];
            }
            incmove(s,1);
            A[j] = temp;
        }
    }
}


// selection sort
void selectionSort(int * A, int l, int r, sortperf_t * s)
{
    int j, Min;
    inccalls(s,1);
    for (l = 0; l < r - 1; l++)
    {
        Min = l;
        inccalls(s,1);
        for (j = l + 1 ; j < r; j++)
        {
            inccmp(s,1);
            if (A[j] < A[Min])
                Min = j;
        }
        swap(&A[l], &A[Min],s);
    }
}

//insertion sort
void insertionSort(int *A, int l, int r, sortperf_t * s)
{
    int j;
    int aux;
    inccalls(s,1);
    for (l = 1; l < r; l++)
    {
        incmove(s,1);
        aux = A[l];
        j = l - 1;
        inccalls(s,1);
        while (( j >= 0 ) && (aux < A[j]))
        {
            inccmp(s,2);
            incmove(s,1);
            A[j + 1] = A[j];
            j--;
        }
        incmove(s,1);
        A[j + 1] = aux;
    }
}


// quicksort partition using median of 3
void partition3(int * A, int l, int r, int *i, int *j, sortperf_t *s)
// inccmp   incrementa o numero de comparacoes 
// incmove  incrementa o numero de movimentacoes de dados
// inccalls incrementa o numero de chamadas de função
{
    int x, w;
    *i = l; 
    *j = r;
    x = A[(*i + *j)/2]; /* obtem o pivo x */
    x = median(x,*i,*j);// n pega um pivor extremo
    inccalls(s,1);
    do
    { 
        inccalls(s,1);
        while (x > A[*i]) (*i)++;
        inccalls(s,1);
        while (x < A[*j]) (*j)--;
        inccmp(s,1);
        if (*i <= *j)
        {
            incmove(s,1);
            w     = A[*i];
            incmove(s,1);
            A[*i] = A[*j];
            incmove(s,1);
            A[*j] = w;
            (*i)++; 
            (*j)--;
        }
    inccmp(s,1);
    } while (*i <= *j);
}

// standard quicksort partition
void partition(int * A, int l, int r, int *i, int *j, sortperf_t *s)
{
    int x, w;
    *i = l; 
    *j = r;
    x = A[(*i + *j)/2]; /* obtem o pivo x */
    inccalls(s,1);
    do
    { 
        inccalls(s,1);
        while (x > A[*i]) (*i)++;
        inccalls(s,1);
        while (x < A[*j]) (*j)--;
        inccmp(s,1);
        if (*i <= *j)
        {
            incmove(s,1);
            w     = A[*i];
            incmove(s,1);
            A[*i] = A[*j];
            incmove(s,1);
            A[*j] = w;
            (*i)++; 
            (*j)--;
        }
    inccmp(s,1);
    } while (*i <= *j);
}

void Ordena(int l, int r, int * A, sortperf_t *s)
{
    int i, j;
    partition(A, l, r, &i, &j, s);
    if (l < j) Ordena(l, j, A, s);
    if (i < r) Ordena(i, r, A, s);
}
// standard quicksort
void quickSort(int * A, int l, int r, sortperf_t *s) 
{
    Ordena(l, r, A, s);
}

// quicksort with median of 3
void Ordena3(int l, int r, int * A, sortperf_t *s)
{
    int i, j;
    partition3(A, l, r, &i, &j, s);
    if (l < j) Ordena(l, j, A, s);
    if (i < r) Ordena(i, r, A, s);
}
void quickSort3(int * A, int l, int r, sortperf_t *s) 
{
    Ordena3(l, r, A, s);
}

// quicksort with insertion for small partitions
void OrdenaIns(int l, int r, int * A, sortperf_t *s)
{
    int i, j;
    partition(A, l, r, &i, &j, s);
    if (l < j)
    {
        if(l-j > 50)// r é o tamanho - 1
        {
            OrdenaIns(l, j, A, s);
        }else
        {
            insertionSort(A, l, j, s);
        }
    }
    if (i < r)
    {
        if(r-i > 50)// r é o tamanho - 1
        {
            OrdenaIns(i, r, A, s);
        }else
        {
            insertionSort(A, i, r, s);
        }
    }
}
void quickSortIns(int * A, int l, int r, sortperf_t *s) 
{
    OrdenaIns(l, r, A, s);
}

// quicksort with insertion for small partitions and median of 3
void Ordena3Ins(int l, int r, int * A, sortperf_t *s)
{
    int i, j;
    partition3(A, l, r, &i, &j, s);
    if (l < j)
    {
        if(l-j > 50)// r é o tamanho - 1
        {
            Ordena3Ins(l, j, A, s);
        }else
        {
            insertionSort(A, l, j, s);
        }
    }
    if (i < r)
    {
        if(r-i > 50)// r é o tamanho - 1
        {
            Ordena3Ins(i, r, A, s);
        }else
        {
            insertionSort(A, i, r, s);
        }
    }
}

void quickSort3Ins(int * A, int l, int r, sortperf_t *s) 
{
    Ordena3Ins(l, r, A, s);
} 
void parse_args(int argc, char ** argv, opt_t * opt)
// Descricao: le as opcoes da linha de comando e inicializa variaveis
// Entrada: argc, argv, opt
// Saida: opt
{
     // variaveis externas do getopt
    extern char * optarg;
    extern int optind;

     // variavel auxiliar
    int c;

     // inicializacao variaveis globais para opcoes
    opt->seed = 1;
    opt->size = 10;
    opt->alg = 1;

     // getopt - letra indica a opcao, : junto a letra indica parametro
     // no caso de escolher mais de uma operacao, vale a ultima
    while ((c = getopt(argc, argv, "z:s:a:h")) != EOF)
    {
        switch(c)
        {
            case 'z':
                opt->size = atoi(optarg);
                break;
            case 's':
                opt->seed = atoi(optarg);
                break;
            case 'a':
                opt->alg = name2num(optarg);
                break;
            case 'h':
            default:
                uso();
                exit(1);
        }
    }
    if (!opt->alg)
    {
        uso();
        exit(1);
    }
}

void clkDiff(struct timespec t1, struct timespec t2, struct timespec * res)
// Descricao: calcula a diferenca entre t2 e t1, que e armazenada em res
// Entrada: t1, t2
// Saida: res
{
    if (t2.tv_nsec < t1.tv_nsec){
        // ajuste necessario, utilizando um segundo de tv_sec
        res-> tv_nsec = 1000000000+t2.tv_nsec-t1.tv_nsec;
        res-> tv_sec = t2.tv_sec-t1.tv_sec-1;
    } else {
        // nao e necessario ajuste
        res-> tv_nsec = t2.tv_nsec-t1.tv_nsec;
        res-> tv_sec = t2.tv_sec-t1.tv_sec;
    }
}