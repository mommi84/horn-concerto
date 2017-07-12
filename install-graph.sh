#!/usr/bin/env bash
#
#  Usage: [sudo] bash install-graph.sh <NT_FILE> <GRAPH_IRI>
#
cp $1 virtuoso/model-fwc.nt
echo "delete from load_list where ll_file='/opt/virtuoso-opensource/var/lib/virtuoso/db//model-fwc.nt';" > virtuoso/script.sql
echo "ld_dir('/opt/virtuoso-opensource/var/lib/virtuoso/db/', 'model-fwc.nt', '$2');" >> virtuoso/script.sql
echo "rdf_loader_run();" >> virtuoso/script.sql
