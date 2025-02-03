#include <iostream>
#include <fstream>
#include <string>
#include <flight.hpp>
#include <data_Struct.hpp>
#include <date_.hpp>
#include <heapsort.hpp>
#include <expression.hpp>


int main()
{
    int n;
    std::cin >> n;

    SequentialList<Flight> flightList(n);
    BalancedBinaryTree<std::string> org, dst;
    BalancedBinaryTree<double> prc;
    BalancedBinaryTree<int> sea, sto;
    BalancedBinaryTree<Date> dep, arr;
    BalancedBinaryTree<double> dur;

    for (int i = 0; i < n; ++i)
    {
        std::string origin, destination, departureTimeStr, arrivalTimeStr;
        double price;
        int availableSeats, numberOfStops;

        std::cin >> origin >> destination >> price >> availableSeats >> departureTimeStr >> arrivalTimeStr >> numberOfStops;

        Date departureTime = Date::fromString(departureTimeStr);
        Date arrivalTime = Date::fromString(arrivalTimeStr);

        Flight flight(origin, destination, price, availableSeats, departureTime, arrivalTime, numberOfStops);
        flightList.insert(flight);

        org.insert(origin, i);
        dst.insert(destination, i);
        prc.insert(price, i);
        sea.insert(availableSeats, i);
        dep.insert(departureTime, i);
        arr.insert(arrivalTime, i);
        sto.insert(numberOfStops, i);
        dur.insert(flight.getDurationInSeconds(), i);
    }

    std::cin >> n;
    for (int i = 0; i < n; ++i)
    {
        int m;
        std::string sortCriteria, logicalExpression;
        std::cin >> m >> sortCriteria >> logicalExpression;
        
        // Chama a função recursiva para avaliar a expressão lógica
        DynamicArray indices = evaluateExpressionRec(logicalExpression, org, dst, prc, sea, dep, arr, sto, dur);
        
        HeapSort<Flight> heapSort(&flightList, sortCriteria);
        for (int j = 0; j < indices.getSize(); ++j)
        {
            heapSort.insert(indices[j]);
        }

        for (int j = 0; j < m && !heapSort.isEmpty(); ++j)
        {
            int index = heapSort.extractMin();
            std::cout << flightList[index] << std::endl;
        }
    }

    return 0;
}
