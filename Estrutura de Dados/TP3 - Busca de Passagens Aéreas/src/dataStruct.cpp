#include <data_Struct.hpp>
#include <date_.hpp>
#include <flight.hpp>
#include <iostream>
#include <fstream>
#include <stdexcept>

// Explicit template instantiation
template class BalancedBinaryTree<std::string>;
template class BalancedBinaryTree<int>;
template class BalancedBinaryTree<double>;
template class BalancedBinaryTree<Date>;
template class SequentialList<Flight>;

void DynamicArray::resize() {
    capacity *= 2;
    int* newData = new int[capacity];
    for (int i = 0; i < size; ++i) {
        newData[i] = data[i];
    }
    delete[] data;
    data = newData;
}

DynamicArray::DynamicArray() : data(nullptr), size(0), capacity(1) {
    data = new int[capacity];
}

DynamicArray::DynamicArray(const DynamicArray& other) : data(nullptr), size(other.size), capacity(other.capacity) {
    data = new int[capacity];
    for (int i = 0; i < size; ++i) {
        data[i] = other.data[i];
    }
}

DynamicArray& DynamicArray::operator=(const DynamicArray& other) {
    if (this != &other) {
        delete[] data;
        size = other.size;
        capacity = other.capacity;
        data = new int[capacity];
        for (int i = 0; i < size; ++i) {
            data[i] = other.data[i];
        }
    }
    return *this;
}

DynamicArray::~DynamicArray() {
    delete[] data;
}

void DynamicArray::push_back(int value) {
    if (size == capacity) {
        resize();
    }
    data[size++] = value;
}

int DynamicArray::operator[](int index) const {return data[index];}

int DynamicArray::getSize() const {return size;}

void DynamicArray::clear() {size = 0;}

DynamicArray DynamicArray::operator&&(const DynamicArray& other) const {
    DynamicArray result;
    for (int i = 0; i < size; ++i) {
        for (int j = 0; j < other.size; ++j) {
            if (data[i] == other.data[j]) {
                result.push_back(data[i]);
                break;
            }
        }
    }
    return result;
}

DynamicArray DynamicArray::operator||(const DynamicArray& other) const {
    DynamicArray result;
    for (int i = 0; i < size; ++i) {
        result.push_back(data[i]);
    }
    for (int j = 0; j < other.size; ++j) {
        bool found = false;
        for (int i = 0; i < size; ++i) {
            if (other.data[j] == data[i]) {
                found = true;
                break;
            }
        }
        if (!found) {
            result.push_back(other.data[j]);
        }
    }
    return result;
}

template <typename T>
BalancedBinaryTree<T>::TreeNode::TreeNode(const T& val) : value(val), left(nullptr), right(nullptr) {}

template <typename T>
BalancedBinaryTree<T>::BalancedBinaryTree() : root(nullptr) {}

template <typename T>
BalancedBinaryTree<T>::~BalancedBinaryTree() {clear(root);}

template <typename T>
void BalancedBinaryTree<T>::insert(TreeNode*& node, const T& value, int index)
{
    if (!node) {
        node = new TreeNode(value);
        node->indices.push_back(index);
    } else if (value < node->value) {
        insert(node->left, value, index);
    } else if (value > node->value) {
        insert(node->right, value, index);
    } else {
        node->indices.push_back(index);
    }
}

template <typename T>
void BalancedBinaryTree<T>::print(TreeNode* node) const {
    if (node) {
        print(node->left);
        std::cout << node->value << ": ";
        for (int i = 0; i < node->indices.getSize(); ++i) {
            std::cout << node->indices[i] << " ";
        }
        std::cout << std::endl;
        print(node->right);
    }
}

template <typename T>
void BalancedBinaryTree<T>::clear(TreeNode* node) {
    if (node) {
        clear(node->left);
        clear(node->right);
        delete node;
    }
}

template <typename T>
void BalancedBinaryTree<T>::insert(const T& value, int index) {
    insert(root, value, index);
}

template <typename T>
void BalancedBinaryTree<T>::print() const {
    print(root);
}

template <typename T>
void BalancedBinaryTree<T>::getIndices(TreeNode* node, const T& value, const std::string& op, DynamicArray& result) const {
    if (!node) return;

    if (op == "==") {
        if (node->value == value) {
            for (int i = 0; i < node->indices.getSize(); ++i) {
                result.push_back(node->indices[i]);
            }
        }
    } else if (op == ">=") {
        if (node->value >= value) {
            getIndices(node->left, value, op, result);
            for (int i = 0; i < node->indices.getSize(); ++i) {
                result.push_back(node->indices[i]);
            }
        }
        getIndices(node->right, value, op, result);
    } else if (op == "<=") {
        getIndices(node->left, value, op, result);
        if (node->value <= value) {
            for (int i = 0; i < node->indices.getSize(); ++i) {
                result.push_back(node->indices[i]);
            }
        }
    } else if (op == ">") {
        if (node->value > value) {
            getIndices(node->left, value, op, result);
            for (int i = 0; i < node->indices.getSize(); ++i) {
                result.push_back(node->indices[i]);
            }
        }
        getIndices(node->right, value, op, result);
    } else if (op == "<") {
        getIndices(node->left, value, op, result);
        if (node->value < value) {
            for (int i = 0; i < node->indices.getSize(); ++i) {
                result.push_back(node->indices[i]);
            }
        }
    }
}

template <typename T>
DynamicArray BalancedBinaryTree<T>::getIndices(const T& value, const std::string& op) const {
    DynamicArray result;
    getIndices(root, value, op, result);
    return result;
}

template <typename T>
SequentialList<T>::SequentialList(int n) : elements(nullptr), indices(nullptr), size(0), capacity(n)
{
    if (n <= 0)
    {
        throw std::invalid_argument("Capacity must be greater than 0");
    }
    elements = new T[n];
    indices = new int[n];
}

template <typename T>
SequentialList<T>::~SequentialList()
{
    delete[] elements;
    delete[] indices;
}

template <typename T>
void SequentialList<T>::insert(const T& value)
{
    if (size >= capacity) {
        throw std::overflow_error("List is full");
    }
    indices[size] = size;
    elements[indices[size]] = value;
    size++;
}

template <typename T>
T& SequentialList<T>::operator[](int index)
{
    if (index < 0 || index >= size)
    {
        throw std::out_of_range("Index out of range");
    }
    return elements[indices[index]];
}

template <typename T>
int SequentialList<T>::getSize() const {return size;}

template <typename T>
void SequentialList<T>::pop_back() {if (size > 0) {--size;}}

template <typename T>
void SequentialList<T>::print()
{
    for (int i = 0; i < size; ++i)
    {
        std::cout << elements[indices[i]] << std::endl;
    }
}
