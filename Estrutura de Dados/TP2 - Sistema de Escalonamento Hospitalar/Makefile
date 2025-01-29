# Compiler
CXX = g++

# Directories
SRC_DIR = src
BIN_DIR = bin
OBJ_DIR = obj
INCLUDE_DIR = include

# Files
SOURCES = $(wildcard $(SRC_DIR)/*.cpp)
OBJECTS = $(SOURCES:$(SRC_DIR)/%.cpp=$(OBJ_DIR)/%.o)
EXECUTABLE = $(BIN_DIR)/tp2.out

# Files
TEST_SOURCES = Teste/dataTeste.cpp
TEST_OBJECTS = $(TEST_SOURCES:%.cpp=$(OBJ_DIR)/%.o)
TEST_EXECUTABLE = $(BIN_DIR)/test_date.out

# Flags
CXXFLAGS = -I$(INCLUDE_DIR) -Wall -Wextra -std=c++11

# Targets
all: $(EXECUTABLE)

test: $(TEST_EXECUTABLE)

$(EXECUTABLE): $(OBJECTS)
	@mkdir -p $(BIN_DIR)
	$(CXX) $(OBJECTS) -o $@

$(TEST_EXECUTABLE): $(TEST_OBJECTS) $(OBJ_DIR)/date.o
	@mkdir -p $(BIN_DIR)
	$(CXX) $(TEST_OBJECTS) $(OBJ_DIR)/date.o -o $@

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp
	@mkdir -p $(OBJ_DIR)
	$(CXX) $(CXXFLAGS) -c $< -o $@

$(OBJ_DIR)/%.o: %.cpp
	@mkdir -p $(dir $@)
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -rf $(OBJ_DIR) $(BIN_DIR)

run: all
	$(EXECUTABLE) "Data/20242TP2 (1).csv"

test_date: test
	$(TEST_EXECUTABLE)

.PHONY: all clean test test_date
