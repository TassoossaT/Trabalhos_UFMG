CC = gcc
CFLAGS = -Wall -g -Iinclude
LDFLAGS = -lm

SRC = src/matop.c src/mat.c

OBJ_DIR = obj
OBJ = $(SRC:src/%.c=$(OBJ_DIR)/%.o)

BIN_DIR = bin
BIN = $(BIN_DIR)/matop

all: $(OBJ_DIR) $(BIN_DIR) $(BIN)

$(OBJ_DIR):
	mkdir -p $(OBJ_DIR)

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

$(BIN): $(OBJ)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

$(OBJ_DIR)/%.o: src/%.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -rf $(OBJ_DIR) $(BIN_DIR)


run_cachegrind: $(BIN)
	valgrind --tool=cachegrind --cachegrind-out-file=cachegrind.out ./$(BIN) -s -x 3 -y 3
	cg_annotate cachegrind.out > cg_annotate.out

run_callgrind: $(BIN)
	valgrind --tool=callgrind --callgrind-out-file=callgrind.out ./$(BIN) -s -x 3 -y 3
	callgrind_annotate callgrind.out > callgrind_annotate.out

.PHONY: all clean run_cachegrind run_callgrind
