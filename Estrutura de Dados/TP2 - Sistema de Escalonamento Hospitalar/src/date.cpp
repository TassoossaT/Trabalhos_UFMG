#include <iostream>
#include "date.hpp"

Date::Date() : day(1), month(1), year(1900), hour(0.0) {}

Date::Date(int day, int month, int year, double hour) : day(day), month(month), year(year), hour(hour) {}

bool Date::isLeapYear(int year) const 
{
    return (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);
}

int Date::daysInMonth(int month, int year) const {
    static const int daysInMonth[] = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };
    if (month == 2 && isLeapYear(year)) {
        return 29;
    }
    return daysInMonth[month - 1];
}

int Date::daysSinceEpoch() const {
    int days = 0;
    for (int y = 1900; y < year; ++y) 
    {
        days += isLeapYear(y) ? 366 : 365;
    }
    for (int m = 1; m < month; ++m) 
    {
        days += daysInMonth(m, year);
    }
    days += day - 1;
    return days;
}

double Date::hoursDifference(const Date& other) const 
{
    int daysDiff = daysSinceEpoch() - other.daysSinceEpoch();
    double hoursDiff = hour - other.hour;
    return daysDiff * 24 + hoursDiff;
}

double Date::operator-(const Date& other) const
{
    return this->hoursDifference(other);
}

const char* Date::dayOfWeek() const 
{
    static const char* days[] = {"Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"};
    int daysSinceEpoch = this->daysSinceEpoch();
    return days[(daysSinceEpoch + 1) % 7]; // 1 Jan 1900 was a Monday
}

const char* Date::monthAbbreviation() const 
{
    static const char* months[] = {"Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"};
    return months[month - 1];
}

void Date::printDate() const 
{
    int hours = static_cast<int>(hour);
    int minutes = static_cast<int>((hour - hours) * 60);
    int seconds = static_cast<int>(((hour - hours) * 60 - minutes) * 60);
    if(seconds>0){seconds=0;minutes+=1;}
    if(minutes>59){minutes=0;hours+=1;}
    std::cout   << dayOfWeek() << " " << monthAbbreviation() << " " 
                << (day < 10 ? " " : "") << day << " " // Ensure day is printed with 2 digits
                << (hours < 10 ? "0" : "") << hours << ":"
                << (minutes < 10 ? "0" : "") << minutes << ":"
                << (seconds < 10 ? "0" : "") << seconds << " " << year;
}

void Date::addHours(double hoursToAdd) 
{
    hour += hoursToAdd;
    while (hour >24.0)
    {
        hour-=24.0;
        day+=1;
    }
    while (day > daysInMonth(month, year)) 
    {
        day -= daysInMonth(month, year);
        month++;
        if (month > 12)
        {
            month = 1;
            year++;
        }
    }
}

double Date::toHours() const 
{
    return daysSinceEpoch() * 24 + hour;
}

bool Date::operator>=(const Date& other) const 
{
    return !(*this < other);
}

bool Date::operator<=(const Date& other) const 
{
    return !(*this > other);
}

bool Date::operator<(const Date& other) const 
{
    if (year != other.year) return year < other.year;
    if (month != other.month) return month < other.month;
    if (day != other.day) return day < other.day;
    return hour < other.hour;
}

bool Date::operator>(const Date& other) const 
{
    if (year != other.year) return year > other.year;
    if (month != other.month) return month > other.month;
    if (day != other.day) return day > other.day;
    return hour > other.hour;
}

bool Date::operator==(const Date& other) const 
{
    return year == other.year && month == other.month && day == other.day && hour == other.hour;
}

bool Date::operator!=(const Date& other) const 
{
    return !(*this == other);
}

