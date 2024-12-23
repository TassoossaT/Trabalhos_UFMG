#ifndef MEMLOG
#define MEMLOG

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

typedef struct memlog
{
        FILE * log;
        // clock_t clk_id;// clockid_t clk_id;
        struct timespec inittime;
        long count;
        int fase;
        int ativo;
} memlog_tipo;
extern memlog_tipo ml;

// constantes definindo os estados de registro
#define MLATIVO 1
#define MLINATIVO 0

#define LEMEMLOG(pos,tam,id) \
        ((void)((ml.ativo==MLATIVO)?leMemLog(pos,tam,id):0))

#define ESCREVEMEMLOG(pos,tam,id) \
        ((void) ((ml.ativo==MLATIVO)?escreveMemLog(pos,tam,id):0))
int iniciaMemLog(char * nome);
int ativaMemLog();
int desativaMemLog();
int defineFaseMemLog(int f);
int leMemLog(long int pos, long int tam, int id);
int escreveMemLog(long int pos, long int tam, int id);
int finalizaMemLog();


#define erroAssert_cond(cond, msg) \
        do { \
                if (!(cond)) { \
                        fprintf(stderr, "Erro: %s\n", msg); \
                        fprintf(stderr, "Arquivo: %s\n", __FILE__); \
                        fprintf(stderr, "Linha: %d\n", __LINE__); \
                        exit(EXIT_FAILURE); \
                } \
        } while (0)
        
#endif // MEMLOG

