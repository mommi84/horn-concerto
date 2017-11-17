#!/usr/bin/env bash
#
#  Usage: [sudo] bash install-graph.sh <NT_FILE> <GRAPH_IRI> [FILE_TYPE]
#
cp $1 virtuoso/model-fwc.${3:-nt}
echo "delete from load_list where ll_file='/usr/local/virtuoso-opensource/var/lib/virtuoso/db//model-fwc.${3:-nt}';" > virtuoso/script.sql
echo "ld_dir('/usr/local/virtuoso-opensource/var/lib/virtuoso/db/', 'model-fwc.${3:-nt}', '$2');" >> virtuoso/script.sql
echo "rdf_loader_run();" >> virtuoso/script.sql
