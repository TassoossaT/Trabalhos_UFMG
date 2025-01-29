# Compiler and flags
CXX = g++
CXXFLAGS = -Wall -Wextra -g3

# Source and target files
TARGET = Tp3_Tasso
SRCS = Tp3_Tasso.cpp
OBJS = $(SRCS:.cpp=.o)

# Default target
all: $(TARGET)

# Build target
$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJS)

# Compile source files into object files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Run the program
run: $(TARGET)
	./$(TARGET)

# Clean up build files
clean:
	rm -f $(TARGET) $(OBJS)