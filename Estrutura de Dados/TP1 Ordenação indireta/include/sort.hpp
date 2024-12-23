#ifndef SORT
#define SORT

/**
 * @file sort.hpp
 * @brief Header file for the QuickSort class template.
 *
 * This file contains the declaration of the QuickSort class template, which provides
 * an implementation of the QuickSort algorithm for sorting a list of elements.
 */

#include <string>


template <typename T>
class QuickSort
/**
 * @class QuickSort
 * @brief A class template for performing QuickSort on a list of elements.
 *
 * @tparam T The type of the list to be sorted.
 */
{
protected:
    T& list; ///< Reference to the list to be sorted.
    
    virtual void sort(int l, int r);//virtual for overrite in insertion quick
    /**
     * @brief Sorts the list between indices l and r.
     * 
     * @param l The left index.
     * @param r The right index.
     */
    
    void partition(int l, int r, int* i, int* j);
    /**
     * @brief Partitions the list between indices l and r.
     * 
     * @param l The left index.
     * @param r The right index.
     * @param i Pointer to the left partition index.
     * @param j Pointer to the right partition index.
     */
    
    void median3(int low, int pivot, int high);
    /**
     * @brief Finds the median of three elements and rearranges them.
     * 
     * @param low The index of the low element.
     * @param pivot The index of the pivot element.
     * @param high The index of the high element.
     */
    
public:
    QuickSort(T* l, std::string key);
    /**
     * @brief Constructs a QuickSort object.
     * 
     * @param l Pointer to the list to be sorted.
     * @param key The key used for sorting.
     */
};

template <typename T>
class InsertionQuickSort: QuickSort<T>
/**
 * @class InsertionQuickSort
 * @brief A class template for performing QuickSort on a list of elements.
 *
 * @tparam T The type of the list to be sorted.
 */
{
public:
    InsertionQuickSort(T* l, std::string key);
private:
    void sort(int l, int r) override;
    /**
     * @brief Sorts the list between indices l and r.
     * 
     * @param l The left index.
     * @param r The right index.
     */
    void insertion(int l, int r);
    /**
     * @brief Sorts the list between indices l and r.
     * 
     * @param l The left index.
     * @param r The right index.
     */
};

template <typename T>
class HeapSort 
{
public:
    HeapSort(T* l, std::string key);
    void sort();

private:
    void heapify(int n, int i);
    T& list;
};

#endif