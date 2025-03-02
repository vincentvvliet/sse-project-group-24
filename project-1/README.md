# Energy Consumption Analysis: Python 3.11 vs Python 3.14

## Overview

This project automates the benchmarking of energy consumption for Python 3.11 and Python 3.14 by running a matrix multiplication workload and measuring energy usage using Energibridge. The experiment is conducted under different optimization settings (`normal` and `optimized` with `PYTHONOPTIMIZE=2`).

## Project Structure

```
project-root/
│── benchmarks/                     # Contains benchmark scripts
│   ├── matrix_benchmark.py         # Matrix multiplication script
│── scripts/                         # Automation scripts
│   ├── setup_env.sh                 # Installs dependencies and sets up environment
│   ├── user_upload.sh               # Handles user uploads
│   ├── experiment.sh                # Runs experiments and collects energy data
│   ├── package_results.sh           # Processes and summarizes results
│── results/                         # Stores experiment results
│── Energibridge/                    # Energy measurement tool
│── requirements.txt                 # Python dependencies
│── python_versions.txt              # Lists tested Python versions
│── README.md                        # Documentation
```

# Running the experiment on Windows

1. Make sure you DON'T already have a version of python 3.11 or python 3.14 already installed. Installation will quietly fail, and I haven't figured out how to make the script find python versions yet. If you do have either of them installed, uninstall them via Apps & features.
2. Open powershell with administrator privileges.
3. Navigate to the folder containing the script and run it with ".\experiment.ps1"

It should then install both versions of python, install energibridge, start energibridge, install requirements.txt, create a .env file, and then run the python code with the experiment. 

If the script does not work, or you want to use existing locations for python 3.11, python 3.14, or energibridge, you can still run the experiment by creating a .env file. Fill this file with PYTHON_3.11_PATH="(insert path)", PYTHON_3.14_PATH="(insert path)", and ENERGIBRIDGE_PATH="(insert path)". Then run the experiment by running main.py.

## Setup Instructions For MacOs and Linux

1. **Install Dependencies**

   ```bash
   bash scripts/setup_env.sh
   ```

   This script installs the required dependencies for running the benchmarks and processing results.

2. **Run the Experiment**

   ```bash
   bash scripts/user_upload.sh  
   bash scripts/experiment.sh   
   bash scripts/package_results.sh  
   ```

3. **Fully Automated Execution** The entire process can be run with a single command:

   ```bash
   bash run_all.sh
   ```

   This script sequentially executes:

   - `setup_env.sh`: Installs dependencies
   - `user_upload.sh`: Prepares necessary files
   - `experiment.sh`: Runs all test scenarios and logs energy consumption
   - `package_results.sh`: Processes and summarizes the results

   If you don't have EnergiBridge or Python versions installed, please remain connected to the internet while running these experiments so that all the uninstalled dependencies are installed.

## Experiment Methodology

- **Warm-up Phase:** Before running benchmarks, the system is warmed up for 5 minutes (Windows) or 1 minute (Mac) by performing CPU-intensive calculations to ensure a stable test environment.
- **Benchmark Execution:**
  - 300x300 matrix multiplication (MacOS, due to different power measurement constraints)
- **Energy Measurement:**
  - Linux: Uses `PACKAGE_ENERGY (J)` from Energibridge
  - MacOS: Uses `SYSTEM_POWER (Watts) × Execution Time (Seconds)`
- **Test Scenarios:**
  - `Python 3.11 normal`
  - `Python 3.14 normal`
  - `Python 3.11 optimized (PYTHONOPTIMIZE=2)`
  - `Python 3.14 optimized (PYTHONOPTIMIZE=2)`
- **Randomized Execution Order:** Each Python version is tested in randomized order to prevent systematic bias.
- **Post-Test Cooldown:** A 1-minute rest time is included between tests to prevent tail energy influence.

## Automation Process

This project is fully automated using Bash scripts that:

1. **Setup the Environment:** Installs necessary dependencies (`setup_env.sh`).
2. **Prepare Files and Uploads:** Ensures required files are present (`user_upload.sh`).
3. **Run Benchmarks:** Executes Python scripts with different versions and optimization levels (`experiment.sh`).
4. **Measure Energy Consumption:** Uses Energibridge to log energy usage.
5. **Process Results:** Converts power readings into energy consumption values and summarizes findings (`package_results.sh`).
6. **Generate Reports:** Outputs statistical results and visualizations.


---

For any issues or contributions, please refer to the repository documentation.
