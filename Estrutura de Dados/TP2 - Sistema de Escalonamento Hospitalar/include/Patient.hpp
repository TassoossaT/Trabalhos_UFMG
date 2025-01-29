#ifndef PATIENT_HPP
#define PATIENT_HPP
#include "date.hpp"

class Patient
{
private:
    int id;
    bool discharged;
    Date AdmissionDate;
    Date dischargedDate;
    Date insertQueueDate;
    int urgencyLevel;
    int triageUrgencyLevel; // New variable for triage urgency level
    int hospitalMeasures;
    int labTests;
    int imagingExams;
    int instrumentsMedications;
    int currentState;
    double queueTime;
    double attendedTime;

public:
    Patient(int id, bool discharged, int year, int month, int day, double hour, int urgencyLevel, int hospitalMeasures, int labTests, int imagingExams, int instrumentsMedications);
    // Getters for each attribute
    int getId() const;
    int getState() const;
    int getLabTests() const;
    int getImagingExams() const;
    int getUrgencyLevel() const;
    Date getAdmissionDate() const;
    Date getDischargedDate() const;
    int getHospitalMeasures() const;
    int getInstrumentsMedications() const;
    bool getDischarged() const;
    double getqueueTime() const;
    double getAttendedTime() const;
    Date getInsertQueueDate() const;
    // Methods to update the state and statistics
    void setState(int state);
    void setInsertQueueDate(const Date& date);
    void addqueueTime(double time);
    void addAttendedTime(double time);
    void updateHour(double t);
    void updateState();
    void consumeHospitalMeasures();
    void consumeLabTests();
    void consumeImagingExams();
    void consumeInstrumentsMedications();
    void setTriageUrgencyLevel(); // New method to set triage urgency level
    void print();
};

#endif // PATIENT_HPP