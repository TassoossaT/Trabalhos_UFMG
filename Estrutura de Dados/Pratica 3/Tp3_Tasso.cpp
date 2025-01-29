#include <iostream>
#include <chrono>
#include <cmath>
#include <cstring>
#include <string>
#include <fstream>

using namespace std;
using namespace std::chrono;

// Recursive factorial function
unsigned long long factorial_recursive(int n) {
    if (n <= 1) return 1;
    return n * factorial_recursive(n - 1);
}

// Iterative factorial function
unsigned long long factorial_iterative(int n) {
    unsigned long long result = 1;
    for (int i = 1; i <= n; ++i) {
        result *= i;
    }
    return result;
}

// Recursive Fibonacci function
unsigned long long fibonacci_recursive(int n) {
    if (n <= 1) return n;
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2);
}

// Iterative Fibonacci function
unsigned long long fibonacci_iterative(int n) {
    if (n <= 1) return n;
    unsigned long long a = 0, b = 1, c;
    for (int i = 2; i <= n; ++i) {
        c = a + b;
        a = b;
        b = c;
    }
    return b;
}

// Function to consume computational resources
void consume_resources() {
    for (int i = 0; i < 1000000; ++i) {
        sin(i);
    }
}

int main() {
    ofstream outfile("resultados.txt");
    auto s = high_resolution_clock::now();
    consume_resources();
    auto e = high_resolution_clock::now();
    auto consume_resources = duration_cast<microseconds>(e- s).count();
    outfile << "consume_resources: " << consume_resources << endl;

    if (!outfile.is_open()) {
        cerr << "Erro ao abrir o arquivo para escrita" << endl;
        return 1;
    }
    outfile << "Time factorial" << endl;
    for (int i = 0; i < 1000; i+=100) {
        auto start = high_resolution_clock::now();
        factorial_recursive(i);
        auto end = high_resolution_clock::now();
        auto recursive = duration_cast<microseconds>(end - start).count();
        
        auto _start = high_resolution_clock::now();
        factorial_iterative(i);
        auto _end = high_resolution_clock::now();
        auto iterative = duration_cast<microseconds>(_end - _start).count();
        
        outfile << i << " Recursive: " << recursive << " Iterative: " << iterative << endl;
    }
    
    outfile << "Time fibonacci" << endl;
    for (int i = 1; i < 100; i+=2) {
        auto start = high_resolution_clock::now();
        fibonacci_recursive(i);
        auto end = high_resolution_clock::now();
        auto recursive = duration_cast<microseconds>(end - start).count();
        
        auto _start = high_resolution_clock::now();
        fibonacci_iterative(i);
        auto _end = high_resolution_clock::now();
        auto iterative = duration_cast<microseconds>(_end - _start).count();
        
        outfile << i << " Recursive: " << recursive << " Iterative: " << iterative << endl;
    }


    outfile.close();
    return 0;
}