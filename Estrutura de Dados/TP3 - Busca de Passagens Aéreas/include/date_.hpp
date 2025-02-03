#ifndef DATE_HPP
#define DATE_HPP

#include <iostream> // Add this include for std::ostream

class Date 
{
private:
    int day, month, year, hour, minute, second, millisecond;
    int timezoneOffset; // in hour
    bool isLeapYear(int year) const;
    int daysInMonth(int month, int year) const;
public:
    Date(); // Ensure this line for the default constructor is present
    Date(const std::string& dateTimeStr);

    static Date fromString(const std::string& dateTimeStr);
    std::string toString() const;
    double hoursDifference(const Date& other) const;
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
    friend std::ostream& operator<<(std::ostream& os, const Date& date); // Add this line
};

#endif // DATE_HPP
