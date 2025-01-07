#include "Statistics.hpp"

Statistics::Statistics() : totalWaitingTime(0), totalServiceTime(0), patientCount(0) {}

void Statistics::addWaitingTime(int time) {
    totalWaitingTime += time;
    patientCount++;
}

void Statistics::addServiceTime(int time) {
    totalServiceTime += time;
}

double Statistics::getAverageWaitingTime() const {
    if (patientCount == 0) return 0.0;
    return static_cast<double>(totalWaitingTime) / patientCount;
}

double Statistics::getAverageServiceTime() const {
    if (patientCount == 0) return 0.0;
    return static_cast<double>(totalServiceTime) / patientCount;
}
