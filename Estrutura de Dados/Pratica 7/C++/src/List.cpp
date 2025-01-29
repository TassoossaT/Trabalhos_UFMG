#include "../include/List.hpp"
#include <iostream>


ListaAdjacencia::ListaAdjacencia() : head(nullptr), tail(nullptr), size(0) {}


ListaAdjacencia::~ListaAdjacencia() {clear();}


void ListaAdjacencia::append(int value)
{
    Node* newNode = new Node(value);
    if (!head)
    {
        head = tail = newNode;
    } else
    {
        tail->next = newNode;
        tail = newNode;
    }
    size++;
}


void ListaAdjacencia::prepend(int value)
{
    Node* newNode = new Node(value);
    if (!head)
    {
        head = tail = newNode;
    } else
    {
        newNode->next = head;
        head = newNode;
    }
    size++;
}

void ListaAdjacencia::appendReverse(int value)
{
    Node* newNode = new Node(value);
    if (!head)
    {
        head = tail = newNode;
    } else
    {
        newNode->next = head;
        head = newNode;
    }
    size++;
}

void ListaAdjacencia::remove(int value)
{
    if (!head) return;
    if (head->data == value)
    {
        Node* temp = head;
        head = head->next;
        delete temp;
        size--;
        if (!head) tail = nullptr;
        return;
    }

    Node* current = head;
    while (current->next && current->next->data != value)
    {
        current = current->next;
    }

    if (current->next)
    {
        Node* temp = current->next;
        current->next = current->next->next;
        if (temp == tail) tail = current;
        delete temp;
        size--;
    }
}


bool ListaAdjacencia::find(int value)
{
    Node* current = head;
    while (current) 
    {
        if (current->data == value) return true;
        current = current->next;
    }
    return false;
}


int ListaAdjacencia::getSize() const {return size;}


void ListaAdjacencia::clear()
{
    while (head)
    {
        Node* temp = head;
        head = head->next;
        delete temp;
    }
    tail = nullptr;
    size = 0;
}

void ListaAdjacencia::addEdge(int from, int to)
{
    Node* current = head;
    while (current)
    {
        if (current->data == from)
        {
            EdgeNode* newEdge = new EdgeNode(to);
            newEdge->next = current->edges;
            current->edges = newEdge;
            return;
        }
        current = current->next;
    }
}

EdgeNode* ListaAdjacencia::getEdges(int value)
{
    Node* current = head;
    while (current)
    {
        if (current->data == value)
        {
            return current->edges;
        }
        current = current->next;
    }
    return nullptr; // Return nullptr if node not found
}
