#include "./data.h"

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

int EUC_2D(int i, int j, Node *node) {
    double xd = node[i].x - node[j].x;
    double yd = node[i].y - node[j].y;
    return (int)(sqrt(xd * xd + yd * yd));
}
int ATT(int i, int j, Node *node) {
    double xd = (node[i].x - node[j].x);
    double yd = (node[i].y - node[j].y);
    double rij = sqrt((xd * xd + yd * yd) / 10.0);
    int tij = (int)(rij);
    return (tij < rij) ? tij + 1 : tij;
}
void check_filename(const char *filename) {
    if (filename == NULL) {
        printf("Filename is NULL\n");
        return;
    }

    // Verifica se a string está corretamente terminada
    size_t len = strlen(filename);
    if (len == 0) {
        printf("Filename is an empty string\n");
        return;
    }

    // Remove espaços em branco no final da string
    while (len > 0 && (filename[len - 1] == ' ' || filename[len - 1] == '\n' || filename[len - 1] == '\r')) {
        len--;
    }

    char clean_filename[len + 1];
    strncpy(clean_filename, filename, len);
    clean_filename[len] = '\0';

    // Verifica se a condição é atendida
    if (strcmp(clean_filename, "att48.tsp") == 0) {
        printf("Condition met: filename is 'att48.tsp'\n");
    } else {
        printf("Condition not met: filename is '%s'\n", clean_filename);
    }
}
void read_data(const char *filename, Data *data) 
{
    if (filename == NULL) {
        printf("Filename is NULL\n");
        return;
    }

    // Verifica se a string está corretamente terminada
    size_t len = strlen(filename);
    if (len == 0) {
        printf("Filename is an empty string\n");
        return;
    }

    // Remove espaços em branco no final da string
    while (len > 0 && (filename[len - 1] == ' ' || filename[len - 1] == '\n' || filename[len - 1] == '\r')) {
        len--;
    }

    char clean_filename[len + 1];
    strncpy(clean_filename, filename, len);
    clean_filename[len] = '\0';

    FILE *file = fopen(clean_filename, "r");
    if (file == NULL) {
        perror("Error opening file");
        exit(EXIT_FAILURE);
    }
    char line[256];
    while (fgets(line, sizeof(line), file) != NULL && strncmp(line, "EOF", 3)) 
    {
        if (strncmp(line, "EDGE_WEIGHT_TYPE", 16) == 0) 
        {
            sscanf(line, "EDGE_WEIGHT_TYPE : %s", data->edge_weight_type);
        } 
        else if (strncmp(line, "DIMENSION", 9) == 0) 
        {
            sscanf(line, "DIMENSION : %d", &data->n_node);
            data->node = malloc(data->n_node * sizeof(Node));
            if (data->node == NULL) 
            {
                perror("Error allocating memory");
                fclose(file);
                exit(EXIT_FAILURE);
            }
        }
        else if (strncmp(line, "NODE_COORD_SECTION", 18) == 0) 
        {
            for (int i = 0; i < data->n_node; i++) 
            {
                fgets(line, sizeof(line), file);
                sscanf(line, "%d %lf %lf", &data->node[i].id, &data->node[i].x, &data->node[i].y);
            }
        }
    }
    fclose(file);
}
Matrix make_dist_matrix(const char *filename)
{
    Data *data = malloc(sizeof(Data));
    read_data(filename, data);
    Matrix distance_matrix;
    distance_matrix.n_node = data->n_node;
    distance_matrix.matrix = malloc(data->n_node * sizeof(int *));
    int (*dist_function)(int, int, Node*);
    dist_function = (strcmp(data->edge_weight_type, "EUC_2D")) ? ATT:EUC_2D;
    for (int i = 0; i < data->n_node; i++) 
    {
        distance_matrix.matrix[i] = malloc(data->n_node * sizeof(int));
        for (int j = 0; j < data->n_node; j++)
        {
            {
                distance_matrix.matrix[i][j] = dist_function(i, j, data->node);
            }
        }
    }
    // for (int i = 0; i < data->n_node; i++) {distance_matrix.matrix[i][i] = 10000;}
    free(data->node);
    free(data);
    return distance_matrix;
}


// void print_distance_matrix(Matrix distance_matrix) 
// {
//     printf("here\n");
//     for (int i = 0; i < distance_matrix.n_node; i++) {
//         for (int j = 0; j < distance_matrix.n_node; j++) {
//             printf("%d ", distance_matrix.matrix[i][j]);
//         }
//         printf("\n");
//     }
// }
void print_distance_matrix(Matrix distance_matrix) 
{
    printf("Distance Matrix:\n");
    printf("    ");
    for (int i = 0; i < distance_matrix.n_node; i++) {
        printf("%4d ", i + 1);
    }
    printf("\n");
    printf("   +");
    for (int i = 0; i < distance_matrix.n_node; i++) {
        printf("-----");
    }
    printf("\n");
    for (int i = 0; i < distance_matrix.n_node; i++) {
        printf("%2d |", i + 1);
        for (int j = 0; j < distance_matrix.n_node; j++) {
            printf("%4d ", distance_matrix.matrix[i][j]);
        }
        printf("\n");
    }
}
void free_distance_matrix(Matrix distance_matrix) {
    for (int i = 0; i < distance_matrix.n_node; i++) {
        free(distance_matrix.matrix[i]);
    }
    free(distance_matrix.matrix);
}

// int main()
// {
//     printf("Iniciando o programa...\n");
//     Matrix m = make_dist_matrix("att48.tsp");
//     printf("Matriz criada...\n");
//     print_distance_matrix(m);
//     printf("Matriz impressa...\n");
//     free_distance_matrix(m);
//     printf("Matriz liberada...\n");
//     printf("here\n");
//     return 0;
// }
char** read_filenames(const char *filename, int *count)
{
    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        perror("Error opening data");
        return NULL;
    }

    // Contar o número de linhas no arquivo
    char line[256];
    *count = 0;
    while (fgets(line, sizeof(line), file)) {
        (*count)++;
    }
    rewind(file);

    // Alocar memória para armazenar os nomes dos arquivos
    char **filenames = malloc(*count * sizeof(char *));
    for (int i = 0; i < *count; i++) {
        fgets(line, sizeof(line), file);
        line[strcspn(line, "\n")] = 0; // Remover o caractere de nova linha
        filenames[i] = malloc((strlen(line) + 1) * sizeof(char));
        if (filenames[i] == NULL) {
            perror("Error allocating memory");
            fclose(file);
            return NULL;
        }
        strcpy(filenames[i], line);
    }

    fclose(file);
    return filenames;
}

// Função para liberar a memória alocada para os nomes dos arquivos
void free_filenames(char **filenames, int count) {
    for (int i = 0; i < count; i++) {
        free(filenames[i]);
    }
    free(filenames);
}