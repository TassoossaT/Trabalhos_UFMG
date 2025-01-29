#ifndef LIST_HPP
#define LIST_HPP

class EdgeNode
{
public:
    int data;
    EdgeNode* next;

    EdgeNode(int value) : data(value), next(nullptr) {}
};

class Node
{
public:
    int data;
    Node* next;
    EdgeNode* edges; // List of edges

    Node(int value) : data(value), next(nullptr), edges(nullptr) {}
};

class ListaAdjacencia
{
private:
    Node* head;
    Node* tail;
    int size;

public:
    ListaAdjacencia();
    ~ListaAdjacencia();

    void append(int value);
    void prepend(int value);
    void remove(int value);
    bool find(int value);
    int getSize() const;
    void clear();
    void addEdge(int from, int to); // Add edge method
    EdgeNode* getEdges(int value); // Get edges method
    void appendReverse(int value); // Add new method declaration
};

#endif // LIST_HPP