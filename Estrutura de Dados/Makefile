# Makefile for compiling and running the project

# Compiler
CXX = g++

# Compiler flags
CXXFLAGS = -Wall -std=c++11 

# Target executables
TARGET = bin/tp1.out
ANALISAMEM = bin/analisamem

# Source files
SRCS = $(wildcard src/*.cpp src/*.c) main/main.cpp

# Object files
OBJS = $(patsubst src/%.cpp %.c, obj/%.o, $(filter-out main/main.cpp, $(SRCS))) obj/main.o
ANALISAMEM_OBJS = $(patsubst src/%.cpp %.c, obj/%.o, $(filter-out main/main.cpp, $(SRCS))) obj/analisamem.o

# Default target
all: $(TARGET)

# Link object files to create the executables
$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJS)

$(ANALISAMEM): $(ANALISAMEM_OBJS)
	$(CXX) $(CXXFLAGS) -o $(ANALISAMEM) $(ANALISAMEM_OBJS) -lm

# Compile source files to object files
obj/%.o: src/%.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

obj/main.o: main/main.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

obj/%.o: src/%.c
	$(CC) -g -Wall -c $< -o $@ -Iinclude

obj/%.o: mem/%.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Clean up build files
clean:
	rm -f obj/* obj/* $(TARGET) $(ANALISAMEM)
	# Remove the output directory
	rm -rf output
# Run the program with Valgrind
valgrind: $(TARGET)
	valgrind --leak-check=full ./$(TARGET) 2>&1 | tee output/valgrind_output.txt

# Run the program
run: $(TARGET)
	./$(TARGET) Data/cad.r5000.p5000.xcsv

# Run analisamem
run_analisamem: $(ANALISAMEM)
	./$(ANALISAMEM) -i quick.out -p output_prefix -f png

# use: $(ANALISAMEM)
# 	mkdir -p output
# 	fixaddr/fixaddr.csh output/quick.out output/
# 	$(ANALISAMEM) -i output/quick.out.fixed -p output/mem
# 	gnuplot output/*.gp
use: $(ANALISAMEM)
	mkdir -p output
	for algorithm in InsertionQuickSort QuickSort HeapSort; do \
		for key in name id address; do \
			mkdir -p output/$$algorithm/$$key; \
			fixaddr/fixaddr.csh output/$$algorithm/$$key.log output/$$algorithm/$$key/; \
			$(ANALISAMEM) -i output/$$algorithm/$$key/$$key.log.fixed -p output/$$algorithm/$$key/$$key; \
		done \
	done
	gnuplot output/*/*/*.gp
	ls output/*

valgrind_analisamem: $(ANALISAMEM)
	mkdir -p output
	for algorithm in InsertionQuickSort QuickSort HeapSort; do \
		for key in name id address; do \
			fixaddr/fixaddr.csh output/$$algorithm/$$key.log output/$$algorithm/; \
			valgrind --leak-check=full $(ANALISAMEM) -i output/$$algorithm/$$key.log.fixed -p output/$$algorithm/$$key 2>&1 | tee output/valgrind_$$algorithm_$$key_output.txt; \
		done \
	done
	gnuplot output/*/*.gp
	ls output/*

