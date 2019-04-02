"""
plot the relation between inverse paragraph frequency
 w.r.t the conditional entroppy or pmi of relevance given
 the term is present in a document
"""

import os
import json
import sys
import re
import redis
import argparse
import codecs
import math
import matplotlib
from collections import Counter
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from misc import *

sys.path.append("/infolab/node4/lukuang/trec_news/trec_news/src")
from config.db import RedisDB


class Qrel(object):
    def __init__(self, qrel_file, doc_index, measure):
        self._qrel_file = qrel_file
        self._N = get_num_doc(doc_index)
        self._qrels = read_qrel(qrel_file)
        self._relevant_docs = {}
        for qid in self._qrels:
            self._relevant_docs[qid] = []
            for docid in self._qrels[qid]:
                rel = self._qrels[qid][docid]
                if rel > 0:
                    self._relevant_docs[qid].append(get_internal_docid(doc_index, docid))


        if measure == 'pmi':
            self.measure = self._compute_pmi
        elif measure == 'cond_entropy':
            self.measure = self._compute_cond_entropy

        else:
            raise NotImplementedError('Measure {} is not implemented!'.format(measure))

        self._print_flag = True

    def _compute_cond_entropy(self, doc_vector, qid):
        if self._print_flag:
            print 'measure conditional entropy'
            self._print_flag = False
        pr_t = len(doc_vector) * 1.0 / self._N
        pr_no_t = 1 - pr_t
        
        # the number of documents that are relevant and
        # contain term t
        t_rel_count = len(list(filter(lambda docid: docid in self._relevant_docs[qid], doc_vector)))
        pr_t_rel = t_rel_count * 1.0 / self._N
        pr_t_irrel = (len(doc_vector) - t_rel_count) * 1.0 / self._N

        no_t_rel_count = len(self._relevant_docs[qid]) - t_rel_count 
        pr_no_t_rel = no_t_rel_count * 1.0 / self._N
        pr_no_t_irrel = 1 - pr_t_rel - pr_t_irrel - pr_no_t_rel

        entropy = pr_t_rel * safe_log( pr_t, pr_t_rel)
        entropy += pr_t_irrel * safe_log(pr_t, pr_t_irrel )
        entropy += pr_no_t_rel * safe_log(pr_no_t , pr_no_t_rel)
        entropy += pr_no_t_irrel * safe_log(pr_no_t , pr_no_t_irrel)


        return entropy


    def _compute_pmi(self, doc_vector, qid):
        if self._print_flag:
            print 'measure pmi'
            self._print_flag = False
        pr_t = len(doc_vector) * 1.0 / self._N
        t_rel_count = len(list(filter(lambda docid: docid in self._relevant_docs[qid], doc_vector)))
        pr_rel = len(self._relevant_docs[qid]) * 1.0 / self._N

        return safe_log(t_rel_count, pr_t * pr_rel)







def get_ipf_map(paragraph_words):
    pf = Counter()
    num_of_para = len(paragraph_words) 
    for pid in paragraph_words:
        pf.update(paragraph_words[pid])

    ipf = {}
    for word in pf:
        ipf[word] = num_of_para * 1.0 / pf[word] 

    return ipf





def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--para_index",default="/infolab/node4/lukuang/trec_news/data/washington_post/paragraph_index/v3_stemed")
    parser.add_argument("--doc_index",default="/infolab/node4/lukuang/trec_news/data/washington_post/index/v3_stemed")
    parser.add_argument('--qrel_file', '-qf', default='/infolab/node4/lukuang/trec_news/data/eval/bqrels')
    parser.add_argument('--measure', '-m', default='pmi', choices=['cond_entropy', 'pmi'])
    parser.add_argument("dest_dir")
    args=parser.parse_args()

    qrels = Qrel(args.qrel_file, args.doc_index, args.measure)

    collection_stats_db = redis.Redis(host=RedisDB.host,
                                      port=RedisDB.port,
                                      db=RedisDB.stemed_collection_stats_db)

    #load the testing query document
    bl_query_db = redis.Redis(host=RedisDB.host,
                                 port=RedisDB.port,
                                 db=RedisDB.bl_query_db)

    doc_db = redis.Redis(host=RedisDB.host,
                              port=RedisDB.port,
                              db=RedisDB.doc_db)

    meausre_dir = os.path.join(args.dest_dir, args.measure)
    if not os.path.exists(meausre_dir):
        os.mkdir(meausre_dir)

    doc_vector_generator = DocVectorGenerator(args.doc_index)

    all_measure = []
    all_ipf = []
    for qid in bl_query_db.keys():
        print "start processing query %s" %(qid)
        query_string = bl_query_db.get(qid)
        query_json = json.loads(query_string)
        docid = query_json["docid"]
        doc_string = doc_db.get(docid)
        doc_json = json.loads(doc_string)
        paragraphs = doc_json["paragraphs"]
        num_of_para = len(paragraphs)
        paragraph_words = get_paragraph_word_sets(args.para_index, docid, num_of_para)
        # print 'There are {} paragraphs'.format(len(paragraph_words))
        ipf_map  =  get_ipf_map(paragraph_words)
        # print ipf_map
        # sys.exit()
        doc_vector =  doc_vector_generator.get_doc_vector(ipf_map)

        query_measure = []
        query_ipf = []

        for word in ipf_map:
            word_measure = qrels.measure(doc_vector[word], qid)
            query_measure.append(word_measure)
            query_ipf.append(ipf_map[word])
            all_measure.append(word_measure)
            all_ipf.append(ipf_map[word])


        query_dest_file = os.path.join(meausre_dir, '{}.png'.format(qid))

        plt.plot(query_ipf, query_measure, 'ro')
        plt.savefig(query_dest_file)
        plt.clf()


    all_dest_file = os.path.join(meausre_dir, 'all.png' )
    plt.plot(all_ipf, all_measure, 'ro')
    plt.savefig(all_dest_file)



if __name__=="__main__":
    main()

