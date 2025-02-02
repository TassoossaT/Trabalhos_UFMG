CC = gcc
CFLAGS = -Wall -Wextra -std=c99
MAIN = heuristica
TARGET = $(MAIN)
OBJS = $(MAIN).o data.o

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ -lm -lglpk

$(MAIN).o: $(MAIN).c $(MAIN).h data.h
	$(CC) $(CFLAGS) -c $< -o $@

data.o: data.c data.h
	$(CC) $(CFLAGS) -c $<

run: $(TARGET)
	./$(TARGET)

clean:
	rm -f $(TARGET) $(OBJS)