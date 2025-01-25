#!/bin/bash

# Check if the script is executed in the correct directory
if [[ -z "$(ls chart*.csv 2>/dev/null)" ]]; then
  echo "No files matching the pattern 'chart*.csv' were found."
  exit 1
fi

# Loop through all files matching the pattern
for file in chart*.csv; do
  # Extract the number between parentheses using a regular expression
  if [[ $file =~ chart\(([0-9]+)\)\.csv ]]; then
    number="${BASH_REMATCH[1]}"
    new_name="${number}h.csv"
    mv "$file" "$new_name"
    echo "Renamed '$file' to '$new_name'"
  fi
done

echo "Renaming complete."
