#!/bin/bash

echo "| Run | Significance | Recommendation | Current | New Range | Confidence | Risk |"
echo "|-----|-------------|----------------|---------|-----------|------------|------|"

for i in 1 2 3 4 5 6; do
    file="consistency_tests/run_${i}.txt"

    sig=$(grep "Overall Significance:" "$file" | awk '{print $NF}')
    rec=$(grep "YES\|NO" "$file" | grep "Re-evaluation" | head -1 | awk '{print $1}')
    current=$(grep "Current Level:" "$file" | head -1 | awk '{print $NF}')
    newrange=$(grep "Expected New Range:" "$file" | head -1 | cut -d: -f2 | xargs)
    conf=$(grep "Confidence:" "$file" | head -1 | awk '{print $NF}')
    risk=$(grep "Risk Assessment:" "$file" | awk '{print $NF}')

    echo "| $i | $sig | $rec | $current | $newrange | $conf | $risk |"
done
