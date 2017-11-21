#!/usr/bin/env python
"""
Horn Concerto - Evaluation for inference.
Author: Tommaso Soru <tsoru@informatik.uni-leipzig.de>
Version: 0.0.6
Usage:
    Use test endpoint (DBpedia)
    > python evaluation.py <TEST_SET> <INFERRED_TRIPLES>
"""
import sys
from joblib import Parallel, delayed
import numpy as np
import multiprocessing

reload(sys)
sys.setdefaultencoding("utf-8")

VERSION = "0.0.6"

############################### ARGUMENTS ################################
num_cores = multiprocessing.cpu_count()
print "Cores: ", num_cores

TEST_SET = sys.argv[1]
INFERRED = sys.argv[2]

inferred = list()
with open(INFERRED) as f:
    for line in f:
        line = line[:-1].split('\t')
        inferred.append(line)

test = list()

def evaluate(t):
    # corrupted
    t_triple = t.split(' ')
    corr_obj = "{} {}".format(t_triple[0], t_triple[1])
    corr_sub = "{} {}".format(t_triple[1], t_triple[2])
    pos = 1
    for line in inferred:
        tpl = line[1]
        if t == tpl:
            return pos
        triple = tpl.split(' ')
        if corr_obj in tpl:
            # filter out if true
            if not line[1] in test:
                pos += 1            
        elif corr_sub in tpl:
            # filter out if true
            if not tpl in test:
                pos += 1
    return None

# index test set
with open(TEST_SET) as f:
    for line in f:
        line = line[:-1].split(' ')
        test.append(line[0] + " " + line[1] + " " + line[2])

def range_test(t):
    pos = evaluate(t)
    # print "{}\n\t{}".format(t, pos)
    if pos is None:
        rr = 1.0 / len(test)
        return rr, 0, 0, 0
    rr = 1.0 / pos
    h1 = 0; h3 = 0; h10 = 0
    if pos <= 10:
        h10 = 1
        if pos <= 3:
            h3 = 1
            if pos <= 1:
                h1 = 1
    return rr, h1, h3, h10

rr, h1, h3, h10, n = 0, 0, 0, 0, 0
mrr, hitsAt1, hitsAt3, hitsAt10 = 0, 0, 0, 0

STEP = 500 * num_cores

for i in range(len(test)):
    if i % STEP == 0:
        start = i / STEP
        result = Parallel(n_jobs=num_cores)(delayed(range_test)(t=t) for t in test[i:i+STEP])
        print "len=",len(result)
        rr, h1, h3, h10 = np.sum(result, axis=0) + (rr, h1, h3, h10)
        n = n + len(result)
        mrr = rr / n
        hitsAt1 = float(h1) / n
        hitsAt3 = float(h3) / n
        hitsAt10 = float(h10) / n
        print "adding range {} to {}".format(i, i+STEP)
        print "|test| = {}".format(n)
        print "MRR = {}".format(mrr)
        print "Hits@1 = {}".format(hitsAt1)
        print "Hits@3 = {}".format(hitsAt3)
        print "Hits@10 = {}".format(hitsAt10)

print "\nFINAL RESULTS"
print "|test| = {}".format(len(test))
print "MRR = {}".format(mrr)
print "Hits@1 = {}".format(hitsAt1)
print "Hits@3 = {}".format(hitsAt3)
print "Hits@10 = {}".format(hitsAt10)
print "{}\t{}\t{}\t{}".format(mrr, hitsAt1, hitsAt3, hitsAt10)
