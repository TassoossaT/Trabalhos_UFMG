#include <flight.hpp>
#include <data_Struct.hpp>
#include <string>

template <typename T>
class QuickSort
{
private:
    int* arr; // stores indices
    int capacity;
    int size;
    SequentialList<T>* flightList; 
    std::string sortCriteria;
    bool sorted;
    int currentIndex; // tracks extraction
    void quickSort(int, int);
    int partition(int, int);
    void resize();
    void swap(int&, int&);
    bool compare(int, int) const;

public:
    QuickSort(SequentialList<T>* flightList, const std::string& sortCriteria);
    ~QuickSort();
    void insert(int);
    int extractMin();
    int viewMin() const;
    bool isEmpty() const;
    int getSize() const;
};