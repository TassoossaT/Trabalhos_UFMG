#ifndef DATA_H
#define DATA_H

typedef struct {
    int id;
    double x, y;
} Node;

typedef struct {
    Node* node;
    int n_node;
    char edge_weight_type[6];
} Data;

typedef struct {
    int n_node;
    int** matrix;
} Matrix;

int EUC_2D(int, int, Node *);
int ATT(int, int, Node *);
void read_data(const char *, Data *);
Matrix make_dist_matrix(const char *);
void print_distance_matrix(Matrix);
void free_distance_matrix(Matrix);
char** read_filenames(const char *, int *);
void free_filenames(char **, int );


#endif // DATA_H
