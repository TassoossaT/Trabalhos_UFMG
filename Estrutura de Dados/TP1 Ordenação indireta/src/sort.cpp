#include "../include/estrutura_dados.hpp"
#include "../include/sort.hpp"
#include <iostream>

// Global sort key
extern std::string sortKey;

// Explicit template instantiation for different sorting algorithms
template class QuickSort<SequentialList<DataRow>>;
template class InsertionQuickSort<SequentialList<DataRow>>;
template class HeapSort<SequentialList<DataRow>>;

// Constructor for QuickSort class
template <typename T>
QuickSort<T>::QuickSort(T* l, std::string key) : list(*l)
{
    sortKey = key;
    sort(0, (list.getSize() - 1));
}

// Main sorting function for QuickSort
template <typename T>
void QuickSort<T>::sort(int l, int r)
{
    int i, j;
    partition(l, r, &i, &j);
    if (l < j) sort(l, j);
    if (i < r) sort(i, r);
}

// Partition function for QuickSort
template <typename T>
void QuickSort<T>::partition(int l, int r, int* i, int* j)
{
    *i = l; 
    *j = r;
    int pivot = (*i + *j) / 2; // Get the pivot
    median3(*i, pivot, *j); // Adjust the pivot using median of three
    auto pivotValue = getValue(list[pivot]);

    do
    { 
        while (pivotValue > getValue(list[*i])) {(*i)++;}
        while (pivotValue < getValue(list[*j])) {(*j)--;}
        if (*i <= *j)
        {
            list.swap(*i, *j);
            (*i)++; 
            (*j)--;
        }
    } while (*i <= *j);
}

// Function to calculate the median of three elements
template <typename T>
void QuickSort<T>::median3(int low, int pivot, int high)
{
    if (getValue(list[low])   > getValue(list[pivot])) list.swap(low, pivot);
    if (getValue(list[pivot]) > getValue(list[high]))  list.swap(pivot, high);
    if (getValue(list[low])   > getValue(list[pivot])) list.swap(low, pivot);
}

// Constructor for HeapSort class
template <typename T>
HeapSort<T>::HeapSort(T* l, std::string key) : list(*l)
{
    sortKey = key;
    sort();
}

// Main sorting function for HeapSort
template <typename T>
void HeapSort<T>::sort()
{
    int n = list.getSize();
    for (int i = n / 2 - 1; i >= 0; i--)
        heapify(n, i);
    for (int i = n - 1; i > 0; i--) {
        list.swap(0, i);
        heapify(i, 0);
    }
}

// Function to reorganize the heap
template <typename T>
void HeapSort<T>::heapify(int n, int i)
{
    int largest = i;
    int left = 2 * i + 1;
    int right = 2 * i + 2;

    if (left < n && getValue(list[left]) > getValue(list[largest]))
        largest = left;

    if (right < n && getValue(list[right]) > getValue(list[largest]))
        largest = right;

    if (largest != i) {
        list.swap(i, largest);
        heapify(n, largest);
    }
}

// Constructor for InsertionQuickSort class
template <typename T>
InsertionQuickSort<T>::InsertionQuickSort(T* l, std::string key) : QuickSort<T>(l, key) {}

// Main sorting function for InsertionQuickSort
template <typename T>
void InsertionQuickSort<T>::sort(int l, int r)
{
    if (r - l <= 50)
    {
        insertion(l, r);
    } else {
        int i, j;
        this->partition(l, r, &i, &j);
        if (l < j) sort(l, j);
        if (i < r) sort(i, r);
    }
}

// Insertion sort function
template <typename T>
void InsertionQuickSort<T>::insertion(int l, int r)
{
    for (int i = l + 1; i <= r; i++)
    {
        auto key = this->list[i];
        int j = i - 1;
        while (j >= l && getValue(this->list[j]) > getValue(key))
        {
            this->list[j + 1] = this->list[j];
            j--;
        }
        this->list[j + 1] = key;
    }
}