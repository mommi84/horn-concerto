#!/usr/bin/env bash
echo "SPARQL CLEAR GRAPH <$1>;" > virtuoso/scriptdel.sql
docker exec virtuoso /opt/virtuoso-opensource/bin/isql 1111 dba dba /opt/virtuoso-opensource/var/lib/virtuoso/db/scriptdel.sql
