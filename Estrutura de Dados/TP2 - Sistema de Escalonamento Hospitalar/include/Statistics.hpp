#ifndef STATISTICS_HPP
#define STATISTICS_HPP

class Statistics {
private:
    int totalWaitingTime;
    int totalServiceTime;
    int patientCount;

public:
    Statistics();
    void addWaitingTime(int time);
    void addServiceTime(int time);
    double getAverageWaitingTime() const;
    double getAverageServiceTime() const;
};

#endif // STATISTICS_HPP
