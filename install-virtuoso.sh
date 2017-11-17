#!/usr/bin/env bash
mkdir virtuoso
wget https://raw.githubusercontent.com/tenforce/docker-virtuoso/master/virtuoso.ini -O virtuoso/virtuoso.ini
docker run --name virtuoso -d -v `pwd`/virtuoso:/usr/local/virtuoso-opensource/var/lib/virtuoso/db -t -p 1111:1111 -p 8890:8890 -i tenforce/virtuoso
