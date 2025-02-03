#ifndef FLIGHT_HPP
#define FLIGHT_HPP

#include <string>
#include <date_.hpp>

class Flight {
private:
    std::string origin;
    std::string destination;
    double price;
    int availableSeats;
    Date departureTime;
    Date arrivalTime;
    int numberOfStops;

public:
    Flight();
    Flight(const std::string& origin, const std::string& destination, double price, int availableSeats, 
            const Date& departureTime, const Date& arrivalTime, int numberOfStops);

    std::string getOrigin() const;
    std::string getDestination() const;
    double getPrice() const;
    int getAvailableSeats() const;
    Date getDepartureTime() const;
    Date getArrivalTime() const;
    int getNumberOfStops() const;
    double getDurationInSeconds() const;
    friend std::ostream& operator<<(std::ostream& os, const Flight& flight);
};

#endif // FLIGHT_HPP
