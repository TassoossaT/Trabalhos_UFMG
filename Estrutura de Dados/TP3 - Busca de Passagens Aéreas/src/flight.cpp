#include <flight.hpp>
#include <date_.hpp>
#include <iostream>


Flight::Flight() : price(0.0), availableSeats(0), departureTime(Date()), arrivalTime(Date()), numberOfStops(0) {}

Flight::Flight(const std::string& origin, const std::string& destination, double price, int availableSeats, 
                const Date& departureTime, const Date& arrivalTime, int numberOfStops)
    : origin(origin), destination(destination), price(price), availableSeats(availableSeats), 
        departureTime(departureTime), arrivalTime(arrivalTime), numberOfStops(numberOfStops) {}

std::string Flight::getOrigin() const {
    return origin;
}

std::string Flight::getDestination() const {
    return destination;
}

double Flight::getPrice() const {
    return price;
}

int Flight::getAvailableSeats() const {
    return availableSeats;
}

Date Flight::getDepartureTime() const {
    return departureTime;
}

Date Flight::getArrivalTime() const {
    return arrivalTime;
}

int Flight::getNumberOfStops() const {
    return numberOfStops;
}

double Flight::getDurationInSeconds() const {
    return (arrivalTime - departureTime) * 3600; // Convert hours to seconds
}

std::ostream& operator<<(std::ostream& os, const Flight& flight) {
    os << flight.origin << " " << flight.destination << " " << flight.price <<
    " " << flight.availableSeats << " " << flight.departureTime << " " 
    << flight.arrivalTime << " " << flight.numberOfStops;
    return os;
}

