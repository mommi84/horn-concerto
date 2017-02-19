#!/usr/bin/env bash
#
#  Usage: [sudo] bash install-graph.sh <NT_FILE> <GRAPH_IRI>
#
cp $1 horn-concerto/virtuoso/model-fwc.nt
echo "delete from load_list where ll_file='/opt/virtuoso-opensource/var/lib/virtuoso/db//model-fwc.nt';" > horn-concerto/virtuoso/script.sql
echo "ld_dir('/opt/virtuoso-opensource/var/lib/virtuoso/db/', 'model-fwc.nt', '$2');" >> horn-concerto/virtuoso/script.sql
echo "rdf_loader_run();" >> horn-concerto/virtuoso/script.sql
