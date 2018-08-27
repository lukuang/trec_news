"""
generate query files, run the queries, and 
get top 5 results for each paragraphs
"""

import os
import json
import sys
import re
import argparse
import codecs
from lxml import etree
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



def gene_single_original_keyword_query(original_keyword_query_dir,rule,para_index,search_index,
                              number_of_keywords,number_of_results,
                              bl_query_db,doc_db,
                              qid):
    print "for query %s" %(qid)
    query_file = os.path.join(original_keyword_query_dir,qid)
    query_string = bl_query_db.get(qid)
    query_json = json.loads(query_string)
    docid = query_json["docid"]
    doc_string = doc_db.get(docid)

    doc_json = json.loads(doc_string)

    doc_json = json.loads(doc_string)
    paragraphs = doc_json["paragraphs"]
    published_date = doc_json["published_date"]

    # load stopwords
    collection_stats_db = redis.Redis(host=RedisDB.host,
                                      port=RedisDB.port,
                                      db=RedisDB.collection_stats_db)

    # create queries

    query_factory = IndriQueryFactory(number_of_results,rule=RULE[rule],numeric_compare="less")
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
        if not paragraph_words[qid]:
            paragraph_words.pop(qid,None)


    pdw_calculator = PDWCalculator(para_index)

    pdws = pdw_calculator.compute_pdw(paragraph_words)

    print "Output keywords:"
    for pid in pdws:
        print "For paragraph %s:" %(pid) 
        sorted_pdw = sorted(pdws[pid].items(),key=lambda x:x[1],reverse=True)[:number_of_keywords]
        for keyword_pdw_pair in sorted_pdw:
            print "\t%s: %f" %(keyword_pdw_pair[0],keyword_pdw_pair[1])
        print '-'*10

    print "Generating query file"
    query_factory = IndriQueryFactory(100,rule=RULE[rule],numeric_compare="less")
    queries = OrderedDict()
    
    for pid in pdws:
        sorted_pdw = sorted(pdws[pid].items(),key=lambda x:x[1],reverse=True)[:number_of_keywords]
        weight_dict = {}
        for keyword_pdw_pair in sorted_pdw:
            weight = keyword_pdw_pair[1]
            term = keyword_pdw_pair[0]
            # weight_dict[term] = weight
            weight_dict[term] = 1.0
        # softmax_normalized_weight(weight_dict) 
        queries[pid] = weight_dict
    query_factory.gene_query_with_numeric_filter(query_file,
                            queries,search_index,published_date,
                            "published_date",run_id="test")

def setup_weight(title_weight):
    body_weight = 1.0 - title_weight
    def give_field_weight(text_string_match):
        text_string = text_string_match.group(2)
        replace_string = ""
        weight = 0.0
        is_weight = True
        for match in re.findall("\S+",text_string):
            if is_weight:
                weight = float(match) 
            else:
                new_title_weight = weight*title_weight
                replace_string += "%f %s.(tt) " %(new_title_weight, match)
                new_body_weight = weight*body_weight
                replace_string += "%f %s.(body) " %(new_body_weight, match)

            is_weight = not is_weight
        return "#weight(%s)" %(replace_string)
    return give_field_weight
        
                    


def add_field_weight(original_keyword_query_dir,keyword_field_query_dir,
                     qid,give_field_weight):
    src_file =  os.path.join(original_keyword_query_dir,qid)
    dest_file =  os.path.join(keyword_field_query_dir,qid)

    with open(src_file) as f:
        root = etree.parse(f)
        for query in root.iterfind("query"):
            query_string = query.find("text").text
            query_string = re.sub("#(weight|combine)\(([^\)]+)\)",give_field_weight,query_string)
            # print query_string
            query.find("text").text = query_string

        with open(dest_file,"w") as of:
            of.write( etree.tostring(root, pretty_print=True) )


def run_query(keyword_field_query_dir,field_query_result_dir,qid):
    query_file = os.path.join(keyword_field_query_dir,qid)
    result_file = os.path.join(field_query_result_dir,qid)
    run_query_args = "IndriRunQuery %s > %s" %(query_file,result_file)
    subprocess.call(run_query_args,shell=True)

def find_top_five(field_query_result_dir,top_five_result_dir):
    for file_name in os.walk(field_query_result_dir).next()[2]:
        src_file = os.path.join(field_query_result_dir,file_name)
        dest_file = os.path.join(top_five_result_dir,file_name)


        result_dict = {}
        output_lines = []
        print "process file %s" %(src_file)
        with open(src_file) as f:
            for line in f:
                parts = line.strip().split()
                qid = parts[0]
                score = float(parts[4])
                if qid not in result_dict:
                    result_dict[qid] = set()
                if len(result_dict[qid]) >=5:
                    continue
                elif score in result_dict[qid]:
                    # use the score to ensure that
                    # for duplicate documents with
                    # same content, only one of them
                    # will be selected
                    continue
                else:
                    result_dict[qid].add(score)
                    output_lines.append(line)

        with open(dest_file,"w") as of:
            for line in output_lines:
                of.write(line)


def main(): 
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root_dest_dir")
    parser.add_argument("--rule","-r",choices=range(4),default=0,type=int,
        help="""
            Choose the retrieval function:
                0: f2exp
                1: dirichlet
                2: pivoted
                3: okapi
        """)
    parser.add_argument("--index_type","-it",choices=range(2),default=0,type=int,
        help="""
            Choose the index type:
                0: normal
                1: annotated
        """)
    parser.add_argument("--para_root_index",default="/infolab/node4/lukuang/trec_news/data/washington_post/paragraph_index/")
    parser.add_argument("--search_root_index",default="/infolab/node4/lukuang/trec_news/data/washington_post/index/")
    parser.add_argument("--number_of_keywords","-kn",default=5,type=int)
    parser.add_argument("--number_of_results","-rn",default=10,type=int)
    parser.add_argument("--title_weight","-tw",type=float,default=0.7,
        help="""
            weight of the title field (form 0.0 to 1.0)
        """
        )
    args=parser.parse_args()

    #load the testing query document
    bl_query_db = redis.Redis(host=RedisDB.host,
                                 port=RedisDB.port,
                                 db=RedisDB.bl_query_db)
    if args.index_type == 0:
        print "Using normal index"
        doc_db = redis.Redis(host=RedisDB.host,
                              port=RedisDB.port,
                              db=RedisDB.doc_db)
        para_index = os.path.join(args.para_root_index,"v2")
        search_index = os.path.join(args.search_root_index,"v2")

    else:
        print "Using annotated index"
        doc_db = redis.Redis(host=RedisDB.host,
                              port=RedisDB.port,
                              db=RedisDB.annotated_doc_db)
        para_index = os.path.join(args.para_root_index,"annotated")
        search_index = os.path.join(args.search_root_index,"annotated")


    original_keyword_query_dir = os.path.join(args.root_dest_dir,"original_keyword_queries")
    keyword_field_query_dir = os.path.join(args.root_dest_dir,"keyword_queries_with_field")
    field_query_result_dir = os.path.join(args.root_dest_dir,"field_query_results")
    top_five_result_dir = os.path.join(args.root_dest_dir,"top_five")
    

    # print "generate original keyword queries"
    # for qid in bl_query_db.keys():
    #     gene_single_original_keyword_query(original_keyword_query_dir, args.rule,
    #                               para_index, search_index,
    #                               args.number_of_keywords,
    #                               args.number_of_results,
    #                               bl_query_db,doc_db,
    #                               qid)

    print "add field weights"
    give_field_weight = setup_weight(args.title_weight)
    for qid in bl_query_db.keys():
        add_field_weight(original_keyword_query_dir,keyword_field_query_dir,
                         qid,give_field_weight)

    print "run queries"
    for qid in bl_query_db.keys():
        run_query(keyword_field_query_dir,field_query_result_dir,qid)

    print "get top five results for each paragraph"
    find_top_five(field_query_result_dir,top_five_result_dir)


if __name__=="__main__":
    main()

