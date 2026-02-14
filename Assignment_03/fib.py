#! /usr/bin/python

import time

# Program to calculate the Fibonacci sequence up to n-th term
nterms = int(input())

def recur_fibo(n):
   if n <= 1:
       return n
   else:
       return(recur_fibo(n-1) + recur_fibo(n-2))

def execute_fib():
    tic = time.time()

    # check if the number of terms is valid
    if nterms <= 0:
       print("Please enter a positive integer")
    else:
       recur_fibo(nterms)

    tac = time.time()
    execution_time = tac-tic
    print(execution_time)

execute_fib()
