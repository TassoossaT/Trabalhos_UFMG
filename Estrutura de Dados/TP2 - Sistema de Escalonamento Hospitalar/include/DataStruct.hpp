#ifndef STRUCT_HPP
#define STRUCT_HPP

#include "Patient.hpp"

template <typename T, typename U>
class MinHeap
{
private:
    T** heap;
    int capacity;
    int size;
    void heapifyUp(int);
    void heapifyDown(int);
    void resize();
    void swap(T*&, T*&);
    U (T::*sortParam)() const;

public:
    MinHeap(U (T::*sortParam)() const);
    ~MinHeap();
    void insert(T*);
    T* extractMin();
    T* viewMin() const;
    bool isEmpty() const;
    int getSize() const;
};

class Queue
{
private:
    MinHeap<Patient, Date> red, yellow, green;

public:
    Queue();
    void insert(Patient* patient, Date QueueDate);
    Patient* extractMin();
    Patient* viewMin();
    bool isEmpty() const;
};

class FIFO {
private:
    struct Node {
        Patient* patient;
        Node* next;
        Node(Patient* p) : patient(p), next(nullptr) {}
    };
    Node* front;
    Node* rear;
    int size;

public:
    FIFO();
    ~FIFO();
    void insert(Patient*);
    Patient* extractMin();
    Patient* viewMin() const;
    bool isEmpty() const;
    int getSize() const;
};

class PriorityQueue {
private:
    FIFO red, yellow, green;

public:
    PriorityQueue();
    void insert(Patient* patient, Date QueueDate);
    Patient* extractMin();
    Patient* viewMin();
    bool isEmpty() const;
};

#endif // STRUCT_HPP