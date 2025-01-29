CXX = g++
CXXFLAGS = -Wall -std=c++11
TARGET_DIR = ../bin
TARGET = $(TARGET_DIR)/pa.out
SRC = AVL.cpp

all: $(TARGET)

$(TARGET): $(SRC)
	@mkdir -p $(TARGET_DIR)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SRC)

clean:
	rm -f $(TARGET)

run: $(TARGET)
	./$(TARGET)

.PHONY: all clean run
