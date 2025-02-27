#!/usr/bin/env bash

# Directories
BENCHMARK_DIR="benchmarks/"
ENERGIBRIDGE="$HOME/Desktop/energibridge/target/release/energibridge"
OUTPUT_FILE="results/energy_results.csv"
LOG_FILE="results/execution_logs.txt"
TOTAL_RUNS=30  # Ensuring exactly 30 runs
REST_TIME=60   # Rest time to prevent residual effects

# Create necessary directories
mkdir -p results

# Log output to a file
exec > >(tee -a "$LOG_FILE") 2>&1

echo "⚙️ Increasing script priority..."
sudo renice -n -20 -p $$ >/dev/null

echo "🧘 Entering Zen Mode..."
sleep 5  # Allow user to perform necessary actions

echo "🔥 Warming up CPU for 1 minute..."
end_time=$(( $(date +%s) + 60 ))
while [ "$(date +%s)" -lt "$end_time" ]; do
    python3 -c "x = [i*i for i in range(10**6)]"
done
echo "✅ Warm-up complete!"

# Detect benchmarks
BENCHMARK_SCRIPTS=($(ls $BENCHMARK_DIR/*.py))
PYTHON_VERSIONS=("python3.11" "python3.14")
MODES=("normal" "optimized")

# Generate scenarios (repeat until we reach 30 runs)
declare -a scenarios
for i in $(seq $TOTAL_RUNS); do
    for script in "${BENCHMARK_SCRIPTS[@]}"; do
        for pyversion in "${PYTHON_VERSIONS[@]}"; do
            for mode in "${MODES[@]}"; do
                scenarios+=("$pyversion-$script-$mode")
            done
        done
    done
done

# Shuffle the scenarios
for ((i=${#scenarios[@]}-1; i>0; i--)); do
  j=$((RANDOM % (i+1)))
  tmp="${scenarios[$i]}"
  scenarios[$i]="${scenarios[$j]}"
  scenarios[$j]="$tmp"
done

# Select exactly 30 runs
selected_scenarios=("${scenarios[@]:0:$TOTAL_RUNS}")

# Write CSV Header
echo "Python Version,Benchmark Name,Mode,Energy (Joules),Time (Seconds)" > "$OUTPUT_FILE"

run_experiment() {
    local pyversion=$1
    local script_path=$2
    local mode=$3

    local script_name=$(basename "$script_path")  # Extract filename only

    if [[ "$mode" == "optimized" ]]; then
        python_cmd="env PYTHONOPTIMIZE=2 $pyversion"
    else
        python_cmd="$pyversion"
    fi

    local result_file="results/energy_${pyversion}_${script_name}_${mode}.csv"
    local summary_file="results/energybridge_output_${pyversion}_${script_name}_${mode}.txt"

    echo "▶️ Running $script_name with $pyversion ($mode mode)..."

    # Start energy measurement
    sudo "$ENERGIBRIDGE" -o "$result_file" --summary sleep 20 > "$summary_file" 2>&1 &
    ENERGY_PID=$!
    sleep 1

    # Run benchmark for 20 seconds
    local end_time=$(( $(date +%s) + 20 ))
    while [ "$(date +%s)" -lt "$end_time" ]; do
         $python_cmd "$script_path" >/dev/null
    done

    wait "$ENERGY_PID"

    # Extract energy consumption (Joules) and execution time (Seconds)
    local energy_joules=$(grep -i "Energy consumption in joules:" "$summary_file" | awk '{print $5}')
    local energy_time=$(grep -i "Energy consumption in joules:" "$summary_file" | awk '{print $7}')

    # Ensure values are set (fallback to N/A if not extracted properly)
    energy_joules=${energy_joules:-"N/A"}
    energy_time=${energy_time:-"N/A"}

    # Append results to CSV file
    echo "$pyversion,$script_name,$mode,$energy_joules,$energy_time" >> "$OUTPUT_FILE"
}

# Run experiments (exactly 30 runs)
for scenario in "${selected_scenarios[@]}"; do
  IFS='-' read -ra parts <<< "$scenario"
  pyver="${parts[0]}"
  script="${parts[1]}"
  mode="${parts[2]}"

  run_experiment "$pyver" "$script" "$mode"
  
  echo "⏸ Resting for $REST_TIME seconds..."
  sleep "$REST_TIME"
done

echo "✅ All runs complete! Results saved in $OUTPUT_FILE"
