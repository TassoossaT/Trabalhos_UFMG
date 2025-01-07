#ifndef STRUCT_HPP
#define STRUCT_HPP

#include "pacient.hpp"
#include "Statistics.hpp"

class MinHeap
{
private:
    Pacient** heap;
    int capacity;
    int size;
    void heapifyUp(int);
    void heapifyDown(int);
    void resize();
    void swap(Pacient*&, Pacient*&);

public:
    MinHeap();
    ~MinHeap();
    void insert(Pacient*);
    Pacient* getMin();
    bool isEmpty() const;
};

class Queue
{
private:
    MinHeap red, yellow, green;
    Statistics stats;

public:
    Queue();
    void insert(int grauUrgencia, Pacient* paciente);
    Pacient* getMin();
    bool isEmpty() const;
    double getAverageWaitingTime() const;
    double getAverageServiceTime() const;
};

template <typename T>
class SequentialList 
{
private:
    T* elements;    ///< Pointer to the array of elements
    int* indices;   ///< Pointer to the array of indices
    int size;       ///< Current size of the list
    int capacity;   ///< Maximum capacity of the list
    int id;         ///< ID for memory tracking

public:

    SequentialList(int n);
    ~SequentialList();
    void insert(const T& value);
    T& operator[](int index);

};
#endif // STRUCT_HPP