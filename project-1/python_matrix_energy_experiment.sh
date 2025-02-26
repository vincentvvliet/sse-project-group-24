#!/usr/bin/env bash

# Python scripts
COLLATZ_SCRIPT="collatz_benchmark.py"
MATRIX_SCRIPT="matrix_benchmark.py"

# Path to EnergiBridge
ENERGIBRIDGE="$HOME/Desktop/energibridge/target/release/energibridge"

# Output file
OUTPUT_FILE="energy_results.csv"

echo "========================="
echo "🏁 Starting Python Energy Benchmarking"
echo "========================="
echo "Increasing script priority..."
sudo renice -n -20 -p $$ >/dev/null

# 🛠 Check Python versions
echo "🔍 Checking Python versions..."
python3.11 --version || { echo "❌ Python 3.11 not found!"; exit 1; }
python3.14 --version || { echo "❌ Python 3.14 not found!"; exit 1; }
echo "✅ Python versions are available."

# 🏋️‍♂️ Warm-up CPU to ensure accurate measurements
echo "🔥 Warming up CPU for 5 minutes..."
end_time=$(( $(date +%s) + 300 ))
while [ "$(date +%s)" -lt "$end_time" ]; do
    python3 -c "x = [i*i for i in range(10**6)]" >/dev/null 2>&1
done
echo "✅ Warm-up complete!"

# 🏗 Define test scenarios (10 per version per method + 3.14 with optimizations)
declare -a scenarios
for i in $(seq 10); do
  scenarios+=("3.11-collatz-normal")
  scenarios+=("3.14-collatz-normal")
  scenarios+=("3.14-collatz-optimized")
  scenarios+=("3.11-matrix-naive")
  scenarios+=("3.14-matrix-naive")
  scenarios+=("3.14-matrix-optimized")
done

# 🎲 Shuffle the scenarios (Fisher-Yates shuffle)
for ((i=${#scenarios[@]}-1; i>0; i--)); do
  j=$((RANDOM % (i+1)))
  tmp="${scenarios[$i]}"
  scenarios[$i]="${scenarios[$j]}"
  scenarios[$j]="$tmp"
done

# 📌 Function to run a single experiment
run_experiment() {
    local pyversion=$1
    local script_name=$2
    local method=$3
    local mode=$4  # normal or optimized

    echo "----------------------------------------"
    echo "🚀 Running Experiment: $pyversion | $script_name | $method | $mode"
    
    # Choose the correct Python command
    if [[ "$mode" == "optimized" ]]; then
        python_cmd="python$pyversion --enable-optimizations"
    else
        python_cmd="python$pyversion"
    fi

    # Output files
    local result_file="energy_${pyversion}_${script_name}_${method}_${mode}.csv"
    local summary_file="energybridge_output_${pyversion}_${script_name}_${method}_${mode}.txt"

    # ✅ Check if EnergiBridge is executable
    if [ ! -x "$ENERGIBRIDGE" ]; then
        echo "❌ EnergiBridge not found or not executable! Exiting."
        exit 1
    fi

    # 🚀 Start EnergiBridge monitoring
    echo "⚡ Starting EnergiBridge..."
    sudo "$ENERGIBRIDGE" -o "$result_file" --summary sleep 20 > "$summary_file" 2>&1 &
    ENERGY_PID=$!
    sleep 1  # Allow EnergiBridge to initialize

    # 🏁 Run the benchmark for 20 seconds
    local end_time=$(( $(date +%s) + 20 ))
    while [ "$(date +%s)" -lt "$end_time" ]; do
         $python_cmd "$script_name" "$method" >/dev/null 2>&1
    done

    # 🕐 Wait for EnergiBridge to complete
    wait "$ENERGY_PID"

    # 📊 Extract energy consumption & execution time
    local energy_joules=$(grep -i "Energy consumption in joules:" "$summary_file" | sed -n 's/.*Energy consumption in joules: \([0-9.]*\).*/\1/p')
    local energy_time=$(grep -i "Energy consumption in joules:" "$summary_file" | sed -n 's/.* for \([0-9.]*\) sec of execution.*/\1/p')
    
    # 🔍 Run benchmark script once to get execution time
    local script_exec_time=$($python_cmd "$script_name" "$method" 2>&1 | awk '/Execution Time|Matrix multiply/ {print $(NF-1)}')

    # 🛑 Handle missing values
    energy_joules=${energy_joules:-"N/A"}
    energy_time=${energy_time:-"N/A"}
    script_exec_time=${script_exec_time:-"N/A"}

    echo "✅ Results: Joules=$energy_joules | Energy_Time=$energy_time | ExecTime=$script_exec_time"

    # Return results as CSV
    echo "$pyversion,$script_name,$method,$mode,$energy_joules,$energy_time,$script_exec_time"
}

# 📝 Write CSV header
echo "PythonVersion,Task,Method,Mode,Joules,Energy_Time,Script_ExecTime" > "$OUTPUT_FILE"

# 🔄 Run all experiments
echo "========================="
echo "🏁 Running Experiments..."
echo "========================="
for scenario in "${scenarios[@]}"; do
  IFS='-' read -ra parts <<< "$scenario"
  pyver="${parts[0]}"
  task="${parts[1]}"
  method="${parts[2]}"
  mode="${parts[3]}"

  # Pick correct script
  script_name=""
  if [[ "$task" == "collatz" ]]; then
    script_name="$COLLATZ_SCRIPT"
  else
    script_name="$MATRIX_SCRIPT"
  fi

  # Run experiment and log results
  data=$(run_experiment "$pyver" "$script_name" "$method" "$mode")
  echo "$data" >> "$OUTPUT_FILE"

  # 💤 Rest 1 min between runs
  echo "⏳ Resting for 1 minute before next run..."
  sleep 60
done

echo "========================="
echo "✅ All runs complete! Results saved in $OUTPUT_FILE"
echo "========================="
