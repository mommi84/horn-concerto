#!/usr/bin/env python
"""
Horn Concerto - Mining Horn clauses in RDF datasets using SPARQL queries.
Author: Tommaso Soru <tsoru@informatik.uni-leipzig.de>
Version: 0.0.6
Usage:
    Use test endpoint (DBpedia)
    > python horn_concerto.py
    Use with default hyperparameters
    > python horn_concerto.py <ENDPOINT> <GRAPH_IRI>
    Use the current directory as output folder
    > python horn_concerto.py <ENDPOINT> <GRAPH_IRI> <MIN_CONFIDENCE> <TOP_PROPERTIES> <MAX_TRIANGLES>
    Full custom setup
    > python horn_concerto.py <ENDPOINT> <GRAPH_IRI> <MIN_CONFIDENCE> <TOP_PROPERTIES> <MAX_TRIANGLES> <OUTPUT_FOLDER>
"""
import urllib2, urllib, httplib, json
import sys
import pickle
import time
from joblib import Parallel, delayed
import multiprocessing

reload(sys)
sys.setdefaultencoding("utf-8")

VERSION = "0.0.6"

endpoint = None
graph = None
min_confidence = None
n_properties = None
n_triangles = None
output_folder = None

############################### FUNCTIONS ################################

def sort_by_value_desc(d):
    return sorted(d.items(), key=lambda e: e[1], reverse=True)

def sparql_query(query):
    param = dict()
    param["default-graph-uri"] = graph
    param["query"] = query
    param["format"] = "JSON"
    param["CXML_redir_for_subjs"] = "121"
    param["CXML_redir_for_hrefs"] = ""
    param["timeout"] = "600000" # ten minutes - works with Virtuoso endpoints
    param["debug"] = "on"
    try:
        resp = urllib2.urlopen(endpoint + "?" + urllib.urlencode(param))
        j = resp.read()
        resp.close()
    except (urllib2.HTTPError, httplib.BadStatusLine):
        print "*** Query error. Empty result set. ***"
        j = '{ "results": { "bindings": [] } }'
    sys.stdout.flush()
    return json.loads(j)

def simple_rules(q):
    SIMPLE_RULES = "SELECT ?p (COUNT(*) AS ?c) WHERE { ?x ?p ?y . ?x <" + q + "> ?y . FILTER(?p != <" + q + "> ) } GROUP BY ?p ORDER BY DESC(?c)"
    print "Querying:", SIMPLE_RULES
    rules = dict()
    start = time.time()
    results = sparql_query(SIMPLE_RULES)
    print "Time: {}".format(time.time() - start)
    try:
        for result in results["results"]["bindings"]:
            rules[str(result["p"]["value"])] = int(result["c"]["value"])
    except KeyError:
        pass
    print "Result:", rules
    return rules

def type_two_rules(q):
    TYPE_2_RULES = "SELECT ?p (COUNT(*) AS ?c) WHERE { ?y ?p ?x . ?x <" + q + "> ?y } GROUP BY ?p ORDER BY DESC(?c)"
    print "Querying:", TYPE_2_RULES
    rules = dict()
    start = time.time()
    results = sparql_query(TYPE_2_RULES)
    print "Time: {}".format(time.time() - start)
    try:
        for result in results["results"]["bindings"]:
            rules[str(result["p"]["value"])] = int(result["c"]["value"])
    except KeyError:
        pass
    print "Result:", rules
    return rules

def top_properties():
    TOP_PROPERTIES = 'SELECT ?q (COUNT(*) AS ?c) WHERE { [] ?q [] } GROUP BY ?q ORDER BY DESC(?c) LIMIT ' + str(n_properties)
    print "Querying:", TOP_PROPERTIES
    tp = dict()
    results = sparql_query(TOP_PROPERTIES)
    try:
        for result in results["results"]["bindings"]:
            tp[str(result["q"]["value"])] = int(result["c"]["value"])
    except KeyError:
        pass
    print "Result:", tp
    return tp
    
def triangles(t, p):
    tri = [["?x ?q ?z", "?z ?r ?y"], ["?x ?q ?z", "?y ?r ?z"], ["?z ?q ?x", "?z ?r ?y"], ["?z ?q ?x", "?y ?r ?z"]]
    TRIANGLES = 'SELECT ?q ?r (COUNT(*) AS ?c) WHERE { ' + tri[t][0] + ' . ' + tri[t][1] + ' . ?x <' + p + '> ?y } GROUP BY ?q ?r ORDER BY DESC(?c) LIMIT ' + str(n_triangles)
    print "Querying:", TRIANGLES
    rules = dict()
    start = time.time()
    results = sparql_query(TRIANGLES)
    print "Time: {}".format(time.time() - start)
    try:
        for result in results["results"]["bindings"]:
            rules[(str(result["q"]["value"]), str(result["r"]["value"]))] = int(result["c"]["value"])
    except KeyError:
        pass
    print "Result:", rules
    return rules    

def adjacencies(t, k):
    nodes = ["xzzy", "xzyz", "zxzy", "zxyz"]
    ADJACENCIES = 'SELECT (COUNT(*) AS ?c) WHERE { ?' + nodes[t][0] + ' <' + k[0] + '> ?' + nodes[t][1] + ' . ?' + nodes[t][2] + ' <' + k[1] + '> ?' + nodes[t][3] + ' }'
    print "Querying:", ADJACENCIES
    start = time.time()
    results = sparql_query(ADJACENCIES)
    print "Time: {}".format(time.time() - start)
    try:
        res = results["results"]["bindings"]
    except KeyError:
        return 0
    if len(res) == 0:
        return 0
    else:
        return res[0]["c"]["value"]

def write_rule(t, c, p, q):
    files = ["pxy-qxy", "pxy-qyx"]
    args = ["(x,y)", "(y,x)"]
    worth = False
    with open("{}/rules-{}.tsv".format(output_folder, files[t]), 'a') as f:
        if c > min_confidence:
            f.write("{}\t{}\t(x,y)\t{}\t{}\n".format(c, p, q, args[t]))
            worth = True
    return worth

def write_rule_3(t, c, p, q, r):
    files = ["pxy-qxz-rzy", "pxy-qxz-ryz", "pxy-qzx-rzy", "pxy-qzx-ryz"]
    args = [["(x,z)", "(z,y)"], ["(x,z)", "(y,z)"], ["(z,x)", "(z,y)"], ["(z,x)", "(y,z)"]]
    worth = False
    with open("{}/rules-{}.tsv".format(output_folder, files[t]), 'a') as f:
        if c > min_confidence:
            f.write("{}\t{}\t(x,y)\t{}\t{}\t{}\t{}\n".format(c, p, q, args[t][0], r, args[t][1]))
            worth = True
    return worth

def write_titles():
    print "output_folder:", output_folder
    files = ["pxy-qxy", "pxy-qyx", "pxy-qxz-rzy", "pxy-qxz-ryz", "pxy-qzx-rzy", "pxy-qzx-ryz"]
    for t in range(len(files)):
        if t < 2:
            with open("{}/rules-{}.tsv".format(output_folder, files[t]), 'w') as f:
                f.write(unicode("weight\tp\t(?,?)\tq\t(?,?)\n"))
        else:
            with open("{}/rules-{}.tsv".format(output_folder, files[t]), 'w') as f:
                f.write(unicode("weight\tp\t(?,?)\tq\t(?,?)\tr\t(?,?)\n"))

types = [
    "I: p(x,y) <= q(x,y)", 
    "II: p(x,y) <= q(y,x)", 
    "III: p(x,y) <= q(x,z), r(z,y)", 
    "IV: p(x,y) <= q(x,z), r(y,z)", 
    "V: p(x,y) <= q(z,x), r(z,y)", 
    "VI: p(x,y) <= q(z,x), r(y,z)"]
body = [
    "(x,y)", 
    "(y,x)", 
    ("(x,z)", "(z,y)"), 
    ("(x,z)", "(y,z)"), 
    ("(z,x)", "(z,y)"), 
    ("(z,x)", "(y,z)")]

# outer loop
def rangeTypes(i, tp):
    print "Rules of type", types[i]
    # there might exist p_1,p_2 such that: p_i(x,y) <= q(?,?), r(?,?)
    # shared dictionary
    adj_dict = dict()
    # inner loop
    for tp_key, tp_val in sort_by_value_desc(tp):
        print "Processing:", tp_key, tp_val
        if i < 2: # p-q rules
            if i == 0: # p(x,y) <= q(x,y)
                r = simple_rules(tp_key)
            else: # p(x,y) <= q(y,x)
                r = type_two_rules(tp_key)
            for r_key, r_val in sort_by_value_desc(r):
                print r_key, r_val
                print "*** RULE FOUND! ***",
                c = float(r_val) / float(tp_val)
                print "c = {}\t{} (x,y) <= {} {}".format(c, r_key, tp_key, body[i])
                worth = write_rule(i, c, r_key, tp_key)
                if not worth:
                    break
        else: # p-q-r rules
            j = i - 2 # p-q-r rule index
            triang = triangles(j, tp_key)
            for k, v in sort_by_value_desc(triang):
                print k, v
                if k in adj_dict:
                    print "Value found in dictionary:", k
                    adj = adj_dict[k]
                else:
                    adj = adjacencies(j, k)
                if adj == 0:
                    continue
                c = float(v) / float(adj)
                print "*** RULE FOUND! ***"
                print "c = {}\t{} (x,y) <= {} {} ^ {} {}".format(c, tp_key, k[0], body[i][0], k[1], body[i][1])
                worth = write_rule_3(j, c, tp_key, k[0], k[1])
                if not worth:
                    break
                adj_dict[k] = adj

############################### ALGORITHM ################################

def run(endpoint_P, graph_P, min_confidence_P, n_properties_P, n_triangles_P, output_folder_P):
    
    global endpoint, graph, min_confidence, n_properties, n_triangles, output_folder
    
    endpoint = endpoint_P
    graph = graph_P
    min_confidence = min_confidence_P
    n_properties = n_properties_P
    n_triangles = n_triangles_P
    output_folder = output_folder_P
    
    print "Horn Concerto v{}".format(VERSION)
    print "Endpoint: {}\nGraph: {}\nMin_Confidence: {}\nN_Properties: {}\nN_Triangles: {}\nOutput_Folder: {}\n".format(endpoint, graph, min_confidence, n_properties, n_triangles, output_folder)
    num_cores = multiprocessing.cpu_count()
    print "Cores:", num_cores
    
    write_titles()

    tp = top_properties()

    # Making outer loop Parallel
    Parallel(n_jobs=num_cores)(delayed(rangeTypes)(i=iElem, tp=tp) for iElem in range(len(types)))

    print "Done."
    print "\nRules saved in files {}/rules-*.tsv".format(output_folder)

if __name__ == '__main__':
    
############################### ARGUMENTS ################################
    if len(sys.argv) < 2:
        endpoint = "http://dbpedia.org/sparql"
        graph = "http://dbpedia.org"
    else:
        endpoint = sys.argv[1]
        graph = sys.argv[2]

    if len(sys.argv) < 4:
        min_confidence = 0.001
        n_properties = 100
        n_triangles = 10
    else:
        min_confidence = float(sys.argv[3])
        n_properties = int(sys.argv[4])
        n_triangles = int(sys.argv[5])
    
    if len(sys.argv) < 7:
        output_folder = "."
    else:
        output_folder = sys.argv[6]
    
    run(endpoint, graph, min_confidence, n_properties, n_triangles, output_folder)
