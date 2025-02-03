
#include "flight.hpp"
#include "data_Struct.hpp"
#include "date_.hpp"
#include "sort.hpp"
#include "expression.hpp"
#include <iostream>
#include <fstream>
#include <string>


int main(int argc, char* argv[])
{
    if (argc != 2) {
        std::cerr << "Uso: " << argv[0] << " <arquivo_de_entrada.txt>" << std::endl;
        return 1;
    }

    std::ifstream inputFile(argv[1]);
    if (!inputFile.is_open()) {
        std::cerr << "Erro ao abrir o arquivo de entrada." << std::endl;
        return 1;
    }

    int n;
    inputFile >> n;

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

        inputFile >> origin >> destination >> price >> availableSeats >> departureTimeStr >> arrivalTimeStr >> numberOfStops;

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

    int q;
    inputFile >> q;

    for (int i = 0; i < q; ++i)
    {
        int m;
        std::string sortCriteria, logicalExpression;
        inputFile >> m >> sortCriteria >> logicalExpression;

        DynamicArray indices = evaluateExpressionRec(logicalExpression, org, dst, prc, sea, dep, arr, sto, dur);
        QuickSort<Flight> quickSort(&flightList, sortCriteria);

        for (int j = 0; j < indices.getSize(); ++j)
        {
            quickSort.insert(indices[j]);
        }

        std::cout << m << " " << sortCriteria << " " << logicalExpression << std::endl;
        for (int j = 0; j < m && !quickSort.isEmpty(); ++j)
        {
            int index = quickSort.extractMin();
            std::cout << flightList[index] << std::endl;
        }
    }

    inputFile.close();
    return 0;
}
