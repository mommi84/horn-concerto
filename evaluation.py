#!/usr/bin/env python
"""
Horn Concerto - Evaluation for inference.
Author: Tommaso Soru <tsoru@informatik.uni-leipzig.de>
Version: 0.1.0
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

VERSION = "0.1.0"

############################### ARGUMENTS ################################
num_cores = multiprocessing.cpu_count()
print "Cores: ", num_cores

TEST_SET = sys.argv[1]
INFERRED = sys.argv[2]

test = list()
# index test set
with open(TEST_SET) as f:
    for line in f:
        test.append(line[:-3])

def range_test(t):
    t_triple = t.split(' ')
    corr_obj = "{} {}".format(t_triple[0], t_triple[1])
    corr_sub = "{} {}".format(t_triple[1], t_triple[2])
    # collect appearances of corr_obj and corr_sub in inferred, sorted by confidence value
    conf = list()
    t_conf = None
    # print "testing triple: {}".format(t)
    with open(INFERRED) as f:
        for line in f:
            if t in line:
                t_conf = float(line[:-1].split('\t')[0])
                continue
            if corr_obj in line or corr_sub in line:
                temp = line[:-1].split('\t')
                i_conf = float(temp[0])
                i_triple = temp[1]
                if i_triple not in test:
                    conf.append(i_conf)
    if t_conf is None:
        rr = 1.0 / len(test)
        return rr, 0, 0, 0
    pos = 1
    for c in conf:
        if t_conf < c:
            pos += 1
    # print "t_conf: {}".format(t_conf)
    # print "conf: {}".format(conf)
    # print "pos: {}".format(pos)
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
STEP = 50 * num_cores

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
