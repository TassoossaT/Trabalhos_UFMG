#include <flight.hpp>
#include <data_Struct.hpp>
#include <string>

template <typename T>
class HeapSort
{
private:
    int* heap; // Change to store indices
    int capacity;
    int size;
    SequentialList<T>* flightList; // Pointer to the flight list
    void heapifyUp(int);
    void heapifyDown(int);
    void resize();
    void swap(int&, int&); // Change to swap indices
    std::string sortCriteria;

    bool compare(int a, int b) const; // Change to compare indices

public:
    HeapSort(SequentialList<T>* flightList, const std::string& sortCriteria); // Constructor to accept flight list
    ~HeapSort();
    void insert(int);
    int extractMin();
    int viewMin() const;
    bool isEmpty() const;
    int getSize() const;
};