#!/bin/bash

# Define Python versions
PYTHON_OLD="python3.11"
PYTHON_NEW="python3.14"

# Define test script
TEST_SCRIPT="collatz_benchmark.py"

# Define output file for combined results
OUTPUT_FILE="energy_results.csv"

# Path to EnergiBridge
ENERGIBRIDGE="$HOME/Desktop/energibridge/target/release/energibridge"

# Increase priority to reduce OS interference
echo "Increasing script priority..."
sudo renice -n -20 -p $$

# Function to run the test and collect energy data over a fixed duration
run_experiment() {
    local python_version=$1
    local result_file=$2
    local summary_file="energybridge_output_${python_version}.txt"

    # Start EnergiBridge measurement for 20 seconds
    sudo "$ENERGIBRIDGE" -o "$result_file" --summary sleep 20 > "$summary_file" 2>&1 &
    ENERGY_PID=$!
    sleep 1

    # Run the benchmark repeatedly for 20 seconds to generate measurable load
    local end_time
    end_time=$(($(date +%s) + 20))
    while [ "$(date +%s)" -lt "$end_time" ]; do
         "$python_version" "$TEST_SCRIPT" > /dev/null
    done > /dev/null

    # Wait for EnergiBridge to finish
    wait "$ENERGY_PID"

    # Example line in $summary_file:
    # Energy consumption in joules: 242.35 for 20.01 sec of execution.

    # Parse Joules
    local energy_joules
    energy_joules=$(grep -i "Energy consumption in joules:" "$summary_file" \
        | sed -n 's/.*Energy consumption in joules: \([0-9.]*\).*/\1/p')

    # Parse Time
    local energy_time
    energy_time=$(grep -i "Energy consumption in joules:" "$summary_file" \
        | sed -n 's/.* for \([0-9.]*\) sec of execution.*/\1/p')

    # Return them comma-separated
    echo "$energy_joules,$energy_time"
}

# Write CSV header
echo "Python Version, Joules, Energy_Time" > "$OUTPUT_FILE"

# Run experiment for python3.11
old_data=$(run_experiment "$PYTHON_OLD" "energy_old.csv")
old_joules=$(echo "$old_data" | cut -d',' -f1)
old_time=$(echo "$old_data" | cut -d',' -f2)

# Run experiment for python3.14
new_data=$(run_experiment "$PYTHON_NEW" "energy_new.csv")
new_joules=$(echo "$new_data" | cut -d',' -f1)
new_time=$(echo "$new_data" | cut -d',' -f2)

# Append numeric values to CSV
echo "3.11, $old_joules, $old_time" >> "$OUTPUT_FILE"
echo "3.14, $new_joules, $new_time" >> "$OUTPUT_FILE"

echo "Results saved in $OUTPUT_FILE"
