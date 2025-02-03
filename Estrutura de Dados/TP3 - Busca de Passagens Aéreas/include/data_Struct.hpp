/**
 * @file estrutura_dados.hpp
 * @brief Header file for data structures used in the project.
 */

#ifndef ESTRUTURA
#define ESTRUTURA

#include <string>
#include <iostream>
#include <fstream>
#include <stdexcept>


/**
 * @class SequentialList
 * @brief A custom sequential list with indirect indexing.
 */
template <typename T>
class SequentialList {
private:
    T* elements;
    int* indices;
    int size;
    int capacity;

public:
    SequentialList(int n);
    ~SequentialList();

    void insert(const T& value);
    T& operator[](int index);
    int getSize() const;
    void pop_back();
    void print();
};

/**
 * @class DynamicArray
 * @brief A custom dynamic array for storing integers.
 */
class DynamicArray {
private:
    int* data;
    int size;
    int capacity;

    void resize();

public:
    DynamicArray();
    ~DynamicArray();
    DynamicArray(const DynamicArray& other);
    DynamicArray& operator=(const DynamicArray& other);

    void push_back(int value);
    int operator[](int index) const;
    void clear();
    int getSize() const;
    DynamicArray operator&&(const DynamicArray& other) const;
    DynamicArray operator||(const DynamicArray& other) const;
};

/**
 * @class BalancedBinaryTree
 * @brief A class for a balanced binary tree that stores a list of indices for each node value.
 */
template <typename T>
class BalancedBinaryTree 
{
private:
    struct TreeNode 
    {
        T value;
        DynamicArray indices;
        TreeNode* left;
        TreeNode* right;

        TreeNode(const T& val);
    };

    TreeNode* root;

    void insert(TreeNode*& node, const T& value, int index);
    void print(TreeNode* node) const;
    void clear(TreeNode* node);
    void getIndices(TreeNode* node, const T& value, const std::string& op, DynamicArray& result) const;

public:
    /**
     * @brief Constructs a BalancedBinaryTree.
     */
    BalancedBinaryTree();

    /**
     * @brief Destructor for the BalancedBinaryTree.
     */
    ~BalancedBinaryTree();

    /**
     * @brief Inserts a value and index into the tree.
     * @param value The value to insert.
     * @param index The index associated with the value.
     */
    void insert(const T& value, int index);

    /**
     * @brief Prints the tree.
     */
    void print() const;

    /**
     * @brief Retrieves indices based on comparison operator.
     * @param value The value to compare.
     * @param op The comparison operator ("==", ">=", "<=", ">", "<").
     * @return A DynamicArray of indices that match the comparison.
     */
    DynamicArray getIndices(const T& value, const std::string& op) const;

    // Define operators
    DynamicArray operator==(const T& value) const { return getIndices(value, "=="); }
    DynamicArray operator>=(const T& value) const { return getIndices(value, ">="); }
    DynamicArray operator<=(const T& value) const { return getIndices(value, "<="); }
    DynamicArray operator>(const T& value) const { return getIndices(value, ">"); }
    DynamicArray operator<(const T& value) const { return getIndices(value, "<"); }
};

#endif