#!/usr/bin/env bash
echo "Loading graph into Virtuoso..."
bash delete-graph.sh http://hornconcerto.org/example > /dev/null
bash install-graph.sh $1 http://hornconcerto.org/example > /dev/null
bash install-graph-exec.sh > /dev/null
echo "Performing rule mining..."
python horn_concerto_parallel.py http://localhost:8890/sparql http://hornconcerto.org/example > /dev/null
echo "Performing inference..."
python horn_concerto_inference.py http://localhost:8890/sparql http://hornconcerto.org/example . 
echo "Saved inferred triples and confidence values to 'inferred_triples.txt'"
