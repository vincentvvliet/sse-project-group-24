# File: matrix_multiply.py

import time
import random

def matrix_multiply(n=300):
    # Create two n×n matrices with random floats
    A = [[random.random() for _ in range(n)] for _ in range(n)]
    B = [[random.random() for _ in range(n)] for _ in range(n)]
    
    # Multiply A × B
    # (Naive O(n^3) approach)
    start_time = time.time()
    C = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            total = 0.0
            for k in range(n):
                total += A[i][k] * B[k][j]
            C[i][j] = total
    end_time = time.time()
    
    print(f"Matrix multiply {n}x{n} Execution Time: {end_time - start_time:.6f} seconds")

if __name__ == "__main__":
    matrix_multiply(300)
