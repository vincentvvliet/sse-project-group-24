import time

def matrix_multiplication(n):
    A = [[i + j for j in range(n)] for i in range(n)]
    B = [[i - j for j in range(n)] for i in range(n)]
    result = [[0] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            for k in range(n):
                result[i][j] += A[i][k] * B[k][j]

    return result

# Define matrix size
N = 500  # Adjust for higher computation

# Run for 5 minutes
start_time = time.time()
end_time = start_time + 180  # 120 seconds = 2 minutes

iteration_count = 0

while time.time() < end_time:
    matrix_multiplication(N)
    iteration_count += 1

total_time = time.time() - start_time
print(f"Total Execution Time: {total_time:.2f} seconds")
print(f"Total Iterations: {iteration_count}")
