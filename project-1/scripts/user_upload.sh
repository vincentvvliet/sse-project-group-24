#!/usr/bin/env bash

BENCHMARK_DIR="benchmarks/"
UPLOAD_DIR="user_benchmarks/"

mkdir -p "$BENCHMARK_DIR"
mkdir -p "$UPLOAD_DIR"

echo "Please upload your benchmark script(s) to '$UPLOAD_DIR'."
echo "Detecting uploaded scripts..."

for script in "$UPLOAD_DIR"/*.py; do
    if [[ -f "$script" ]]; then
        echo "📜 Found: $script"
        mv "$script" "$BENCHMARK_DIR"
        chmod +x "$BENCHMARK_DIR/$(basename "$script")"
    fi
done

echo "All uploaded scripts moved to $BENCHMARK_DIR"
