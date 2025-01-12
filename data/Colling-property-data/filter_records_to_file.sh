#!/bin/bash

# Check if the input file is provided
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <input_file> <output_file>"
  exit 1
fi

input_file="$1"
output_file="$2"

# Create or overwrite the output file with the first line of the input file
head -n 1 "$input_file" > "$output_file"

# Append lines containing "75024" to the output file
grep "75024" "$input_file" >> "$output_file"

echo "Filtered records saved to $output_file"
