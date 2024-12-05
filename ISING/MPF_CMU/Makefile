SHELL=/bin/bash

# Use Homebrew's GCC
CC=gcc-14
CFLAGS=-O3 -fopenmp $(shell gsl-config --cflags)
LFLAGS=-lm $(shell gsl-config --libs)
OBJ = mpf.o mcmc.o nlin.o nsb.o

all: main.c $(OBJ)
	$(CC) $(CFLAGS) main.c $(OBJ) -o mpf $(LFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f *.o mpf