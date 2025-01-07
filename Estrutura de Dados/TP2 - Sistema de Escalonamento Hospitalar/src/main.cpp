#include "DataStruct.hpp"
#include "pacient.hpp"
#include "Statistics.hpp"
#include <iostream>

int main() {
    Queue queue;
    Statistics stats;

    // Example input
    Pacient p1(9600024, false, 2017, 3, 21, 6, 0, 7, 15, 5, 38);
    p1.setWaitingTime(10);
    p1.setServiceTime(20);
    queue.insert(p1.getGrauUrgencia(), &p1);

    Pacient* attended = queue.getMin();
    if (attended) {
        std::cout << "Average Waiting Time: " << queue.getAverageWaitingTime() << std::endl;
        std::cout << "Average Service Time: " << queue.getAverageServiceTime() << std::endl;
    }

    return 0;
}