#include <iostream>
#include <sstream>
#include <iomanip>
#include <cmath>
#include <date_.hpp>

Date::Date() : day(1), month(1), year(1900), hour(0), minute(0), second(0) {} //, timezoneOffset(0)

Date::Date(const std::string& dateTimeStr) {
    std::istringstream ss(dateTimeStr);
    char delimiter;

    // Parse da data (ano-mês-dia)
    ss >> year >> delimiter >> month >> delimiter >> day;
    ss.ignore(1, 'T');

    // Parse da hora (hora:minuto:segundo.millisecond)
    ss >> hour >> delimiter >> minute >> delimiter >> second;

    // Comentado: Parse do timezone
    // char sign;
    // ss >> sign;
    // int tzHours, tzMinutes;
    // ss >> tzHours >> delimiter >> tzMinutes;
    // timezoneOffset = (tzHours * 60 + tzMinutes) * (sign == '-' ? -1 : 1);
    // Como o fuso horário foi removido, manter o valor default (0)
    // timezoneOffset = 0;
}

bool Date::isLeapYear(int year) const {
    return (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);
}

int Date::daysInMonth(int month, int year) const {
    static const int daysInMonth[] = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };
    return month == 2 && isLeapYear(year) ? 29 : daysInMonth[month - 1];
}


double Date::hoursDifference(const Date& other) const {
    // Converter a data para segundos desde a época (1970-01-01)
    auto toEpochSeconds = [](const Date& d) -> double {
        int a = (14 - d.month) / 12;
        int y = d.year + 4800 - a;
        int m = d.month + 12 * a - 3;
        int julian_day = d.day + (153 * m + 2) / 5 + 365 * y + y / 4 - y / 100 + y / 400 - 32045;
        int epochJulianDay = 2440588; // Julian Day para 1970-01-01
        int daysSinceEpoch = julian_day - epochJulianDay;
        double totalSeconds = daysSinceEpoch * 86400.0 +
                              d.hour * 3600.0 +
                              d.minute * 60.0 +
                              d.second;
        // Comentado: Ajuste do timezone
        // totalSeconds -= d.timezoneOffset * 60;
        return totalSeconds;
    };
    double t1 = toEpochSeconds(*this);
    double t2 = toEpochSeconds(other);
    return (t1 - t2) / 3600.0;
}

double Date::operator-(const Date& other) const {
    return this->hoursDifference(other);
}

void Date::printDate() const {
    // Comentado: int tzHours = timezoneOffset / 60;
    // Comentado: int tzMinutes = abs(timezoneOffset % 60);

    std::cout << year << "-"
              << std::setfill('0') << std::setw(2) << month << "-"
              << std::setw(2) << day << "T"
              << std::setw(2) << hour << ":"
              << std::setw(2) << minute << ":"
              << std::setw(2) << second;
              // Comentado: << (timezoneOffset >= 0 ? "+" : "-")
              // Comentado: << std::setw(2) << abs(tzHours) << ":"
              // Comentado: << std::setw(2) << tzMinutes;
}

void Date::addHours(double hoursToAdd) {
    int totalMinutes = static_cast<int>(hoursToAdd * 60);
    hour += totalMinutes / 60;
    minute += totalMinutes % 60;

    if (minute >= 60) {
        minute -= 60;
        hour += 1;
    }

    while (hour >= 24) {
        hour -= 24;
        day += 1;

        if (day > daysInMonth(month, year)) {
            day = 1;
            month++;
            if (month > 12) {
                month = 1;
                year++;
            }
        }
    }
}

double Date::toHours() const {
    return day * 24 + hour + minute / 60.0 + second / 3600.0;
}

bool Date::operator>=(const Date& other) const {
    return !(*this < other);
}

bool Date::operator<=(const Date& other) const {
    return !(*this > other);
}

bool Date::operator<(const Date& other) const {
    if (year != other.year) return year < other.year;
    if (month != other.month) return month < other.month;
    if (day != other.day) return day < other.day;
    if (hour != other.hour) return hour < other.hour;
    if (minute != other.minute) return minute < other.minute;
    if (second != other.second) return second < other.second;
    return false;  // Added to ensure a return value in all control paths.
}

bool Date::operator>(const Date& other) const {
    return other < *this;
}

bool Date::operator==(const Date& other) const {
    return year == other.year && month == other.month && day == other.day &&
           hour == other.hour && minute == other.minute &&
           second == other.second;
           // Comentado: && timezoneOffset == other.timezoneOffset;
}

bool Date::operator!=(const Date& other) const {
    return !(*this == other);
}

Date Date::fromString(const std::string& dateTimeStr) {
    return Date(dateTimeStr);
}

std::string Date::toString() const {
    std::ostringstream ss;
    ss << std::setfill('0') << std::setw(4) << year << "-"
       << std::setw(2) << month << "-"
       << std::setw(2) << day << "T"
       << std::setw(2) << hour << ":"
       << std::setw(2) << minute << ":"
       << std::setw(2) << second;
       // Comentado: << (timezoneOffset >= 0 ? "+" : "-")
       // Comentado: << std::setw(2) << abs(timezoneOffset / 60) << ":"
       // Comentado: << std::setw(2) << abs(timezoneOffset % 60);
    return ss.str();
}

std::ostream& operator<<(std::ostream& os, const Date& date) {
    os << date.toString();
    return os;
}
