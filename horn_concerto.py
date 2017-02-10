#!/usr/bin/env python
"""
Horn Concerto - Mining horn clauses in RDF datasets using SPARQL queries.
Author: Tommaso Soru <tsoru@informatik.uni-leipzig.de>
"""
import urllib2, urllib, httplib, json
import sys
import pickle
import time

reload(sys)
sys.setdefaultencoding("utf-8")

if len(sys.argv) < 2:
    ENDPOINT = "http://dbpedia.org/sparql"
    GRAPH = "http://dbpedia.org"
else:
    ENDPOINT = sys.argv[1]
    GRAPH = sys.argv[2]

# ENDPOINT = "http://localhost:8890/sparql"
# GRAPH = "http://linkedmdb.org"

if len(sys.argv) < 4:
    MIN_CONFIDENCE = 0.001
    N_PROPERTIES = 100
    N_TRIANGLES = 10
else:
    MIN_CONFIDENCE = float(sys.argv[3])
    N_PROPERTIES = int(sys.argv[4])
    N_TRIANGLES = int(sys.argv[5])

def sort_by_value_desc(d):
    return sorted(d.items(), key=lambda e: e[1], reverse=True)

def sparql_query(query):
    param = dict()
    param["default-graph-uri"] = GRAPH
    param["query"] = query
    param["format"] = "JSON"
    param["CXML_redir_for_subjs"] = "121"
    param["CXML_redir_for_hrefs"] = ""
    param["timeout"] = "300000"
    param["debug"] = "on"
    try:
        resp = urllib2.urlopen(ENDPOINT + "?" + urllib.urlencode(param))
        j = resp.read()
        resp.close()
    except (urllib2.HTTPError, httplib.BadStatusLine):
        print "*** Query error. Empty result set. ***"
        j = '{ "results": { "bindings": [] } }'
    return json.loads(j)

def simple_rules(q):
    SIMPLE_RULES = "SELECT ?p (COUNT(*) AS ?c) WHERE { ?x ?p ?y . ?x <" + q + "> ?y . FILTER(?p != <" + q + "> ) } GROUP BY ?p ORDER BY DESC(?c)"
    print "Querying:", SIMPLE_RULES
    rules = dict()
    start = time.time()
    results = sparql_query(SIMPLE_RULES)
    print "Time: {}".format(time.time() - start)
    for result in results["results"]["bindings"]:
        rules[str(result["p"]["value"])] = int(result["c"]["value"])
    print "Result:", rules
    return rules

def type_two_rules(q):
    TYPE_2_RULES = "SELECT ?p (COUNT(*) AS ?c) WHERE { ?y ?p ?x . ?x <" + q + "> ?y } GROUP BY ?p ORDER BY DESC(?c)"
    print "Querying:", TYPE_2_RULES
    rules = dict()
    start = time.time()
    results = sparql_query(TYPE_2_RULES)
    print "Time: {}".format(time.time() - start)
    for result in results["results"]["bindings"]:
        rules[str(result["p"]["value"])] = int(result["c"]["value"])
    print "Result:", rules
    return rules

def top_properties():
    TOP_PROPERTIES = 'SELECT ?q (COUNT(*) AS ?c) WHERE { [] ?q [] } GROUP BY ?q ORDER BY DESC(?c) LIMIT ' + str(N_PROPERTIES)
    print "Querying:", TOP_PROPERTIES
    tp = dict()
    results = sparql_query(TOP_PROPERTIES)
    for result in results["results"]["bindings"]:
        tp[str(result["q"]["value"])] = int(result["c"]["value"])
    print "Result:", tp
    return tp
    
def triangles(t, p):
    tri = [["?x ?q ?z", "?z ?r ?y"], ["?x ?q ?z", "?y ?r ?z"], ["?z ?q ?x", "?z ?r ?y"], ["?z ?q ?x", "?y ?r ?z"]]
    TRIANGLES = 'SELECT ?q ?r (COUNT(*) AS ?c) WHERE { ' + tri[t][0] + ' . ' + tri[t][1] + ' . ?x <' + p + '> ?y } GROUP BY ?q ?r ORDER BY DESC(?c) LIMIT ' + str(N_TRIANGLES)
    print "Querying:", TRIANGLES
    rules = dict()
    start = time.time()
    results = sparql_query(TRIANGLES)
    print "Time: {}".format(time.time() - start)
    for result in results["results"]["bindings"]:
        rules[(str(result["q"]["value"]), str(result["r"]["value"]))] = int(result["c"]["value"])
    print "Result:", rules
    return rules    

def adjacencies(t, k):
    nodes = ["xzzy", "xzyz", "zxzy", "zxyz"]
    ADJACENCIES = 'SELECT (COUNT(*) AS ?c) WHERE { ?' + nodes[t][0] + ' <' + k[0] + '> ?' + nodes[t][1] + ' . ?' + nodes[t][2] + ' <' + k[1] + '> ?' + nodes[t][3] + ' }'
    print "Querying:", ADJACENCIES
    start = time.time()
    results = sparql_query(ADJACENCIES)
    print "Time: {}".format(time.time() - start)
    res = results["results"]["bindings"]
    if len(res) == 0:
        return 0
    else:
        return res[0]["c"]["value"]

def write_rule(t, c, p, q):
    files = ["pxy-qxy", "pxy-qyx"]
    args = ["(x,y)", "(y,x)"]
    worth = False
    with open("rules-{}.tsv".format(files[t]), 'a') as f:
        if c > MIN_CONFIDENCE:
            f.write("{}\t{}\t(x,y)\t{}\t{}\n".format(c, p, q, args[t]))
            worth = True
    return worth

def write_rule_3(t, c, p, q, r):
    files = ["pxy-qxz-rzy", "pxy-qxz-ryz", "pxy-qzx-rzy", "pxy-qzx-ryz"]
    args = [["(x,z)", "(z,y)"], ["(x,z)", "(y,z)"], ["(z,x)", "(z,y)"], ["(z,x)", "(y,z)"]]
    worth = False
    with open("rules-{}.tsv".format(files[t]), 'a') as f:
        if c > MIN_CONFIDENCE:
            f.write("{}\t{}\t(x,y)\t{}\t{}\t{}\t{}\n".format(c, p, q, args[t][0], r, args[t][1]))
            worth = True
    return worth

def write_titles():
    files = ["pxy-qxy", "pxy-qyx", "pxy-qxz-rzy", "pxy-qxz-ryz", "pxy-qzx-rzy", "pxy-qzx-ryz"]
    for t in range(len(files)):
        if t < 2:
            with open("rules-{}.tsv".format(files[t]), 'w') as f:
                f.write(unicode("weight\tp\t(?,?)\tq\t(?,?)\n"))
        else:
            with open("rules-{}.tsv".format(files[t]), 'w') as f:
                f.write(unicode("weight\tp\t(?,?)\tq\t(?,?)\tr\t(?,?)\n"))

write_titles()

tp = top_properties()
# pickle.dump(tp, open("top_prop.pkl", "wb")) # debug only
# tp = pickle.load(open("top_prop.pkl", "rb")) # debug only

# p(x,y) <= q(x,y)
print "Rules of type I: p(x,y) <= q(x,y)"
i = 0
for tp_key, tp_val in sort_by_value_desc(tp):
    i += 1
    if i < 11:
        continue
    print "Processing:", tp_key, tp_val
    r = simple_rules(tp_key)
    for r_key, r_val in sort_by_value_desc(r):
        print r_key, r_val
        print "*** RULE FOUND! ***",
        c = float(r_val) / float(tp_val)
        print "c = {}\t{} (x,y) <= {} (x,y)".format(c, r_key, tp_key)
        # output rule as p(x,y) <= q(x,y)
        worth = write_rule(0, c, r_key, tp_key)
        if not worth:
            break
    print "-----"

# p(x,y) <= q(y,x)
print "Rules of type II: p(x,y) <= q(y,x)"
j = 0 # TODO remove me
for tp_key, tp_val in sort_by_value_desc(tp):
    j += 1
    if j < 8:
        continue
    print "Processing:", tp_key, tp_val
    r = type_two_rules(tp_key)
    for r_key, r_val in sort_by_value_desc(r):
        print r_key, r_val
        print "*** RULE FOUND! ***",
        c = float(r_val) / float(tp_val)
        print "c = {}\t{} (x,y) <= {} (y,x)".format(c, r_key, tp_key)
        # output rule as p(x,y) <= q(y,x)
        write_rule(1, c, tp_key, r_key)
    print "-----"

# adj_dict: there might exist p_1,p_2 such that: p_i(x,y) <= q(?,?), r(?,?)

# p(x,y) <= q(x,z), r(z,y) | forward-forward | x->z->y
print "Rules of type III: p(x,y) <= q(x,z), r(z,y)"
adj_dict = dict()
for tp_key, tp_val in sort_by_value_desc(tp):
    print "Processing:", tp_key
    triang = triangles(0, tp_key)
    for k, v in sort_by_value_desc(triang):
        print k, v
        if k in adj_dict:
            print "Value found in dictionary:", k
            adj = adj_dict[k]
        else:
            adj = adjacencies(0, k)
        if adj == 0:
            continue
        c = float(v) / float(adj)
        print "*** RULE FOUND! ***"
        print "c = {}\t{} (x,y) <= {} (x,z) ^ {} (z,y)".format(c, tp_key, k[0], k[1])
        write_rule_3(0, c, tp_key, k[0], k[1])
        adj_dict[k] = adj
adj_dict.clear()

# p(x,y) <= q(x,z), r(y,z) | forward-backward | x->z<-y
print "Rules of type IV: p(x,y) <= q(x,z), r(y,z)"
adj_dict = dict()
for tp_key, tp_val in sort_by_value_desc(tp):
    print "Processing:", tp_key
    triang = triangles(1, tp_key)
    for k, v in sort_by_value_desc(triang):
        print k, v
        if k in adj_dict:
            print "Value found in dictionary:", k
            adj = adj_dict[k]
        else:
            adj = adjacencies(1, k)
        if adj == 0:
            continue
        c = float(v) / float(adj)
        print "*** RULE FOUND! ***"
        print "c = {}\t{} (x,y) <= {} (x,z) ^ {} (y,z)".format(c, tp_key, k[0], k[1])
        write_rule_3(1, c, tp_key, k[0], k[1])
        adj_dict[k] = adj
adj_dict.clear()

# p(x,y) <= q(z,x), r(z,y) | backward-forward | x<-z->y
print "Rules of type V: p(x,y) <= q(z,x), r(z,y)"
adj_dict = dict()
for tp_key, tp_val in sort_by_value_desc(tp):
    print "Processing:", tp_key
    triang = triangles(2, tp_key)
    for k, v in sort_by_value_desc(triang):
        print k, v
        if k in adj_dict:
            print "Value found in dictionary:", k
            adj = adj_dict[k]
        else:
            adj = adjacencies(2, k)
        if adj == 0:
            continue
        c = float(v) / float(adj)
        print "*** RULE FOUND! ***"
        print "c = {}\t{} (x,y) <= {} (z,x) ^ {} (z,y)".format(c, tp_key, k[0], k[1])
        write_rule_3(2, c, tp_key, k[0], k[1])
        adj_dict[k] = adj
adj_dict.clear()

# p(x,y) <= q(z,x), r(y,z) | backward-backward | x<-z<-y
print "Rules of type VI: p(x,y) <= q(z,x), r(y,z)"
adj_dict = dict()
for tp_key, tp_val in sort_by_value_desc(tp):
    print "Processing:", tp_key
    triang = triangles(3, tp_key)
    for k, v in sort_by_value_desc(triang):
        print k, v
        if k in adj_dict:
            print "Value found in dictionary:", k
            adj = adj_dict[k]
        else:
            adj = adjacencies(3, k)
        if adj == 0:
            continue
        c = float(v) / float(adj)
        print "*** RULE FOUND! ***"
        print "c = {}\t{} (x,y) <= {} (z,x) ^ {} (y,z)".format(c, tp_key, k[0], k[1])
        write_rule_3(3, c, tp_key, k[0], k[1])
        adj_dict[k] = adj
adj_dict.clear()

print "Done."
