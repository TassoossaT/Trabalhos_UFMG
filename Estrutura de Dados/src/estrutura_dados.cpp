#include "../include/estrutura_dados.hpp"
#include "../include/memlog.h"

#include <iostream>
#include <fstream>
#include <stdexcept>

// Global variable to store the key used for sorting
std::string sortKey;

// Function to get the value of a DataRow based on the sortKey
std::string getValue(const DataRow& row)
{
    if (sortKey == "name")      {return row.name;   LEMEMLOG((long int)(&(row.name)),   sizeof(std::string), 0);}
    if (sortKey == "id")        {return row.id;     LEMEMLOG((long int)(&(row.id)),     sizeof(std::string), 0);}
    if (sortKey == "address")   {return row.address;LEMEMLOG((long int)(&(row.address)),sizeof(std::string), 0);}
    LEMEMLOG((long int)(&(row.payload)), sizeof(std::string), 0);
    return row.payload;
}

// Explicit template instantiation for SequentialList<DataRow>
template class SequentialList<DataRow>;

// Method to print a DataRow
std::string DataRow::print()
{
    return name + "," + id + "," + address + "," + payload;
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

// Method to insert an element into the SequentialList
template <typename T>
void SequentialList<T>::insert(const T& value)
{
    erroAssert_cond(size < capacity, "List is full");
    indices[size] = size;
    elements[indices[size]] = value;
    ESCREVEMEMLOG((long int)(&(indices[size])), sizeof(int), indices[size]);
    size++;
}

// Overloaded operator[] to access elements by index
template <typename T>
T& SequentialList<T>::operator[](int index)
{
    erroAssert_cond(index >= 0 && index < size, "operator[]: Index out of range " + index);
    LEMEMLOG((long int)(&(indices[index])), sizeof(int), 0);
    return elements[indices[index]];
}

// Method to get the size of the SequentialList
template <typename T>
int SequentialList<T>::getSize() const{return size;}

// Method to remove the last element from the SequentialList
template <typename T>
void SequentialList<T>::pop_back()
{
    if (size > 0)
    {
        --size;
        ESCREVEMEMLOG((long int)(&(indices[size])), sizeof(int), 0);
    }
    // Optionally handle the case when the list is empty
}

// Method to print all elements in the SequentialList
template <typename T>
void SequentialList<T>::print()
{
    for (int i = 0; i < size; ++i)
    {
        std::cout << elements[indices[i]].print() << std::endl;
    }
}

// Method to save all elements in the SequentialList to a file
template <typename T>
void SequentialList<T>::save_file(const std::string& filename)
{
    std::ofstream file(filename);
    erroAssert_cond(file.is_open(), "Could not open file");
    for (int i = 0; i < size; ++i)
    {
        file << elements[indices[i]].print() << std::endl;
    }
    file.close();
}

// Method to swap two elements in the SequentialList
template <typename T>
void SequentialList<T>::swap(int index1, int index2)
{
    erroAssert_cond(index1 >= 0 && index1 < size, "swap: Index1 out of range");
    erroAssert_cond(index2 >= 0 && index2 < size, "swap: Index2 out of range");
    int temp = indices[index1];
    indices[index1] = indices[index2];
    indices[index2] = temp;
    ESCREVEMEMLOG((long int)(&(indices[index1])), sizeof(T), 0);
    ESCREVEMEMLOG((long int)(&(indices[index2])), sizeof(T), 0);
}

// Method to print the header information of the SequentialList
template <typename T>
void SequentialList<T>::print_header()
{
    std::cout<<"4"              <<std::endl;
    std::cout<<"name,s"         <<std::endl;
    std::cout<<"id,s"           <<std::endl;
    std::cout<<"address,s"      <<std::endl;
    std::cout<<"payload,s"      <<std::endl;
    std::cout<<this->getSize()  <<std::endl;
}