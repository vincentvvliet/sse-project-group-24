import time
import random
import subprocess
import os
import signal

benchmark_script = "C:\\Users\\Luc\\sse-project-group-24\\project-1\\benchmark.py"

# Define paths to Python versions
python_311 = "C:\\Users\\Luc\\AppData\\Local\\Programs\\Python\\Python311\\python.exe"
python_314 = "C:\\Users\\Luc\\AppData\\Local\\Programs\\Python\\Python314\\python.exe"


# Path to EnergyBridge
energybridge_exe = r"C:\Users\Luc\Desktop\energibridge\energibridge.exe"

output_dir = r"C:\Users\Luc\sse-project-group-24\project-1\energy_results"
os.makedirs(output_dir, exist_ok=True)

def warm_up_cpu(duration=300):
    print("Warming up CPU for 5 minutes...")
    start_time = time.time()
    while time.time() - start_time < duration:
        [x**2 for x in range(10**6)]  # Generate CPU load

# Function to run EnergyBridge for measuring energy
def start_energybridge(output_file):
    print("Starting energy measurement...")
    return subprocess.Popen([energybridge_exe, "-o", output_file, "--summary", "timeout", "20"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def run_test(python_path, version_label, run_number):
    print(f"Running {version_label}, Run {run_number}...")

    # Generate unique CSV filename for this run
    energy_csv = os.path.join(output_dir, f"energy_{version_label}_run{run_number}.csv")

    # Start EnergyBridge measurement
    energy_process = start_energybridge(energy_csv)
    
    # Run Python script
    subprocess.run([python_path, benchmark_script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for EnergyBridge to finish
    energy_process.terminate()
    energy_process.wait()

    print(f"Finished {version_label}, Run {run_number}. Energy data saved to {energy_csv}")

# Prepare randomized test order
test_order = [(version, idx + 1) for idx, version in enumerate(["3.11"] * 30 + ["3.14"] * 30)]
random.shuffle(test_order)

warm_up_cpu()

# Run tests in randomized order
for version, run_number in test_order:
    python_exe = python_311 if version  == "3.11" else python_314
    label = f"Python {version}"
    run_test(python_exe, f"Python{version}", run_number)
    time.sleep(60)

print("Experiment complete! Energy results saved in energy_results.csv")

