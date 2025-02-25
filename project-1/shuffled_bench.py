import time
import subprocess
import csv

PYTHON_313 = "C:\\Python313\\python.exe"
PYTHON_314 = "C:\\Python314\\python.exe"

ENERGIBRIDGE_CMD = "C:\\energibridge-v0.0.7-x86_64-pc-windows-msvc\\energibridge.exe"
ENERGY_CSV = "results.csv"

# Matrix Multiplication 
def matrix_multiplication(n):
    A = [[i + j for j in range(n)] for i in range(n)]
    B = [[i - j for j in range(n)] for i in range(n)]
    result = [[0] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            for k in range(n):
                result[i][j] += A[i][k] * B[k][j]

    return result

# Start EnergiBridge
def measure_energy(python_version):
    print(f"Starting EnergiBridge for {python_version}...")

    try:
        # Start EnergiBridge before running the computation
        energy_process = subprocess.Popen(
            [ENERGIBRIDGE_CMD, "-o", ENERGY_CSV, "--summary", "timeout", "5"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )

        # Run matrix multiplication while energy is being measured
        start_time = time.time()
        matrix_multiplication(N)
        exec_time = time.time() - start_time  # Measure execution time

        # Wait for EnergiBridge to finish
        energy_process.wait()

    except subprocess.CalledProcessError as e:
        print(f"Error running EnergiBridge: {e}")
        return exec_time, "ERROR"

    # Parse energy consumption result
    energy_used = parse_energy_results()

    return exec_time, energy_used

# Parse EnergiBridge CSV Output
def parse_energy_results():
    try:
        with open(ENERGY_CSV, "r") as file:
            lines = file.readlines()
            
            # Ensure file has at least two lines (header + data)
            if len(lines) > 1:
                header = lines[0].strip().split(",")  # Extract column headers
                last_line = lines[-1].strip().split(",")  # Extract last row

                # Find index of 'PACKAGE_ENERGY (J)' in the header
                if "PACKAGE_ENERGY (J)" in header:
                    energy_index = header.index("PACKAGE_ENERGY (J)")
                    energy_value = last_line[energy_index]

                    # Convert extracted energy to float
                    try:
                        return float(energy_value)
                    except ValueError:
                        print("Error: Invalid energy value in results.csv.")
                        return 0.0  # Return 0 if conversion fails

                print("Error: 'PACKAGE_ENERGY (J)' column not found in EnergiBridge output.")
                return 0.0  # Return 0 if column is missing

    except FileNotFoundError:
        print("Error: EnergiBridge results.csv not found.")
    except Exception as e:
        print(f"Error reading results.csv: {e}")

    return 0.0  

N = 500  # Matrix size
NUM_RUNS = 15  # Run each version 30 times for full test
REST_TIME = 60  # Pause to stabilize power
SHUFFLE_RUNS = False

if __name__ == "__main__":
    # Strict alternation between Python 3.13 and 3.14
    runs = []
    for _ in range(NUM_RUNS):
        runs.append(("3.13", PYTHON_313))
        runs.append(("3.14", PYTHON_314))

    with open("benchmark_results.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Run", "Python Version", "Execution Time (s)", "Energy (J)"])

        for i, (version, python_path) in enumerate(runs, start=1):
            print(f"Running Test {i}/{NUM_RUNS * 2} - Python {version}")

            exec_time, energy_used = measure_energy(python_path)

            writer.writerow([i, version, exec_time, energy_used])
            time.sleep(REST_TIME)  # Rest period to stabilize power draw

    print("\nBenchmark Complete! Results saved in benchmark_results.csv")
