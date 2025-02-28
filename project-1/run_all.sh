#!/usr/bin/env bash

echo "Starting full automation..."

bash scripts/setup_env.sh
bash scripts/user_upload.sh
bash scripts/experiment.sh
bash scripts/package_results.sh

echo "Experiment fully automated!"
