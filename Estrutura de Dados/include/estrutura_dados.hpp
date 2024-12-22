/**
 * @file estrutura_dados.hpp
 * @brief Header file for data structures used in the project.
 */

#ifndef ESTRUTURA
#define ESTRUTURA

#include <string>

/**
 * @struct DataRow
 * @brief Represents a row of data with various fields.
 */
struct DataRow
{
    std::string name;    ///< Name of the data row
    std::string id;      ///< ID of the data row
    std::string address; ///< Address of the data row
    std::string payload; ///< Payload of the data row

    /**
     * @brief Prints the data row as a formatted string.
     * @return A string representation of the data row.
     */
    std::string print();
};

/**
 * @class SequentialList
 * @brief A template class for a sequential list of elements.
 * @tparam T The type of elements stored in the list.
 */
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
    /**
     * @brief Constructs a SequentialList with a given capacity.
     * @param n The maximum capacity of the list.
     */
    SequentialList(int n);

    /**
     * @brief Destructor for the SequentialList.
     */
    ~SequentialList();

    /**
     * @brief Inserts a value into the list.
     * @param value The value to be inserted.
     */
    void insert(const T& value);

    /**
     * @brief Accesses an element by index.
     * @param index The index of the element to access.
     * @return A reference to the element at the specified index.
     */
    T& operator[](int index);

    /**
     * @brief Gets the current size of the list.
     * @return The current size of the list.
     */
    int getSize() const;

    /**
     * @brief Removes the last element from the list.
     */
    void pop_back();

    /**
     * @brief Prints the elements of the list.
     */
    void print();

    /**
     * @brief Swaps two elements in the list by their indices.
     * @param index1 The index of the first element.
     * @param index2 The index of the second element.
     */
    void swap(int index1, int index2);

    /**
     * @brief Saves the list to a file.
     * @param filename The name of the file to save the list to.
     */
    void save_file(const std::string& filename);

    /**
     * @brief Prints the header information of the list.
     */
    void print_header();
};

/**
 * @brief Gets a value from a DataRow.
 * @param row The DataRow to get the value from.
 * @return A string value from the DataRow.
 */
std::string getValue(const DataRow& row);

#endif