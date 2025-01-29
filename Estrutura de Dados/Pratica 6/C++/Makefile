# Compiler
CXX = g++

# Directories
SRC_DIR = src
OBJ_DIR = obj
BIN_DIR = bin

# Files
SOURCES = $(wildcard $(SRC_DIR)/*)
OBJECTS = $(patsubst $(SRC_DIR)/%, $(BIN_DIR)/%.o, $(SOURCES))
MAIN = $(OBJ_DIR)/*

# Flags
CXXFLAGS = -Wall -std=c++11

# Target
TARGET = $(BIN_DIR)/pa2.out

# Rules
all: $(TARGET)

$(TARGET): $(OBJECTS) $(MAIN)
	$(CXX) $(CXXFLAGS) -o $@ $^

$(BIN_DIR)/%.o: $(SRC_DIR)/*
	$(CXX) $(CXXFLAGS) -c -o $@ $<

clean:
	rm -f $(BIN_DIR)/* $(TARGET)

.PHONY: all clean

run: $(TARGET)
	./$(TARGET) 3 1 4 2