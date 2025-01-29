#include "DataStruct.hpp"
#include "Patient.hpp"
#include "Procedure.hpp"
#include "date.hpp"

#include <iostream>
#include <fstream>
#include <sstream>



int main(int argc, char* argv[]) 
{
    if (argc < 2) 
    {
        std::cerr << "Usage: " << argv[0] << " <input_file>" << std::endl;
        return 1;
    }

    std::ifstream inputFile(argv[1]);
    if (!inputFile.is_open()) 
    {
        std::cerr << "Erro ao abrir o arquivo." << std::endl;
        return 1;
    }

    std::string line;
    double triageTime, treatmentTime, mhTime, tlTime, eiTime, imTime;
    int triageCount, treatmentCount, mhCount, tlCount, eiCount, imCount;
    int numberOfElements;

    inputFile >> triageTime >> triageCount;
    inputFile >> treatmentTime >> treatmentCount;
    inputFile >> mhTime >> mhCount;
    inputFile >> tlTime >> tlCount;
    inputFile >> eiTime >> eiCount;
    inputFile >> imTime >> imCount;
    inputFile >> numberOfElements;
    // Skip the next line which contains the headers


    MinHeap<Patient, Date> Escalonador(&Patient::getDischargedDate);
    MinHeap<Patient, int> estatisticas(&Patient::getId);

    Procedure procedure(&Escalonador,triageTime, triageCount, treatmentTime, treatmentCount, mhTime, mhCount, tlTime, tlCount, eiTime, eiCount, imTime, imCount);

    std::getline(inputFile, line);
    for (int i = 0; i < numberOfElements && std::getline(inputFile, line); ++i) 
    {
        std::istringstream iss(line);
        int id, discharged, year, month, day, hour, urgencyLevel, hospitalMeasures, labTests, imagingExams, instrumentsMedications;
        iss >> id >> discharged >> year >> month >> day >> hour >> urgencyLevel >> hospitalMeasures >> labTests >> imagingExams >> instrumentsMedications;
        Escalonador.insert(new Patient(id, discharged, year, month, day, hour, urgencyLevel, hospitalMeasures, labTests, imagingExams, instrumentsMedications));
    }
    
    inputFile.close();

    FIFO triageQueue;
    PriorityQueue serviceQueue, hospMeasureQueue, labTestsQueue, imagingQueue, instrumentsQueue;
    Date currentData;
    bool terminationCondition = false;

    while (!terminationCondition) 
    {
        Patient* currentPatient = nullptr;
        if (!Escalonador.isEmpty()) 
        {
            currentPatient = Escalonador.extractMin();
            currentData    = currentPatient->getDischargedDate();
        }
        while (currentPatient) 
        {
            switch (currentPatient->getState()) 
            {
                case 1:// go to triage queue
                    currentPatient->setInsertQueueDate(currentData);
                    triageQueue.insert(currentPatient);
                    currentPatient->updateState();
                    break;
                case 2://triage
                    procedure.processPatient(currentPatient, currentData);
                    Escalonador.insert(currentPatient);
                    currentPatient->updateState();
                    break;
                case 3://service queue
                    serviceQueue.insert(currentPatient,currentData);
                    currentPatient->updateState();
                    break;
                case 4://service
                    procedure.processPatient(currentPatient, currentData);
                    if (currentPatient->getDischarged())
                    {
                        currentPatient->setState(13);
                    } else 
                    {
                        currentPatient->updateState();
                    }
                    Escalonador.insert(currentPatient); 
                    break;
                case 5:
                    if(currentPatient->getHospitalMeasures()>0)
                    {
                        hospMeasureQueue.insert(currentPatient,currentData);
                    }else {
                        currentPatient->updateState();
                        Escalonador.insert(currentPatient);
                    }
                    currentPatient->updateState();
                    break;
                case 6://hospital Measures
                    procedure.processPatient(currentPatient, currentData);
                    Escalonador.insert(currentPatient);
                    currentPatient->updateState();
                    break;
                case 7:
                    if(currentPatient->getLabTests()>0)
                    {
                        labTestsQueue.insert(currentPatient,currentData);
                    }else {
                        currentPatient->updateState();
                        Escalonador.insert(currentPatient);
                    }
                    currentPatient->updateState();
                    break;
                case 8://labtest
                    procedure.processPatient(currentPatient, currentData);
                    Escalonador.insert(currentPatient);
                    currentPatient->updateState();
                    break;
                case 9:
                    if(currentPatient->getImagingExams()>0)
                    {
                        imagingQueue.insert(currentPatient,currentData);
                    }else {
                        currentPatient->updateState();
                        Escalonador.insert(currentPatient);
                    }
                    currentPatient->updateState();
                    break;
                case 10:
                    procedure.processPatient(currentPatient, currentData);
                    Escalonador.insert(currentPatient);
                    currentPatient->updateState();
                    break;
                case 11:
                    if(currentPatient->getInstrumentsMedications()>0)
                    {
                        instrumentsQueue.insert(currentPatient,currentData);
                    }else {
                        currentPatient->updateState();
                        Escalonador.insert(currentPatient);
                    }
                    currentPatient->updateState();
                    break;
                case 12:
                    procedure.processPatient(currentPatient, currentData);
                    Escalonador.insert(currentPatient);     
                    currentPatient->updateState();
                    break;
                case 13:
                    estatisticas.insert(currentPatient);
                    currentPatient->updateState();
                    break;
                default:
                    currentPatient = nullptr;
                    break;
            }

            currentPatient = nullptr;
            if (!triageQueue.isEmpty() && currentData >= procedure.getNextServAvail(2))
            {
                // procedure.getNextServAvail(2).printDate();
                currentPatient = triageQueue.extractMin();
                currentPatient->addqueueTime(currentData - currentPatient->getInsertQueueDate());
            } else if (!serviceQueue.isEmpty() && currentData >= procedure.getNextServAvail(4))
            {
                // procedure.getNextServAvail(4).printDate();
                currentPatient = serviceQueue.extractMin();
                currentPatient->addqueueTime(currentData - currentPatient->getInsertQueueDate());
            } else if (!hospMeasureQueue.isEmpty() && currentData >= procedure.getNextServAvail(6))
            {
                // procedure.getNextServAvail(6).printDate();
                currentPatient = hospMeasureQueue.extractMin();
                currentPatient->addqueueTime(currentData - currentPatient->getInsertQueueDate());
            } else if (!labTestsQueue.isEmpty() && currentData >= procedure.getNextServAvail(8))
            {
                // procedure.getNextServAvail(8).printDate();
                currentPatient = labTestsQueue.extractMin();
                currentPatient->addqueueTime(currentData - currentPatient->getInsertQueueDate());
            } else if (!imagingQueue.isEmpty() && currentData >= procedure.getNextServAvail(10))
            {
                // procedure.getNextServAvail(10).printDate();
                currentPatient = imagingQueue.extractMin();
                currentPatient->addqueueTime(currentData - currentPatient->getInsertQueueDate());
            } else if (!instrumentsQueue.isEmpty() && currentData >= procedure.getNextServAvail(12))
            {
                // procedure.getNextServAvail(12).printDate();
                currentPatient = instrumentsQueue.extractMin();
                currentPatient->addqueueTime(currentData - currentPatient->getInsertQueueDate());
            }
            // if(currentPatient)
            // {
            //     std::cout<<std::endl;
            //     std::cout<<currentPatient->getId()<<std::endl;
            //     currentPatient->getInsertQueueDate().printDate();
            //     std::cout<<std::endl;
            //     currentPatient->print();
            //     std::cout<<std::endl;
            // }
        }
        terminationCondition = !currentPatient && Escalonador.isEmpty() && serviceQueue.isEmpty() && hospMeasureQueue.isEmpty() && labTestsQueue.isEmpty() && imagingQueue.isEmpty() && instrumentsQueue.isEmpty();
    }
    while (!estatisticas.isEmpty())
    {
        estatisticas.extractMin()->print();
    }
    
    return 0;
}
