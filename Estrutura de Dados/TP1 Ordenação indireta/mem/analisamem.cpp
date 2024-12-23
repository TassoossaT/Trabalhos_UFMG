//---------------------------------------------------------------------
// Arquivo      : analisamem.cpp
// Conteudo     : analise de localidade de referencia
// Autor        : Wagner Meira Jr. (meira@dcc.ufmg.br)
// Historico    : 2021-10-30 - arquivo criado
//              : 2021-11-08 - comentarios
//              : 2022-04-17 - adicionado distp e png
//---------------------------------------------------------------------

#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <cstring>
#include <climits>
#include <limits>
#include <cmath>
#include <getopt.h>
#include "../include/msgassert.h" 
#include "../include/estrutura_dados.hpp"

using namespace std;

// assumimos o que o tamanho da palavra de máquina é 64 bits (8 bytes)
// em uma versao posterior pode ser um parametro
#define TAMPALAVRA 8

// variaveis globais para a captura de opcoes de linha de comando
// poderia ser uma estrutura passada como parametro
char lognome[1000];
char prefixo[1000];
char formato[10];
char terminal[1000];

// estrutura do arquivo gnuplot para grafico de acesso
const char* gpacesso[] = {
    "set term %s",
    "set output \"%s-acesso-%d.%s\"",
    "set title \"Grafico de acesso - ID %d\"",
    "set xlabel \"Acesso\"",
    "set ylabel \"Endereco\"",
    "plot \"%s-acesso-0-%d.gpdat\" u 2:4 w points t \"L\" lw 3, \"%s-acesso-1-%d.gpdat\" u 2:4 w points t \"E\" lw 3", 
    nullptr
};

// estrutura do arquivo gnuplot para histograma de distancia de pilha 
const char* gphist[] = {
    "set term %s",
    "set output \"%s-hist-%d-%d.%s\"",
    "set style fill solid 1.0",
    "set title \"Distancia de Pilha (Total %ld # %d Media %.2f) - Fase  %d - ID %d\"",
    "set xlabel \"Distancia\"",
    "set ylabel \"Frequencia\"",
    "plot [%d:%d] \"%s-hist-%d-%d.gpdat\" u 3:4 w boxes t \"\"", 
    nullptr
};

const char* gpdistp[] = {
    "set term %s",
    "set output \"%s-distp-%d.%s\"",
    "set title \"Evolucao Distancia de Pilha - ID %d\"",
    "set xlabel \"Acesso\"",
    "set ylabel \"Distancia de Pilha\"",
    "plot \"%s-acesso-2-%d.gpdat\" u 2:5 w impulses t \"\"", 
    nullptr
};

void uso() {
    // Descricao: imprime as instrucoes de uso do programa
    // Entrada:  N/A
    // Saida: instrucoes
    cerr << "analyzemem\n";
    cerr << "\t-i <arq> \t(arquivo de log) \n";
    cerr << "\t-p <arq>\t(prefixo de saida)\n";
    cerr << "\t-f <fmt>\t(formato graficos: eps/png)\n";
}

void parse_args(int argc, char** argv)
{
    // Descricao: analisa a linha de comando a inicializa variaveis
    // Entrada: argc e argv
    // Saida: lognome e prefixo (globais)
    int c;
    lognome[0] = 0;
    prefixo[0] = 0;
    strcpy(formato, "png");
    strcpy(terminal, "png");

    // percorre a linha de comando buscando identificadores
    while ((c = getopt(argc, argv, "i:p:f:h")) != -1) {
        switch (c) {
            case 'i':
                // log de entrada
                strcpy(lognome, optarg);
                break;
            case 'p':
                // prefixo dos arquivos de saida
                strcpy(prefixo, optarg);
                break;
            case 'f':
                // formato de saida dos graficos
                cout << 'f'<<endl;
                strcpy(formato, optarg);
                if (!strcasecmp(formato, "png"))
                {
                    strcpy(terminal, "png");
                    cout << terminal << endl;
                } else if (!strcasecmp(formato, "eps"))
                {
                    strcpy(terminal, "postscript eps color 14");
                    cout << terminal << endl;
                } else 
                {
                    // formato desconhecido, gerar erro 
                    cout << "Formato Desconhecido"<<endl;
                    formato[0] = 0;
                }
                break;
            case 'h':
            default:
                uso();
                exit(1);
        }
    }
    erroAssert(lognome[0], "Arquivo de log nao definido.");
    erroAssert(prefixo[0], "Prefixo de saida nao definido.");
}

int lelinha(ifstream& in, string& line) {
    // Descricao: le uma linha do arquivo in
    // Entrada: in
    // Saida: line
    if (getline(in, line)) {
        return line.length();
    }
    return 0;
}

int quebralinha(const string& line, vector<string>& tkvet) {
    // Descricao: divide a linha em tokens separados por espaço
    // Entrada: line
    // Saida: tkvet
    istringstream iss(line);
    string token;
    tkvet.clear();
    while (iss >> token) {
        tkvet.push_back(token);
    }
    return tkvet.size();
}

int main(int argc, char** argv) {
    // Descricao: 
    // Entrada: 
    // Saida: 

    ifstream log;
    string linha;
    vector<string> tkvet;
    char tipo;
    vector<vector<ofstream>> out;
    char outnome[2000];
    int auxtipo;
    int auxcont;
    vector<vector<int>> controle;
    vector<vector<int>> liminf;
    vector<vector<int>> limsup;

    // declara e inicializa as variaveis de controle 
    long int minend = LONG_MAX;
    long int maxend = -1;
    long int auxend;
    long int numend;

    int minfase = INT_MAX;
    int maxfase = -1;
    int auxfase;
    int numfase;

    int minid = INT_MAX;
    int maxid = -1;
    int auxid;
    int numid;

    int auxdp, i, j, k, numcampos;
    int retprint;

    char aux[1000];
    // analisa a linha de comando
    parse_args(argc, argv);

    SequentialList<DataRow> list(1000); // Example initialization, adjust as needed

    // le arquivo de log, determinando o limite superior e inferior de end
    // determina o número de fases e de identificadores de variaveis
    log.open(lognome);
    erroAssert(log.is_open(), "Erro no fopen");
    while (lelinha(log, linha)) {
        numcampos = quebralinha(linha, tkvet);
        // I, L , E ou F
        tipo = tkvet[0][0];
        switch (tipo) {
            case 'I':
                erroAssert(numcampos == 3, "Numero de campos errado");
                // nao usamos essa informacao no momento
                break;
            case 'L':
            case 'E':
                // caso seja L ou E, verifica e atualiza os limites
                erroAssert(numcampos == 7, "Numero de campos errado");
                auxend = stol(tkvet[5]);
                if (auxend > maxend) maxend = auxend;
                if (auxend < minend) minend = auxend;
                auxfase = stoi(tkvet[1]);
                if (auxfase > maxfase) maxfase = auxfase;
                if (auxfase < minfase) minfase = auxfase;
                auxid = stoi(tkvet[3]);
                if (auxid > maxid) maxid = auxid;
                if (auxid < minid) minid = auxid;
                break;
            case 'F':
                erroAssert(numcampos == 4, "Numero de campos errado");
                // nao usamos essa informacao no momento
                break;
        }
    }
    log.close();

    // verifica se minfase e minid sao 0
    erroAssert(minid == 0, "Id minimo nao e zero");
    erroAssert(minfase == 0, "Fase minima nao e zero");

    // calcula as dimensoes a serem utilizadas na analise
    numend = ((maxend - minend) / TAMPALAVRA) + 2;
    numfase = (maxfase - minfase) + 1;
    numid = (maxid - minid) + 1;

    // apenas para conferencia
    cerr << "Enderecos:  [" << minend << "-" << maxend << "] (" << maxend - minend << ") #end " << numend << endl;
    cerr << "Fases: [" << minfase << "-" << maxfase << "] (" << maxfase - minfase << ") #fase " << numfase << endl;
    cerr << "Ids: [" << minid << "-" << maxid << "] #id " << numid << endl;

    // le arquivo de log
    // ajusta enderecos
    // imprime arquivos para mapa de acessos

    // cria arquivos de saida
    // 3(escrita, leitura, historico)*numid arquivos
    // leitura = 0 e escrita = 1 
    out.resize(3);
    for (i = 0; i < 3; i++) {
        out[i].resize(numid);
        for (j = 0; j < numid; j++) {
            retprint = sprintf(outnome, "%s-acesso-%d-%d.gpdat", prefixo, i, j);
            erroAssert(retprint >= 0, "Erro no sprintf");
            out[i][j].open(outnome);
            erroAssert(out[i][j].is_open(), "Erro no fopen");
        }
    }

    vector<vector<vector<long>>> dpvet(numfase, vector<vector<long>>(numid, vector<long>(numend, 0)));

    // le novamente o arquivo de log e analisa e registra os acessos
    log.open(lognome);
    erroAssert(log.is_open(), "Erro no fopen");
    while (lelinha(log, linha)) {
        quebralinha(linha, tkvet);
        tipo = tkvet[0][0];
        switch (tipo) {
            case 'I':
                break;
            case 'L':
            case 'E':
                // qual a fase?
                auxfase = stoi(tkvet[1]);
                // qual o contador de evento?
                auxcont = stoi(tkvet[2]);
                // qual o identificador de variavel?
                auxid = stoi(tkvet[3]);
                // qual o endereco?
                // escalar para a faixa 0-maxend, considerando TAMPALAVRA
                auxend = (stol(tkvet[5]) - minend) / TAMPALAVRA;
                // registro de distancia de pilha
                auxdp = 0; // Placeholder for distance calculation logic
                dpvet[auxfase][auxid][auxdp]++;
                // L - auxtipo=0 / E - auxtipo=1
                auxtipo = (tipo == 'E');
                // escreve no arquivo acessos por tipo e id
                out[auxtipo][auxid] << auxfase << " " << auxcont << " " << auxid << " " << auxend << endl;
                out[2][auxid] << auxfase << " " << auxcont << " " << auxid << " " << auxend << " " << auxdp << endl;
                break;
            case 'F':
                break;
        }
    }
    log.close();

    for (i = 0; i < 3; i++) {
        for (j = 0; j < numid; j++) {
            out[i][j].close();
        }
    }

    // geracao de arquivos gnuplot para acessos
    // na verdade nao e necessario usar a matriz de arquivos de saida
    // feito assim por comodidade
    out.resize(1);
    for (i = 0; i < 1; i++) {
        out[i].resize(numid);
        for (j = 0; j < numid; j++)
        {
            retprint = sprintf(outnome, "%s-acesso-%d.gp", prefixo, j);
            erroAssert(retprint >= 0, "Erro no sprintf");
            out[i][j].open(outnome);
            erroAssert(out[i][j].is_open(), "Erro no fopen");
            k = 0;
            while (gpacesso[k]) {
                switch (k)
                {
                    case 0:
                        retprint = sprintf(aux,gpacesso[k],terminal);
                        erroAssert(retprint>=0,"Erro no sprintf");
                        out[i][j] << aux << endl;
                        erroAssert(out[i][j].is_open(), "Erro no fopen");
                        break;
                    case 1:
                        // nome do arquivo de saida
                        retprint = sprintf(aux,gpacesso[k],prefixo,j,formato);
                        erroAssert(retprint>=0,"Erro no sprintf");
                        out[i][j] << aux << endl;
                        erroAssert(out[i][j].is_open(), "Erro no fopen");
                        break;
                    case 2:
                        // titulo do grafico
                        retprint = sprintf(aux,gpacesso[k],prefixo,j,formato);
                        erroAssert(retprint>=0,"Erro no sprintf");
                        out[i][j] << aux << endl;
                        erroAssert(out[i][j].is_open(), "Erro no fopen");;
                        break;
                    case 3:
                    case 4:
                        // linhas que nao tem parametro
                        retprint = sprintf(aux,gpacesso[k]);
                        erroAssert(retprint>=0,"Erro no sprintf");
                        out[i][j] << aux << endl;
                        erroAssert(out[i][j].is_open(), "Erro no fopen");
                        break;
                    case 5:
                        // geracao do grafico
                        retprint = sprintf(aux,gpacesso[k],prefixo,j,prefixo,j);
                        erroAssert(retprint>=0,"Erro no sprintf");
                        out[i][j] << aux << endl;
                        erroAssert(out[i][j].is_open(), "Erro no fopen");
                        break;
                }
                out[i][j] << endl;
                k++;
            }
            out[i][j].close();
        }
    }

    // geracao de arquivos gnuplot para distancias de pilha
    // na verdade nao e necessario usar a matriz de arquivos de saida
    // feito assim por comodidade
    out.resize(1);
    for (i = 0; i < 1; i++) {
        out[i].resize(numid);
        for (j = 0; j < numid; j++) {
            retprint = sprintf(outnome, "%s-distp-%d.gp", prefixo, j);
            erroAssert(retprint >= 0, "Erro no sprintf");
            out[i][j].open(outnome);
            erroAssert(out[i][j].is_open(), "Erro no fopen");
            k = 0;
            while (gpdistp[k]) {
                switch (k) {
                    case 0:
                        retprint = sprintf(aux,gpdistp[k],terminal);
                        erroAssert(retprint>=0,"Erro no sprintf");
                        out[i][j] << aux << endl;
                        erroAssert(out[i][j].is_open(), "Erro no fopen");
                        break;
                    case 1:
                        // nome do arquivo de saida
                        retprint = sprintf(aux,gpdistp[k],prefixo,j,formato);
                        erroAssert(retprint>=0,"Erro no sprintf");
                        out[i][j] << aux << endl;
                        erroAssert(out[i][j].is_open(), "Erro no fopen");
                        break;
                    case 2:
                        // titulo do grafico
                        retprint = sprintf(aux,gpdistp[k],j);
                        erroAssert(retprint>=0,"Erro no sprintf");
                        out[i][j] << aux << endl;
                        erroAssert(out[i][j].is_open(), "Erro no fopen");
                        break;
                    case 3:
                    case 4:
                        // linhas que nao tem parametro
                        retprint = sprintf(aux,gpdistp[k]);
                        erroAssert(retprint>=0,"Erro no sprintf");
                        out[i][j] << aux << endl;
                        erroAssert(out[i][j].is_open(), "Erro no fopen");
                        break;
                    case 5:
                        // geracao do grafico
                        retprint = sprintf(aux,gpdistp[k],prefixo,j);
                        erroAssert(retprint>=0,"Erro no sprintf");
                        out[i][j] << aux << endl;
                        erroAssert(out[i][j].is_open(), "Erro no fopen");
                        break;
                }
                out[i][j] << endl;
                k++;
            }
            out[i][j].close();
        }
    }

    // impressao dos contadores de distancia de pilha para depuracao 
    for (i = 0; i < numfase; i++) {
        for (j = 0; j < numid; j++) {
            for (k = 0; k < numend; k++) {
                if (dpvet[i][j][k]) {
                    cerr << i << " " << j << " " << k << " " << dpvet[i][j][k] << endl;
                }
            }
        }
    }

    // criacao dos arquivos e estruturas de controle para histogramas
    controle.resize(numfase, vector<int>(numid, 0));
    liminf.resize(numfase, vector<int>(numid, INT_MAX));
    limsup.resize(numfase, vector<int>(numid, -1));
    out.resize(numfase);
    for (i = 0; i < numfase; i++) {
        out[i].resize(numid);
        for (j = 0; j < numid; j++) {
            retprint = sprintf(outnome, "%s-hist-%d-%d.gpdat", prefixo, i, j);
            erroAssert(retprint >= 0, "Erro no sprintf");
            out[i][j].open(outnome);
            erroAssert(out[i][j].is_open(), "Erro no fopen");
        }
    }

    // identificacao de limites do histograma e geracao de arquivos de dados
    for (i = 0; i < numfase; i++) {
        for (j = 0; j < numid; j++) {
            // delimitar limite inferior e superior de cada histograma
            for (k = 0; k < numend; k++) {
                if (dpvet[i][j][k]) {
                    if (liminf[i][j] > k) liminf[i][j] = k;
                    if (limsup[i][j] < k) limsup[i][j] = k;
                }
            }
            for (k = liminf[i][j]; k <= limsup[i][j]; k++) {
                out[i][j] << i << " " << j << " " << k << " " << dpvet[i][j][k] << endl;
                controle[i][j]++;
            }
        }
    }

    // fechar os arquivos
    for (i = 0; i < numfase; i++) {
        for (j = 0; j < numid; j++) {
            out[i][j].close();
        }
    }

    // geracao de arquivos gnuplot dos histogramas
    out.resize(numfase);
    for (i = 0; i < numfase; i++) {
        out[i].resize(numid);
        for (j = 0; j < numid; j++) {
            // verifica se ha dados para gerar os histogramas
            if (controle[i][j]) {
                long somadp = 0;
                int countnonzero = 0;
                for (k = 0; k < numend; k++) {
                    somadp += dpvet[i][j][k] * k;
                    if (dpvet[i][j][k]) countnonzero += dpvet[i][j][k];
                }
                retprint = sprintf(outnome, "%s-hist-%d-%d.gp", prefixo, i, j);
                erroAssert(retprint >= 0, "Erro no sprintf");
                out[i][j].open(outnome);
                erroAssert(out[i][j].is_open(), "Erro no fopen");
                k = 0;
                while (gphist[k]) {
                    switch (k) {
                        case 0:
                            retprint = sprintf(aux,gphist[k],terminal);
                            erroAssert(retprint>=0,"Erro no sprintf");
                            out[i][j] << aux << endl;
                            erroAssert(out[i][j].is_open(), "Erro no fopen");
                            break;
                        case 1:
                            // arquivo de saida
                            retprint = sprintf(aux,gphist[k],prefixo,i,j,formato);
                            erroAssert(retprint>=0,"Erro no sprintf");
                            out[i][j] << aux << endl;
                            erroAssert(out[i][j].is_open(), "Erro no fopen");
                            break;
                        case 2:
                        case 3:
                            // titulo
                            retprint = sprintf(aux,gphist[k],somadp,countnonzero,(somadp * 1.0) / countnonzero,i,j);
                            erroAssert(retprint>=0,"Erro no sprintf");
                            out[i][j] << aux << endl;
                            erroAssert(out[i][j].is_open(), "Erro no fopen");
                            break;
                        case 4:
                        case 5:
                            // imprimir as linhas
                            retprint = sprintf(aux,gphist[k]);
                            erroAssert(retprint>=0,"Erro no sprintf");
                            out[i][j] << aux << endl;
                            erroAssert(out[i][j].is_open(), "Erro no fopen");
                            break;
                        case 6:
                            // gera grafico
                            retprint = sprintf(aux,gphist[k],liminf[i][j] - 1,limsup[i][j] + 1,prefixo, i, j );
                            erroAssert(retprint>=0,"Erro no sprintf");
                            out[i][j] << aux << endl;
                            erroAssert(out[i][j].is_open(), "Erro no fopen");
                            // out[i][j] << gphist[k] << liminf[i][j] - 1 << limsup[i][j] + 1 << prefixo << i << j << endl;
                            break;

                    }
                    out[i][j] << endl;
                    k++;
                }
                out[i][j].close();
            }
        }
    }

    // desaloca as estruturas de controle
    // for (i = 0; i < numfase; i++) {
    //     free(out[i]);
    //     free(controle[i]);
    //     free(liminf[i]);
    //     free(limsup[i]);
    // }
    // free(out);
    // free(controle);
    // free(liminf);
    // free(limsup);

    // desaloca as varias estruturas de dados auxiliares
    // for (i = 0; i < numfase; i++) {
    //     for (j = 0; j < numid; j++) {
    //         // destroipilhaidx(&(p[i][j]));
    //         free(dpvet[i][j]);
    //     }
    //     // free(p[i]);
    //     free(dpvet[i]);
    // }
    // // free(p);
    // free(dpvet);

    return 0;
}

