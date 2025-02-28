#!/usr/bin/env bash

# Directories
BENCHMARK_DIR="benchmarks"
ENERGIBRIDGE="Energibridge/target/release/energibridge"
RESULTS_DIR="results"
LOG_FILE="$RESULTS_DIR/execution_logs.txt"
TOTAL_RUNS=30  
REST_TIME=60  

mkdir -p "$RESULTS_DIR/Python3.11"
mkdir -p "$RESULTS_DIR/Python3.14"


exec > >(tee -a "$LOG_FILE") 2>&1

echo "⚙️ Increasing script priority..."
sudo renice -n -20 -p $$ >/dev/null

echo "   Entering Zen Mode..."
echo "   Close all applications, disable notifications, and unplug unnecessary devices."
echo "   Ensure stable room temperature."
echo "   If possible, disable network access for consistency."
sleep 5  

echo "Warming up CPU for 1 minute..."
end_time=$(( $(date +%s) + 60 ))
while [ "$(date +%s)" -lt "$end_time" ]; do
    python3 -c "x = [i*i for i in range(10**6)]"
done
echo "Warm-up complete!"

if [[ ! -d "$BENCHMARK_DIR" ]]; then
    echo "Error: Benchmark directory not found at $BENCHMARK_DIR"
    exit 1
fi

BENCHMARK_SCRIPTS=($(ls "$BENCHMARK_DIR"/*.py 2>/dev/null))
PYTHON_VERSIONS=("python3.11" "python3.14")
MODES=("normal" "optimized")


run_experiment() {
    local pyversion=$1
    local mode=$2
    local script=$3
    local run=$4

    if [[ ! -f "$script" ]]; then
        echo "Error: Script $script not found!"
        return
    fi

    script_name=$(basename "$script")  

   
    local output_dir="${RESULTS_DIR}/${pyversion}"
    mkdir -p "$output_dir"

   
    local result_file="${output_dir}/energy_${script_name}_${pyversion}_${mode}_run${run}.csv"
    local summary_file="${output_dir}/energybridge_output_${script_name}_${pyversion}_${mode}_run${run}.txt"

    echo "▶️ Running $script_name with $pyversion ($mode mode) - Run $run..."

    # Determine python command
    if [[ "$mode" == "optimized" ]]; then
        python_cmd="env PYTHONOPTIMIZE=2 $pyversion"
    else
        python_cmd="$pyversion"
    fi

    
    if [[ ! -x "$ENERGIBRIDGE" ]]; then
        echo "Error: EnergiBridge not found or not executable at $ENERGIBRIDGE"
        return
    fi

    
    sudo "$ENERGIBRIDGE" -o "$result_file" --summary sleep 20 > "$summary_file" 2>&1 &
    ENERGY_PID=$!
    sleep 1

    
    local end_time=$(( $(date +%s) + 20 ))
    while [ "$(date +%s)" -lt "$end_time" ]; do
        $python_cmd "$script" >/dev/null
    done

    wait "$ENERGY_PID"

   
    echo "⏸ Resting for $REST_TIME seconds..."
    sleep "$REST_TIME"
}

for pyversion in "${PYTHON_VERSIONS[@]}"; do
    for mode in "${MODES[@]}"; do
        for script in "${BENCHMARK_SCRIPTS[@]}"; do
            
            # Generate a **shuffled** list of unique run numbers
            run_numbers=($(seq 1 $TOTAL_RUNS | sort -R))

            # Execute the shuffled 30 runs **without duplicates**
            for run in "${run_numbers[@]}"; do
                run_experiment "$pyversion" "$mode" "$script" "$run"
            done
        done
    done
done

echo "All runs complete! Results saved in $RESULTS_DIR"
