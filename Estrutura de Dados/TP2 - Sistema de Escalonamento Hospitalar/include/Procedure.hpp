#ifndef PROCEDURE_HPP
#define PROCEDURE_HPP

#include "DataStruct.hpp"
#include "Patient.hpp"
#include "date.hpp"

class Procedure 
{
private:
    class Unit; // Forward declaration

    MinHeap<Patient, Date>* escalonador;
    MinHeap<Unit, Date> triage;
    MinHeap<Unit, Date> service;
    MinHeap<Unit, Date> medHosp;
    MinHeap<Unit, Date> labTest;
    MinHeap<Unit, Date> imaging;
    MinHeap<Unit, Date> instruments;
    double tri, att, med, tes, img, inst;

    void updatePatientTime(Patient* patient, double duration);

public:
    Procedure(MinHeap<Patient, Date>* e, double tTri, int nTriage, double tAtt, int nAttendance, double tMed,
                int nMedHosp, double tTes, int nLabTest, double tImg, int nImaging, double tInst, int nInstruments);

    Date getNextServAvail(int serviceType);
    void occupyUnit(MinHeap<Unit, Date>& units, const Date& currentTime, double duration);

    void occupyUnitTriage(Patient* patient, const Date& currentTime);
    void occupyUnitService(Patient* patient, const Date& currentTime);
    void occupyUnitMedHosp(Patient* patient, const Date& currentTime);
    void occupyUnitLabTest(Patient* patient, const Date& currentTime);
    void occupyUnitImaging(Patient* patient, const Date& currentTime);
    void occupyUnitInstruments(Patient* patient, const Date& currentTime);

    void processPatient(Patient* patient, const Date& currentTime);
};

class Procedure::Unit 
{
private:
    int id;
    Date occupiedUntil;

public:
    Unit(int id);
    Date getOccupiedUntil() const { return occupiedUntil; }
    void setOccupiedUntil(const Date& date) { occupiedUntil = date; }
    void addHours(double hours) { occupiedUntil.addHours(hours); }
    int getId() const { return id; }
};

#endif // PROCEDURE_HPP
