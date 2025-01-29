#include "DataStruct.hpp"
#include "Patient.hpp"
#include "Procedure.hpp" // Include the full definition of Unit
#include <stdexcept>
#include <iostream>
#include <ostream>

// Explicit template instantiation
template class MinHeap<Patient, Date>;
template class MinHeap<Patient, int>;
template class MinHeap<Procedure::Unit, Date>; // Add this line

template <typename T, typename U>
MinHeap<T, U>::MinHeap(U (T::*sortParam)() const) : capacity(10), size(0), sortParam(sortParam) 
{
    heap = new T*[capacity];
}

template <typename T, typename U>
MinHeap<T, U>::~MinHeap() {delete[] heap;}

template <typename T, typename U>
void MinHeap<T, U>::insert(T* element) 
{
    if (size == capacity) {resize();}
    heap[size] = element;
    heapifyUp(size);
    size++;
}

template <typename T, typename U>
T* MinHeap<T, U>::extractMin() 
{
    if (isEmpty()) {return nullptr;}
    T* minElement = heap[0];
    heap[0] = heap[size - 1];
    size--;
    heapifyDown(0);
    return minElement;
}

template <typename T, typename U>
T* MinHeap<T, U>::viewMin() const 
{
    if (isEmpty()) {return nullptr;}
    return heap[0];
}

template <typename T, typename U>
bool MinHeap<T, U>::isEmpty() const {return size == 0;}

template <typename T, typename U>
int MinHeap<T, U>::getSize() const {return size;}

template <typename T, typename U>
void MinHeap<T, U>::heapifyUp(int index) 
{
    while (index > 0) 
    {
        int parentIndex = (index - 1) / 2;
        if ((heap[index]->*sortParam)() > (heap[parentIndex]->*sortParam)() || 
            ((heap[index]->*sortParam)() == (heap[parentIndex]->*sortParam)() && 
            heap[index]->getId() > heap[parentIndex]->getId()))
        {
            break;
        }
        swap(heap[index], heap[parentIndex]);
        index = parentIndex;
    }
}

template <typename T, typename U>
void MinHeap<T, U>::heapifyDown(int index) 
{
    while (2 * index + 1 < size) 
    {
        int leftChild = 2 * index + 1;
        int rightChild = 2 * index + 2;
        int smallest = leftChild;
        if (rightChild < size && 
            ((heap[rightChild]->*sortParam)() < (heap[leftChild]->*sortParam)() || 
            ((heap[rightChild]->*sortParam)() == (heap[leftChild]->*sortParam)() && heap[rightChild]->getId() < heap[leftChild]->getId())))
        {
            smallest = rightChild;
        }
        if ((heap[index]->*sortParam)() < (heap[smallest]->*sortParam)() || 
            ((heap[index]->*sortParam)() == (heap[smallest]->*sortParam)() && heap[index]->getId() <= heap[smallest]->getId()))
        {
            break;
        }
        swap(heap[index], heap[smallest]);
        index = smallest;
    }
}

template <typename T, typename U>
void MinHeap<T, U>::resize() {
    capacity *= 2;
    T** newHeap = new T*[capacity];
    for (int i = 0; i < size; ++i) {
        newHeap[i] = heap[i];
    }
    delete[] heap;
    heap = newHeap;
}

template <typename T, typename U>
void MinHeap<T, U>::swap(T*& a, T*& b) {
    T* temp = a;
    a = b;
    b = temp;
}

// Queue implementation
Queue::Queue() : red(&Patient::getInsertQueueDate), yellow(&Patient::getInsertQueueDate), green(&Patient::getInsertQueueDate){}

void Queue::insert(Patient* patient, Date QueueDate)
{
    patient->setInsertQueueDate(QueueDate);
    switch (patient->getUrgencyLevel())
    {
        case 2:
            red.insert(patient);
            break;
        case 1:
            yellow.insert(patient);
            break;
        case 0:
            green.insert(patient);
            break;
        default:
            throw std::invalid_argument("Invalid urgency level");
    }
}

Patient* Queue::extractMin()
{
    Patient* patient = nullptr;
    if (!red.isEmpty())
    {
        patient = red.extractMin();
    }
    else if (!yellow.isEmpty())
    {
        patient = yellow.extractMin();
    }
    else if (!green.isEmpty())
    {
        patient = green.extractMin();
    }
    else
    {
        throw std::runtime_error("All queues are empty");
    }
    return patient;
}

Patient* Queue::viewMin()
{
    if (!red.isEmpty())
    {
        return red.viewMin();
    }
    else if (!yellow.isEmpty())
    {
        return yellow.viewMin();
    }
    else if (!green.isEmpty())
    {
        return green.viewMin();
    }
    else
    {
        throw std::runtime_error("All queues are empty");
    }
}

bool Queue::isEmpty() const
{
    return red.isEmpty() && yellow.isEmpty() && green.isEmpty();
}

