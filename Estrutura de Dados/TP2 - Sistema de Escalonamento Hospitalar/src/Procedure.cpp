#include "Procedure.hpp"
#include "Patient.hpp"
#include "date.hpp"
#include "DataStruct.hpp" // Include the header for MinHeap
#include <iostream>

// class Procedure::Unit 
// {
//     int id;
//     Date occupiedUntil;
// public:
//     Unit(int id);
//     Date getOccupiedUntil() const { return occupiedUntil; }
//     void setOccupiedUntil(const Date& date) { occupiedUntil = date; }
//     void addHours(double hours) { occupiedUntil.addHours(hours); }
//     int getId() const { return id; }
// };

Procedure::Unit::Unit(int id) : id(id), occupiedUntil(Date()) {}

Procedure::Procedure(MinHeap<Patient,Date>* esc,double tTri, int nTri, double tAtt, int nAtt, double tMeHosp, int nMeHosp, 
                        double tLabT, int nLabT, double tImg, int nImg, double tInst, int nInst)
    : escalonador(esc), triage(&Unit::getOccupiedUntil), service(&Unit::getOccupiedUntil), medHosp(&Unit::getOccupiedUntil), 
        labTest(&Unit::getOccupiedUntil), imaging(&Unit::getOccupiedUntil), instruments(&Unit::getOccupiedUntil), 
        tri(tTri), att(tAtt), med(tMeHosp), tes(tLabT), img(tImg), inst(tInst)
{
    for (int i = 0; i < nTri;       ++i) triage.insert(new Unit(i));
    for (int i = 0; i < nAtt;       ++i) service.insert(new Unit(i));
    for (int i = 0; i < nMeHosp;    ++i) medHosp.insert(new Unit(i));
    for (int i = 0; i < nLabT;      ++i) labTest.insert(new Unit(i));
    for (int i = 0; i < nImg;       ++i) imaging.insert(new Unit(i));
    for (int i = 0; i < nInst;      ++i) instruments.insert(new Unit(i));
}

Date Procedure::getNextServAvail(int serviceType) 
{
    switch (serviceType) 
    {
        case 2:
            return triage.viewMin()->getOccupiedUntil();
        case 4:
            return service.viewMin()->getOccupiedUntil();
        case 6:
            return medHosp.viewMin()->getOccupiedUntil();
        case 8:
            return labTest.viewMin()->getOccupiedUntil();
        case 10:
            return imaging.viewMin()->getOccupiedUntil();
        case 12:
            return instruments.viewMin()->getOccupiedUntil();
        default:
            return Date(); // Invalid service type
    }
}

void Procedure::occupyUnit(MinHeap<Unit, Date>& units, const Date& currentTime, double duration) 
{
    Unit* unit = units.extractMin();
    unit->setOccupiedUntil(currentTime);
    unit->addHours(duration);
    units.insert(unit);
}

void Procedure::updatePatientTime(Patient* patient, double duration)
{
    patient->addAttendedTime(duration);
}

void Procedure::occupyUnitTriage(Patient* patient, const Date& currentTime) 
{
    double totalDuration = tri;
    occupyUnit(triage, currentTime, totalDuration);
    updatePatientTime(patient, totalDuration);
}

void Procedure::occupyUnitService(Patient* patient, const Date& currentTime) 
{
    double totalDuration = att;
    occupyUnit(service, currentTime, totalDuration);
    updatePatientTime(patient, totalDuration);
}

void Procedure::occupyUnitMedHosp(Patient* patient, const Date& currentTime) 
{
    double totalDuration = med * patient->getHospitalMeasures();
    occupyUnit(medHosp, currentTime, totalDuration);
    updatePatientTime(patient, totalDuration);
}

void Procedure::occupyUnitLabTest(Patient* patient, const Date& currentTime) 
{
    double totalDuration = tes * patient->getLabTests();
    occupyUnit(labTest, currentTime, totalDuration);
    updatePatientTime(patient, totalDuration);
}

void Procedure::occupyUnitImaging(Patient* patient, const Date& currentTime) 
{
    double totalDuration = img * patient->getImagingExams();
    occupyUnit(imaging, currentTime, totalDuration);
    updatePatientTime(patient, totalDuration);
}

void Procedure::occupyUnitInstruments(Patient* patient, const Date& currentTime) 
{
    double totalDuration = inst * patient->getInstrumentsMedications();
    occupyUnit(instruments, currentTime, totalDuration);
    updatePatientTime(patient, totalDuration);
}

void Procedure::processPatient(Patient* patient, const Date& currentTime)
{
    switch (patient->getState())
    {
        case 2:
            occupyUnitTriage(patient, currentTime);
            break;
        case 4:
            occupyUnitService(patient, currentTime);
            break;
        case 6:
            occupyUnitMedHosp(patient, currentTime);
            break;
        case 8:
            occupyUnitLabTest(patient, currentTime);
            break;
        case 10:
            occupyUnitImaging(patient, currentTime);
            break;
        case 12:
            occupyUnitInstruments(patient, currentTime);
            break;
        default:
            break;
    }
}