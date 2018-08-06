#!/usr/bin/env bash
echo "SPARQL CLEAR GRAPH <$1>;" > virtuoso/scriptdel.sql
docker exec virtuoso isql-v 1111 dba dba /usr/local/virtuoso-opensource/var/lib/virtuoso/db/scriptdel.sql
