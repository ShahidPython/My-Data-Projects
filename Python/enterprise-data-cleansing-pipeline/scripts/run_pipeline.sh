#!/bin/bash
set -e

INPUT_FILE=${1:-"data/input/transactions_dirty.csv"}
OUTPUT_DIR=${2:-"data/output"}
CONFIG_FILE=${3:-"config/cleaning_rules.json"}
LOG_LEVEL=${4:-"INFO"}

echo "🔧 Starting data cleaning pipeline..."
echo "Input: ${INPUT_FILE}"
echo "Output: ${OUTPUT_DIR}"
echo "Config: ${CONFIG_FILE}"

# Validate input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "❌ Input file not found: ${INPUT_FILE}"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"
mkdir -p "logs"

# Run the pipeline
python main.py \
    --input "$INPUT_FILE" \
    --output "$OUTPUT_DIR" \
    --config "$CONFIG_FILE" \
    --log-level "$LOG_LEVEL" \
    --validate \
    --archive

# Check exit code
if [ $? -eq 0 ]; then
    echo "✅ Pipeline completed successfully"
    echo "📊 Results saved to: ${OUTPUT_DIR}"
    
    # Show summary
    if [ -f "${OUTPUT_DIR}/summary.json" ]; then
        echo "📈 Summary:"
        cat "${OUTPUT_DIR}/summary.json" | python -m json.tool
    fi
else
    echo "❌ Pipeline failed"
    exit 1
fi