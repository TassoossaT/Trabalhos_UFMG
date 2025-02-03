#include <sort.hpp>
#include <flight.hpp>

// Instantiation for Flight
template class QuickSort<Flight>;

template <typename T>
QuickSort<T>::QuickSort(SequentialList<T>* flightList, const std::string& sortCriteria) 
    : capacity(10), size(0), flightList(flightList), sortCriteria(sortCriteria), sorted(false), currentIndex(0)
{
    arr = new int[capacity];
}

template <typename T>
QuickSort<T>::~QuickSort() 
{
    delete[] arr;
}

template <typename T>
void QuickSort<T>::insert(int index) 
{
    if (size == capacity) 
    {
        resize();
    }
    arr[size++] = index;
}

template <typename T>
void QuickSort<T>::resize() 
{
    capacity *= 2;
    int* newArr = new int[capacity];
    for (int i = 0; i < size; ++i) 
    {
        newArr[i] = arr[i];
    }
    delete[] arr;
    arr = newArr;
}

template <typename T>
void QuickSort<T>::quickSort(int low, int high) 
{
    if (low < high) 
    {
        int pivot = partition(low, high);
        quickSort(low, pivot - 1);
        quickSort(pivot + 1, high);
    }
}

template <typename T>
int QuickSort<T>::partition(int low, int high) 
{
    int pivotIndex = high;
    int i = low - 1;
    for (int j = low; j < high; ++j) 
    {
        if (compare(arr[j], arr[pivotIndex])) 
        {
            i++;
            swap(arr[i], arr[j]);
        }
    }
    swap(arr[i + 1], arr[high]);
    return i + 1;
}

template <typename T>
void QuickSort<T>::swap(int& a, int& b) 
{
    int temp = a;
    a = b;
    b = temp;
}

template <typename T>
bool QuickSort<T>::compare(int a, int b) const 
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

template <typename T>
int QuickSort<T>::extractMin() 
{
    if (!sorted) 
    {
        quickSort(0, size - 1);
        sorted = true;
    }
    if (currentIndex < size) 
    {
        return arr[currentIndex++];
    }
    return -1;
}

template <typename T>
int QuickSort<T>::viewMin() const 
{
    return (size > 0) ? arr[0] : -1;
}

template <typename T>
bool QuickSort<T>::isEmpty() const 
{
    return currentIndex >= size;
}

template <typename T>
int QuickSort<T>::getSize() const 
{
    return size - currentIndex;
}