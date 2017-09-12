#!/usr/bin/env bash
echo "Querying endpoint: $1"
echo "Graph: $2"
echo "Log file: $3"
echo "Performing rule mining..."
python horn_concerto_parallel.py $1 $2 >> $3
echo "Performing inference..."
python horn_concerto_inference.py $1 $2 . >> $3
echo "Saved inferred triples and confidence values to 'inferred_triples.txt'"
