#include "DataStruct.hpp"
#include "pacient.hpp"
#include "Statistics.hpp"
#include <stdexcept>


template class SequentialList<Pacient>;

MinHeap::MinHeap() : capacity(1), size(0) {heap = new Pacient*[capacity];}
MinHeap::~MinHeap() {delete[] heap;}

void MinHeap::swap(Pacient*& a, Pacient*& b)
{
    Pacient* temp = a;
    a = b;
    b = temp;
}

void MinHeap::heapifyUp(int index)
{
    while (index > 0 && heap[index]->getAdmissionDate() < heap[(index - 1) / 2]->getAdmissionDate())
    {
        swap(heap[index], heap[(index - 1) / 2]);
        index = (index - 1) / 2;
    }
}

void MinHeap::heapifyDown(int index)
{
    int small = index;
    int left = 2 * index + 1;
    int right = 2 * index + 2;

    if (left < size && heap[left]->getAdmissionDate() < heap[small]->getAdmissionDate()){small = left;}
    if (right < size && heap[right]->getAdmissionDate() < heap[small]->getAdmissionDate()){small = right;}
    if (small != index)
    {
        swap(heap[index], heap[small]);
        heapifyDown(small);
    }
}

void MinHeap::resize()
{
    capacity *= 2;
    Pacient** newHeap = new Pacient*[capacity];
    for (int i = 0; i < size; i++)
    {
        newHeap[i] = heap[i];
    }
    delete[] heap;
    heap = newHeap;
}

void MinHeap::insert(Pacient* element)
{
    if (size == capacity)
    {
        resize();
    }
    heap[size] = element;
    heapifyUp(size);
    size++;
}

Pacient* MinHeap::getMin()
{
    if (size == 0)
    {
        throw std::runtime_error("Heap is empty");
    }
    Pacient* minElement = heap[0];
    heap[0] = heap[size - 1];
    size--;
    heapifyDown(0);
    return minElement;
}

bool MinHeap::isEmpty() const{return size == 0;}

// Queue implementation
Queue::Queue() : red(), yellow(), green(), stats() {}

void Queue::insert(Pacient* paciente)
{
    switch (pacient.grauUrgencia)
    {
        case 2:
            red.insert(pacient);
            break;
        case 1:
            yellow.insert(paciente);
            break;
        case 0:
            green.insert(paciente);
            break;
        default:
            throw std::invalid_argument("Invalid urgency level");
    }
}

Pacient* Queue::getMin()
{
    Pacient* paciente = nullptr;
    if (!red.isEmpty())
    {
        paciente = red.getMin();
    }
    else if (!yellow.isEmpty())
    {
        paciente = yellow.getMin();
    }
    else if (!green.isEmpty())
    {
        paciente = green.getMin();
    }
    else
    {
        throw std::runtime_error("All queues are empty");
    }

    if (paciente)
    {
        stats.addWaitingTime(paciente->getWaitingTime());
        stats.addServiceTime(paciente->getServiceTime());
    }

    return paciente;
}

bool Queue::isEmpty() const
{
    return red.isEmpty() && yellow.isEmpty() && green.isEmpty();
}

double Queue::getAverageWaitingTime() const
{
    return stats.getAverageWaitingTime();
}

double Queue::getAverageServiceTime() const
{
    return stats.getAverageServiceTime();
}

// Constructor for SequentialList
template <typename T>
SequentialList<T>::SequentialList(int n) : elements(nullptr), indices(nullptr), size(0), capacity(n)
{
    erroAssert_cond(n > 0, "Capacity must be greater than 0");
    try
    {
        elements = new T[n];
        indices = new int[n];
    } catch (const std::bad_alloc& e)
    {
        std::cerr << "n :" << n << std::endl; // Debug print
        std::cerr << "Memory allocation failed: " << e.what() << std::endl;
        throw;
    }
}

// Destructor for SequentialList
template <typename T>
SequentialList<T>::~SequentialList()
{
    delete[] elements;
    delete[] indices;
}
template <typename T>
void SequentialList<T>::insert(const T& value)
{
    indices[size] = size;
    elements[indices[size]] = value;
    size++;
}
template <typename T>
T& SequentialList<T>::operator[](int index)
{
    return elements[indices[index]];
}