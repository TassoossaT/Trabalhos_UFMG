#include <iostream>
#include "date.hpp"

void testDateOperations() {
    Date date1(1, 1, 2000, 12.0);
    Date date2(2, 1, 2000, 12.0);

    std::cout << "Date 1: ";
    date1.printDate();
    std::cout << std::endl;

    std::cout << "Date 2: ";
    date2.printDate();
    std::cout << std::endl;

    std::cout << "Difference in hours: " << date2 - date1 << std::endl;
    for (int i = 0; i<10;i++)
    {
        date1.addHours(1.2);
        std::cout << "Difference in hours: " << date2 - date1 << std::endl;
    }

    date1.addHours(15.5);
    std::cout << "Date 1 after adding 15.5 hours: ";
    date1.printDate();
    std::cout << std::endl;

    std::cout << "Date 1 day of week: " << date1.dayOfWeek() << std::endl;
    std::cout << "Date 2 day of week: " << date2.dayOfWeek() << std::endl;

    std::cout << "Date 1 >= Date 2: " << (date1 >= date2) << std::endl;
    std::cout << "Date 1 <= Date 2: " << (date1 <= date2) << std::endl;
    std::cout << "Date 1 < Date 2: " << (date1 < date2) << std::endl;
    std::cout << "Date 1 > Date 2: " << (date1 > date2) << std::endl;
    std::cout << "Date 1 == Date 2: " << (date1 == date2) << std::endl;
    std::cout << "Date 1 != Date 2: " << (date1 != date2) << std::endl;
}

int main() {
    testDateOperations();
    return 0;
}
