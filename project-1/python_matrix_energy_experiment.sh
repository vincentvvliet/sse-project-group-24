#!/bin/bash

# Define Python versions
PYTHON_OLD="python3.11"
PYTHON_NEW="python3.14"

# Define test script
TEST_SCRIPT="benchmark.py"

# Define output file
OUTPUT_FILE="energy_results.csv"

# Ensure EnergiBridge is built
ENERGIBRIDGE="./energibridge/target/release/energibridge"

# Function to run the test and collect energy data
run_experiment() {
    local python_version=$1
    local result_file=$2

    echo "Running matrix multiplication with $python_version..."

    # Start energy measurement
    $ENERGIBRIDGE -o "$result_file" --summary &
    ENERGY_PID=$!

    # Run benchmark
    $python_version $TEST_SCRIPT > "execution_time_$python_version.txt"

    # Stop energy measurement
    kill $ENERGY_PID

    echo "Completed: $python_version"
}

# Write CSV header
echo "Python Version, Energy (Joules), Time (s)" > $OUTPUT_FILE

# Run experiment for both Python versions
run_experiment $PYTHON_OLD "energy_old.csv"
run_experiment $PYTHON_NEW "energy_new.csv"

# Combine results
OLD_ENERGY=$(tail -n 1 energy_old.csv | cut -d',' -f2)
NEW_ENERGY=$(tail -n 1 energy_new.csv | cut -d',' -f2)
OLD_TIME=$(grep 'Execution Time' execution_time_python3.11.txt | awk '{print $3}')
NEW_TIME=$(grep 'Execution Time' execution_time_python3.14.txt | awk '{print $3}')

echo "3.11, $OLD_ENERGY, $OLD_TIME" >> $OUTPUT_FILE
echo "3.14, $NEW_ENERGY, $NEW_TIME" >> $OUTPUT_FILE

echo "Experiment completed! Results saved in $OUTPUT_FILE."

