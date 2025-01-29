# Makefile for compiling C++ files and placing the output in the bin directory

# Compiler
CXX = g++

# Compiler flags
CXXFLAGS = -Wall -g

# Source files
SRCS = $(wildcard *.cpp)

# Object files
OBJS = $(patsubst %.cpp, bin/%.o, $(SRCS))

# Output executable
TARGET = bin/tp3.out

# Default target
all: $(TARGET)

# Rule to create the output directory if it doesn't exist
bin:
	mkdir -p bin

# Rule to build the target executable
$(TARGET): bin $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $(OBJS)

# Rule to build object files
bin/%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Clean up
clean:
	rm -rf bin/*.o $(TARGET)

.PHONY: all clean