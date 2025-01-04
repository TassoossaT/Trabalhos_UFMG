#include "../include/estrutura_dados.hpp"
#include "../include/sort.hpp"
#include "../include/memlog.h"

#include <iostream>
#include <fstream>
#include <stdexcept>
#include <cstring> // Adicione esta linha
#include <cstdlib> // Adicione esta linha

SequentialList<DataRow> get_data(std::string filename)
{
    std::ifstream inputFile(filename);
    std::string line;
    int numberOfElements;
    if (!inputFile.is_open())
    {
        throw std::runtime_error("Unable to open input file: " + filename);
    }
    for (int i = 0; i < 5; ++i)
    {
        // std::cout << line << std::endl;
        std::getline(inputFile, line);
    }
    inputFile >> numberOfElements;
    inputFile.ignore(); // Ignore the newline character
    SequentialList<DataRow> list(numberOfElements);
    for (int i = 0; i < numberOfElements; ++i)
    {
        DataRow data;
        std::getline(inputFile, data.name, ',');
        std::getline(inputFile, data.id, ',');
        std::getline(inputFile, data.address, ',');
        std::getline(inputFile, data.payload);
        list.insert(data);
    }
    inputFile.close();
    return list;
}

int main(int argc, char* argv[])
{
    if (argc < 2)
    {
        std::cerr << "Usage: " << argv[0] << " <filename>" << std::endl;
        return 1;
    }
    std::string filename = argv[1];
    SequentialList<DataRow> dataList = get_data(filename);
    // InsertionQuickSort logs

    std::string algorithms[] = {"InsertionQuickSort", "QuickSort", "HeapSort"};
    std::string keys[] = {"name", "id", "address"};

    for (const auto& algorithm : algorithms)
    {
        for (const auto& key : keys)
        {
            // Essa parte é apenas para uma automação na leitura e escrita dos dados, não sei fazer de outra forma
            std::string logFileStr = "output/" + algorithm + "/" + key + ".log";
            const char* logFile = logFileStr.c_str();
            // Create directories if they do not exist
            std::string command = "mkdir -p output/" + algorithm;
            system(command.c_str());

            iniciaMemLog(const_cast<char*>(logFile));
            ativaMemLog();
            if (algorithm == "InsertionQuickSort")
            {
                InsertionQuickSort<SequentialList<DataRow>> sorter(&dataList, key);
            } else 
            if (algorithm == "QuickSort")
            {
                QuickSort<SequentialList<DataRow>> sorter(&dataList, key);
            } else 
            if (algorithm == "HeapSort")
            {
                HeapSort<SequentialList<DataRow>> sorter(&dataList, key);
            }
            finalizaMemLog();
            dataList.print_header();
            dataList.print();
        }
    }
    return 0;
}