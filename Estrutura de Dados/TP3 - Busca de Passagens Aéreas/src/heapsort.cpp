#include <heapsort.hpp>
#include <flight.hpp>

template class HeapSort<Flight>;

template <typename T>
HeapSort<T>::HeapSort(SequentialList<T>* flightList, const std::string& sortCriteria) 
    : capacity(10), size(0), flightList(flightList), sortCriteria(sortCriteria) 
{
    heap = new int[capacity];
}

template <typename T>
HeapSort<T>::~HeapSort() 
{
    delete[] heap;
}

template <typename T>
void HeapSort<T>::insert(int index) 
{
    if (size == capacity) 
    {
        resize();
    }
    heap[size] = index;
    heapifyUp(size);
    size++;
}

template <typename T>
int HeapSort<T>::extractMin() 
{
    if (isEmpty()) 
    {
        return -1;
    }
    int minIndex = heap[0];
    heap[0] = heap[size - 1];
    size--;
    heapifyDown(0);
    return minIndex;
}

template <typename T>
int HeapSort<T>::viewMin() const 
{
    if (isEmpty()) 
    {
        return -1;
    }
    return heap[0];
}

template <typename T>
bool HeapSort<T>::isEmpty() const 
{
    return size == 0;
}

template <typename T>
int HeapSort<T>::getSize() const 
{
    return size;
}

template <typename T>
void HeapSort<T>::heapifyUp(int index) 
{
    while (index > 0) 
    {
        int parentIndex = (index - 1) / 2;
        if (compare(heap[parentIndex], heap[index])) 
        {
            break;
        }
        swap(heap[index], heap[parentIndex]);
        index = parentIndex;
    }
}

template <typename T>
void HeapSort<T>::heapifyDown(int index) 
{
    while (2 * index + 1 < size) 
    {
        int leftChild = 2 * index + 1;
        int rightChild = 2 * index + 2;
        int smallest = leftChild;
        if (rightChild < size && compare(heap[leftChild], heap[rightChild])) 
        {
            smallest = rightChild;
        }
        if (compare(heap[index], heap[smallest])) 
        {
            break;
        }
        swap(heap[index], heap[smallest]);
        index = smallest;
    }
}

template <typename T>
void HeapSort<T>::resize() 
{
    capacity *= 2;
    int* newHeap = new int[capacity];
    for (int i = 0; i < size; ++i) 
    {
        newHeap[i] = heap[i];
    }
    delete[] heap;
    heap = newHeap;
}

template <typename T>
void HeapSort<T>::swap(int& a, int& b) 
{
    int temp = a;
    a = b;
    b = temp;
}

template <typename T>
bool HeapSort<T>::compare(int a, int b) const 
{
    const T& flightA = (*flightList)[a];
    const T& flightB = (*flightList)[b];
    for (char criterion : sortCriteria) 
    {
        if (criterion == 'p') 
        {
            if (flightA.getPrice() != flightB.getPrice()) 
            {
                return flightA.getPrice() < flightB.getPrice();
            }
        } 
        else if (criterion == 'd') 
        {
            if (flightA.getDurationInSeconds() != flightB.getDurationInSeconds()) 
            {
                return flightA.getDurationInSeconds() < flightB.getDurationInSeconds();
            }
        } 
        else if (criterion == 's') 
        {
            if (flightA.getNumberOfStops() != flightB.getNumberOfStops()) 
            {
                return flightA.getNumberOfStops() < flightB.getNumberOfStops();
            }
        }
    }
    return false;
}