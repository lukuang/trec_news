"""
get keyword queries for each paragraphs
"""

import os
import json
import sys
import re
import argparse
import codecs
import subprocess
from string import Template
import redis
import math
from myUtility.indri import IndriQueryFactory
from collections import OrderedDict

sys.path.append("/infolab/node4/lukuang/trec_news/trec_news/src")
from config.db import RedisDB

RULE = [
    "method:f2exp",
    "method:dirichlet",
    "method:pivoted",
    "method:okapi"
]

def get_canonical_form(url):
    m = re.search("resource/(.+)$",url)
    return m.group(1)


def get_words_and_entities(para_text):
    p1 = subprocess.Popen(cmd_template.substitute(text=para_text),
                                  shell=True, stdout=subprocess.PIPE)
    output = p1.communicate()[0]
    returned_json = json.loads(output)
    entiy_strings = []
    entities = {}
    try:
        entities = returned_json["Resources"]
    except KeyError:
        pass
    else:
        for entitiy_struct in entities:
            suface_form = entitiy_struct["@surfaceForm"]
            canonical_form = get_canonical_form(entitiy_struct["@URI"])
            entiy_strings.append(suface_form)
            entities[canonical_form] = suface_form

class PDWCalculator(object):
    """
    used to compute the the probability P(keyword|document)
    """
    def __init__(self,para_index):
        self._cmd_template = Template('dumpindex %s t $word' %(para_index))

    def compute_pdw(self,paragraph_words):
        
        # para_words_struct = self._get_para_word_struct(docs)
        # all_words = set(para_words_struct.keys())
        # for single_word in para_words_struct:
        #     all_words.update(para_words_struct[single_word])
        
        all_words = self._get_all_words(paragraph_words)

        word_document_vector = {}
        print "Getting word document vector:"
        for single_word in all_words:
            word_document_vector[single_word] = self._get_word_document_vector(single_word)

        pdw = OrderedDict()
        pww = {}


        print "Getting pdw for each paragraph"
        for pid in paragraph_words:
            d = paragraph_words[pid]
            single_pdw = {}
            for w1 in d:
                if len(word_document_vector[w1]) <= 5:
                    # ignore very rare words
                    continue
                single_pdw[w1] = .0
                for w2 in d:
                    if w2!=w1:
                        if not w1 in pww:
                            pww[w1] = {}
                        
                        if w2 not in pww[w1]:
                            pww[w1][w2] = self._compute_pww(w1,w2, word_document_vector)
                        try:
                            single_pdw[w1] += math.log(pww[w1][w2])
                        except ValueError:
                            print "Wrong pww for %s %s" %(w1,w2)
                            print "value is %f" %(pww[w1][w2])
                            pass
            pdw[pid] = single_pdw

        return pdw

    def _get_all_words(self,paragraph_words):
        all_words = set()
        for d in paragraph_words.values():
            all_words.update(d)
        return all_words



    def _get_word_document_vector(self,single_word):
        word_document_vector = set()
        p1 = subprocess.Popen(self._cmd_template.substitute(word=single_word),
                                      shell=True, stdout=subprocess.PIPE)
        for line in iter(p1.stdout.readline,''):
            parts = line.split()
            if parts[0].isdigit():
                docid = parts[0]
                word_document_vector.add(docid)
        return word_document_vector

    @staticmethod
    def _compute_pww(word1,word2,word_document_vector):
        vector1 = word_document_vector[word1]
        vector2 = word_document_vector[word2]
        count = 0
        for d in vector1:
            if d in vector2:
                count += 1  
        return (count*1.0)/len(vector1)

def softmax_normalized_weight(weight_dict):
    weight_sum = .0
    for term in weight_dict:
        new_weight = math.exp(weight_dict[term])
        weight_dict[term] = new_weight
        weight_sum += new_weight

    for term in weight_dict:
        weight_dict[term] /= weight_sum


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query_file","-qf")
    parser.add_argument("--rule","-r",choices=range(4),default=0,type=int,
        help="""
            Choose the retrieval function:
                0: f2exp
                1: dirichlet
                2: pivoted
                3: okapi
        """)
    parser.add_argument("--query_type","-qt",choices=range(2),default=0,type=int,
        help="""
            Choose the query type:
                0: all_text
                1: named_entities
        """)
    parser.add_argument("--para_index",default="/infolab/node4/lukuang/trec_news/data/washington_post/paragraph_index/v2")
    parser.add_argument("--search_index",default="/infolab/node4/lukuang/trec_news/data/washington_post/index/v2")
    parser.add_argument("--qid",default="2203bfb5aeb4cf0adb8997e0c7185c28")
    parser.add_argument("--number_of_keywords","-kn",default=3,type=int)
    parser.add_argument("--number_of_results","-rn",default=10,type=int)
    args=parser.parse_args()

    #load the testing query document
    query_db = redis.Redis(host=RedisDB.host,
                                      port=RedisDB.port,
                                      db=RedisDB.query_db)

    doc_string = query_db.get(args.qid)

    print "for query %s" %(args.qid)

    doc_json = json.loads(doc_string)
    paragraphs = doc_json["paragraphs"]
    published_date = doc_json["published_date"]

    # load stopwords
    collection_stats_db = redis.Redis(host=RedisDB.host,
                         port=RedisDB.port,
                         db=RedisDB.collection_stats_db)

    # create queries

    query_factory = IndriQueryFactory(args.number_of_results,rule=RULE[args.rule],numeric_compare="less")
    paragraph_words = OrderedDict()
    print "Getting words for each paragraph"
    for index,para_text in enumerate(paragraphs):
        qid = "Q%s"%(str(index).zfill(2))

        if re.match("^Read more:", para_text):
            break

        # words, named_entities = get_words_and_entities(para_text)
        paragraph_words[qid] = []
        words = re.findall("\w+", para_text.lower())
        for w in words:
            if not collection_stats_db.sismember("stopwords",w.lower()) :
                paragraph_words[qid].append(w)


    pdw_calculator = PDWCalculator(args.para_index)

    pdws = pdw_calculator.compute_pdw(paragraph_words)

    print "Output keywords:"
    for pid in pdws:
        print "For paragraph %s:" %(pid) 
        sorted_pdw = sorted(pdws[pid].items(),key=lambda x:x[1],reverse=True)[:args.number_of_keywords]
        for keyword_pdw_pair in sorted_pdw:
            print "\t%s: %f" %(keyword_pdw_pair[0],keyword_pdw_pair[1])
        print '-'*10

    if args.query_file:
        print "Generating query file"
        query_factory = IndriQueryFactory(100,rule=RULE[args.rule],numeric_compare="less")
        queries = OrderedDict()
        for pid in pdws:
            sorted_pdw = sorted(pdws[pid].items(),key=lambda x:x[1],reverse=True)[:args.number_of_keywords]
            weight_dict = {}
            for keyword_pdw_pair in sorted_pdw:
                weight = keyword_pdw_pair[1]
                term = keyword_pdw_pair[0]
                # weight_dict[term] = weight
                weight_dict[term] = 1.0
            # softmax_normalized_weight(weight_dict) 
            queries[pid] = weight_dict
        query_factory.gene_query_with_numeric_filter(args.query_file,
                                queries,args.search_index,published_date,
                                "published_date",run_id="test")

if __name__=="__main__":
    main()

