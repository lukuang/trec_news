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

def get_idcgs(qrels, ndcg_cutoff):
    idcgs = {}
    for qid in qrels:
        rels = qrels[qid].values()
        rels.sort(reverse=True)
        idcgs[qid] = .0
        for i in xrange(min(ndcg_cutoff, len(rels))):
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

def get_results(result_dirs, merge_cutoff):
    results = {}

    for single_result_dir in result_dirs:
        if 'doc_lm_analysis' in single_result_dir:
            get_results_from_single_run(single_result_dir, 20, results)
        else:
            get_results_from_single_run(single_result_dir, merge_cutoff, results)
    
    for qid in results:
        results[qid] = list(set(results[qid]))
    return results

def get_results_from_single_run(single_result_dir, merge_cutoff, results):
    
    for qid in os.listdir(single_result_dir):
        old_pid = None
        line_num = 0
        if qid not in results:
            results[qid] = []
        q_result_file = os.path.join(single_result_dir,qid)
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



def get_optimal_dcgs(results, qrels, ndcg_cutoff):
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
        for i in xrange(min(ndcg_cutoff, len(q_rels))):

            optimal_dcgs[qid] += q_rels[i] * 1.0 / math.log(i + 2, 2)

    return optimal_dcgs

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qrel_file', '-qf', default='/infolab/node4/lukuang/trec_news/data/eval/bqrels')
    parser.add_argument("--merge_cutoff","-mt",type=int,default=5)
    parser.add_argument("--ndcg_cutoff","-nt",type=int,default=5)
    parser.add_argument("result_dirs" ,nargs='+')
    args=parser.parse_args()


    qrels = read_qrel(args.qrel_file)

    idcgs = get_idcgs(qrels, args.ndcg_cutoff)

    # print idcgs
    results = get_results(args.result_dirs, args.merge_cutoff)

    optimal_dcgs = get_optimal_dcgs(results, qrels, args.ndcg_cutoff)

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

