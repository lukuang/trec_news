"""
get the optimal ndcg from the results prior to merging
"""

import os
import json
import sys
import re
import argparse
import codecs
import math

def get_idcgs(qrels):
    idcgs = {}
    for qid in qrels:
        rels = qrels[qid].values()
        rels.sort(reverse=True)
        idcgs[qid] = .0
        for i in xrange(5):
            idcgs[qid] += rels[i]* 1.0 / math.log(i+2, 2) 
    return idcgs

def read_qrel(qrel_file):
    qrels = {}
    with open(qrel_file) as f:
        for line in f:
            line = line.strip()
            cols = line.split()
            qid = cols[0]
            docid = cols[2]
            rel = int(cols[-1])
            if qid not in qrels:
                qrels[qid] = {}
            qrels[qid][docid] = rel
    return qrels

def get_results(result_dir, merge_cutoff):
    results = {}
    old_pid = None
    line_num = 0
    for qid in os.listdir(result_dir):
        results[qid] = []
        q_result_file = os.path.join(result_dir,qid)
        with open(q_result_file) as f:
            for line in f:
                cols = line.split()
                pid = cols[0]
                docid = cols[2]
                if pid != old_pid:
                    old_pid = pid
                    line_num = 1
                    results[qid].append(docid)
                else:
                    if line_num == merge_cutoff:
                        continue
                    else:
                        line_num += 1
                        results[qid].append(docid)
        results[qid] = list(set(results[qid]))

    return results


def get_optimal_dcgs(results, qrels):
    optimal_dcgs = {}
    for qid in results:
        q_rels = []
        for docid in results[qid]:
            try:
                rel = qrels[qid][docid]
            except KeyError:
                pass
            else:
                q_rels.append(rel)
        q_rels.sort(reverse=True)
        optimal_dcgs[qid] = .0
        for i in xrange(5):
            optimal_dcgs[qid] += q_rels[i] * 1.0 / math.log(i + 2, 2)

    return optimal_dcgs

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qrel_file', '-qf', default='/infolab/node4/lukuang/trec_news/data/eval/bqrels')
    parser.add_argument("--merge_cutoff","-mt",type=int,default=5)
    parser.add_argument("result_dir")
    args=parser.parse_args()


    qrels = read_qrel(args.qrel_file)

    idcgs = get_idcgs(qrels)

    # print idcgs
    results = get_results(args.result_dir, args.merge_cutoff)

    optimal_dcgs = get_optimal_dcgs(results, qrels)

    print 'optimal ndcg:'
    all_odcg = []
    for qid in optimal_dcgs:
        o_ndcg = 0
        if idcgs[qid] != 0:
            o_ndcg = optimal_dcgs[qid] * 1.0/idcgs[qid]
        else:
            continue
        all_odcg.append(o_ndcg)
        print '\t{}: {}'.format(qid, o_ndcg)
    print '\tall: {}'.format( sum(all_odcg)/len(all_odcg)  )


if __name__=="__main__":
    main()

