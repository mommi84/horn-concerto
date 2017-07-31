#!/usr/bin/env bash
mkdir virtuoso
wget https://raw.githubusercontent.com/fusepoolP3/virtuoso-docker/master/virtuoso.ini.template -O virtuoso/virtuoso.ini
docker run --name virtuoso -d -v `pwd`/virtuoso:/opt/virtuoso-opensource/var/lib/virtuoso/db -t -p 1111:1111 -p 8890:8890 -i tenforce/virtuoso
