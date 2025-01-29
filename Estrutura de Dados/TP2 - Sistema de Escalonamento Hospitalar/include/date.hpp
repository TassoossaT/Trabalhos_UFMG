#ifndef DATE_HPP
#define DATE_HPP

class Date 
{
private:
    int day, month, year;
    double hour;
    bool isLeapYear(int year) const;
    int daysInMonth(int month, int year) const;
    int daysSinceEpoch() const;
public:
    Date();
    Date(int day, int month, int year, double hour);
    double hoursDifference(const Date& other) const;
    const char* dayOfWeek() const;
    const char* monthAbbreviation() const;
    void printDate() const;
    void addHours(double hoursToAdd);
    double toHours() const;
    bool operator>=(const Date& other) const;
    bool operator<=(const Date& other) const;
    bool operator<(const Date& other) const;
    bool operator>(const Date& other) const;
    bool operator==(const Date& other) const;
    bool operator!=(const Date& other) const;
    double operator-(const Date& other) const;
};

#endif // DATE_HPP
