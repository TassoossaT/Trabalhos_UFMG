#include "Patient.hpp"
#include "date.hpp"

#include <iostream>
#include <iomanip> // Necessário para setprecision e setw

Patient::Patient(int id, bool discharged, int year, int month, int day, double hour, int urgencyLevel, int hospM, int labTests, int imgExams, int instMed)
    : id(id), discharged(discharged), AdmissionDate(day, month, year, hour), dischargedDate(day, month, year, hour), urgencyLevel(urgencyLevel), 
    triageUrgencyLevel(0), // Initialize triage urgency level to 0
    hospitalMeasures(hospM), labTests(labTests), imagingExams(imgExams), instrumentsMedications(instMed), 
    currentState(1), queueTime(0.0), attendedTime(0.0) {}

int  Patient::getId()                        const { return id; }
bool Patient::getDischarged()               const { return discharged; }
int  Patient::getUrgencyLevel()              const { return triageUrgencyLevel; }

int Patient::getHospitalMeasures()          const { return hospitalMeasures; }
int Patient::getLabTests()                  const { return labTests; }
int Patient::getImagingExams()              const { return imagingExams; }
int Patient::getInstrumentsMedications()    const { return instrumentsMedications; }

void   Patient::updateState() { this->currentState += 1; }
void   Patient::setState(int state) {currentState = state;}
int    Patient::getState()          const { return currentState; }
void   Patient::addqueueTime(double time) { this->queueTime += time; this->updateHour(time);}
double Patient::getqueueTime()      const { return queueTime; }
void   Patient::addAttendedTime(double time) { this->attendedTime += time;this->updateHour(time);}
double Patient::getAttendedTime()   const { return attendedTime; }

void Patient::consumeHospitalMeasures()         { hospitalMeasures--; }
void Patient::consumeLabTests()                 { labTests--; }
void Patient::consumeImagingExams()             { imagingExams--; }
void Patient::consumeInstrumentsMedications()   { instrumentsMedications--; }

void Patient::setInsertQueueDate(const Date& date) { insertQueueDate = date; }
Date Patient::getInsertQueueDate() const { return insertQueueDate; }
Date Patient::getAdmissionDate()   const { return AdmissionDate;   }
Date Patient::getDischargedDate()  const { return dischargedDate;  }

void   Patient::updateHour(double t) { dischargedDate.addHours(t); }

void Patient::setTriageUrgencyLevel() 
{
    triageUrgencyLevel = urgencyLevel;
}

void Patient::print()
{
    std::cout << id << " ";
    AdmissionDate.printDate();
    std::cout << " ";
    dischargedDate.printDate();
    std::cout << " ";

    // Configurar o formato de saída numérica
    std::cout << std::fixed << std::setprecision(2); // Fixar 2 casas decimais

    // Imprimir valores com largura fixa de 4 caracteres, preenchendo com espaços à esquerda
    std::cout << std::setw(5) << std::right << attendedTime + queueTime << " ";
    std::cout << std::setw(5) << std::right << attendedTime << " ";
    std::cout << std::setw(5) << std::right << queueTime << std::endl;
}
