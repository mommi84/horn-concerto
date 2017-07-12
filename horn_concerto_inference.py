#!/usr/bin/env python
"""
Horn Concerto - Inference from Horn rules.
Author: Tommaso Soru <tsoru@informatik.uni-leipzig.de>
Version: 0.0.1
Usage:
    Use test endpoint (DBpedia)
    > python horn_concerto_inference.py <ENDPOINT> <GRAPH_IRI> <RULES_PATH>
"""
import urllib2, urllib, httplib, json
import sys
import pickle
import time
import numpy as np
from joblib import Parallel, delayed
import multiprocessing

reload(sys)
sys.setdefaultencoding("utf-8")

VERSION = "0.0.1"

############################### ARGUMENTS ################################
num_cores = 1 # multiprocessing.cpu_count()
print "Cores: ", num_cores


ENDPOINT = sys.argv[1]
GRAPH = sys.argv[2]
RULES = sys.argv[3]

OUTPUT_FOLDER = "."

############################### FUNCTIONS ################################

def sparql_query(query):
    param = dict()
    param["default-graph-uri"] = GRAPH
    param["query"] = query
    param["format"] = "JSON"
    param["CXML_redir_for_subjs"] = "121"
    param["CXML_redir_for_hrefs"] = ""
    param["timeout"] = "600000" # ten minutes - works with Virtuoso endpoints
    param["debug"] = "on"
    try:
        resp = urllib2.urlopen(ENDPOINT + "?" + urllib.urlencode(param))
        j = resp.read()
        resp.close()
    except (urllib2.HTTPError, httplib.BadStatusLine):
        print "*** Query error. Empty result set. ***"
        j = '{ "results": { "bindings": [] } }'
    sys.stdout.flush()
    return json.loads(j)

def inference():
    files = ["pxy-qxy", "pxy-qyx", "pxy-qxz-rzy", "pxy-qxz-ryz", "pxy-qzx-rzy", "pxy-qzx-ryz"]
    
    # TODO WARNING: in-memory solution - good only for evaluating benchmarks
    predictions = dict()
    
    for t in range(len(files)):
        with open(RULES + "/rules-" + files[t] + ".tsv") as f:
            next(f)
            for line in f:
                line = line[:-1].split('\t')
                weight = float(line[0])
                head = line[1]
                body = list()
                for i in range(len(line[3:])/2):
                    body.append((line[3+i*2], line[4+i*2][1], line[4+i*2][3]))
                # print head, body
                bodies = ""
                for b in body:
                    bodies += "?{} <{}> ?{} . ".format(b[1], b[0], b[2])
                query = "SELECT ?x ?y WHERE { " + bodies + "MINUS { ?x <" + head + "> ?y } }"
                print query
                results = sparql_query(query)
                # print "\t", results
                try:
                    for result in results["results"]["bindings"]:
                        triple = "<{}> <{}> <{}>".format(str(result["x"]["value"]), head, str(result["y"]["value"]))
                        print weight, triple
                        if triple not in predictions:
                            predictions[triple] = list()
                        predictions[triple].append(weight)
                        print predictions[triple]
                except KeyError:
                    pass

    for triple in predictions:
        predictions[triple] = np.mean(predictions[triple])
    
    print "\nPREDICTIONS:"
    with open("inferred_triples.txt", "w") as fout:
        for key, value in sorted(predictions.iteritems(), key=lambda (k,v): (v,k), reverse=True):
            print "%.3f\t%s" % (value, key)
            fout.write("%.3f\t%s\n" % (value, key))


############################### ALGORITHM ################################

print "Horn Concerto v{}".format(VERSION)
print "Endpoint: {}\nGraph: {}\nRules: {}\n".format(ENDPOINT, GRAPH, RULES)

inference()