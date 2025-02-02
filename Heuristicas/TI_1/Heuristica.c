#include "./Heuristica.h"

#include <stdbool.h>
#include <limits.h>
#include <glpk.h>
#include <stdio.h>
#include <time.h>
#include <stdlib.h>
#include <string.h>

int find_nearest_neighbor(Matrix distance_matrix)
{
    // Save the visited nodes and total cost to a file
    // FILE *file = fopen("Heuristica.txt", "w");
    // if (file == NULL)
    // {
    //     perror("Error opening file");
    //     return;
    // }
    // time_t start_time;
    // time(&start_time);
    bool *visited = malloc(distance_matrix.n_node * sizeof(bool));
    for (int i = 0; i < distance_matrix.n_node; i++) 
    {
        visited[i] = false;
    }

    int current_node = 0;
    visited[current_node] = true;
    // printf("Starting at node %d\n", current_node + 1);
    int total_distance = 0;

    for (int step = 0; step < distance_matrix.n_node - 1; step++) 
    {
        int nearest_node = -1;
        int min_distance = INT_MAX;

        for (int i = 0; i < distance_matrix.n_node; i++)
        {
            if (!visited[i] && i != current_node && distance_matrix.matrix[current_node][i] < min_distance)
            {
                min_distance = distance_matrix.matrix[current_node][i];
                nearest_node = i;
            }
        }

        if (nearest_node != -1)
        {
            visited[nearest_node] = true;
        //     printf("Step %d\t: Moving from node %d\t to node %d\t with distance %d\t\n", step + 1, current_node + 1, nearest_node + 1, min_distance);
        //     fprintf(file,"Step %d\t: Moving from node %d\t to node %d\t with distance %d\t\n", step + 1, current_node + 1, nearest_node + 1, min_distance); // Example elapsed time
            current_node = nearest_node;
        }
        total_distance += min_distance;
    }
    // time_t end_time;
    // time(&end_time);
    // // Return to the starting node
    // double elapsed_time = difftime(end_time, start_time);
    // int x = distance_matrix.matrix[current_node][start_node];
    // total_distance += x;
    // printf("Step %d\t: Moving from node %d\t to node %d\t with distance %d\t\n", distance_matrix.n_node, current_node + 1, start_node + 1, x);
    // fprintf(file,"Step %d\t: Moving from node %d\t to node %d\t with distance %d\t\n", distance_matrix.n_node, current_node + 1, start_node + 1, x); // Example elapsed time
    // printf( "Total cost: %d\n", total_distance);
    // fprintf(file, "Total cost: %d\n", total_distance);
    // printf("Elapsed time: %.2f seconds\n", elapsed_time);
    // fprintf(file, "Elapsed time: %.2f seconds\n", elapsed_time); // Example elapsed time
    // fclose(file);
    free(visited);
    return total_distance;
}


int main() 
{
    int count;
    char **filenames = read_filenames("dat.dat", &count);
    if (filenames == NULL) {
        return 1;
    }

    FILE *result_file = fopen("Heur_data.txt", "w");
    if (result_file == NULL) {
        perror("Error opening Heur_data");
        free_filenames(filenames, count);
        return 1;
    }

    for (int i = 0; i < count; i++) {
        printf("Processing file: %s\n", filenames[i]);
        Matrix m = make_dist_matrix(filenames[i]);

        time_t start_time;
        time(&start_time);

        int total_distance = find_nearest_neighbor(m);

        time_t end_time;
        time(&end_time);

        double elapsed_time = difftime(end_time, start_time);
        fprintf(result_file, "File: %s\nTotal distance: %d| Elapsed time: %.2fs\n", filenames[i], total_distance, elapsed_time);

        free_distance_matrix(m);
    }

    fclose(result_file);
    free_filenames(filenames, count);

    return 0;
}