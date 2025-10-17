#!/bin/bash

# Exit on any error
set -e

echo "Running Locust load test..."

# Run locust in headless mode (no UI)
locust -f benchmarks/locustfile.py \
    --host=http://localhost:8000 \
    --headless \
    --users=2 \
    --spawn-rate=15 \
    --run-time=1m \
    --csv=benchmarks/load_test_results

echo "Locust load test completed!"
