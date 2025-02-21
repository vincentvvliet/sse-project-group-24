import random
import time

def generate_matrix(size):
    """Generates a square matrix filled with random numbers."""
    return [[random.random() for _ in range(size)] for _ in range(size)]

def multiply_matrices(A, B):
    """Multiplies two square matrices using a naive O(n^3) algorithm."""
    size = len(A)
    result = [[0] * size for _ in range(size)]
    
    for i in range(size):
        for j in range(size):
            for k in range(size):
                result[i][j] += A[i][k] * B[k][j]
    
    return result

def matrix_multiplication_benchmark(size=300):
    """Runs the matrix multiplication benchmark and records execution time."""
    print(f"Generating {size}x{size} matrices...")
    A = generate_matrix(size)
    B = generate_matrix(size)

    print("Starting matrix multiplication...")
    start_time = time.time()
    result = multiply_matrices(A, B)
    end_time = time.time()
    
    print(f"Matrix multiplication completed in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    matrix_multiplication_benchmark()