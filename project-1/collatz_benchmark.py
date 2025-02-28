import time

n=10000
def collatz(n):
    count = 0
    while n != 1:
        n = 3 * n + 1 if n % 2 else n // 2
        count += 1
    return count
def benchmark_collatz():
    start_time=time.time()
    result=collatz(n)
    end_time= time.time()
    print(f"Execution Time: {end_time - start_time:.6f} seconds")

if __name__ == "__main__":
    benchmark_collatz()