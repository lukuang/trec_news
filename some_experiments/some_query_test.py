"""
run some easy query testing
"""

import os
import json
import sys
import re
import argparse
import codecs
import redis
import subprocess
from string import Template

from collections import OrderedDict
from myUtility.indri import IndriQueryFactory

sys.path.append("/infolab/node4/lukuang/trec_news/trec_news/src")
from config.db import RedisDB


RULE = [
    "method:f2exp",
    "method:dirichlet",
    "method:pivoted",
    "method:okapi"
]

def gene_single_query_file(number_of_results,query_type,
                           rule,index_dir,query_dir,
                           test_query_db,doc_db,
                           qid):
    query_string = test_query_db.get(qid)
    query_json = json.loads(query_string)
    docid = query_json["docid"]
    doc_string = doc_db.get(docid)

    doc_json = json.loads(doc_string)
    paragraphs = doc_json["paragraphs"]
    published_date = doc_json["published_date"]

    cmd_template = Template('curl http://headnode:2222/rest/annotate   -H "Accept: application/json"   --data-urlencode "text=$text" --data "confidence=0.5"')

    query_file_path = os.path.join(query_dir,qid)
    # create queries

    query_factory = IndriQueryFactory(number_of_results,rule=RULE[rule],numeric_compare="less")
    queries = OrderedDict()
    for index,para_text in enumerate(paragraphs):
        qid = "Q%s"%(str(index).zfill(2))

        if re.match("^Read more:", para_text):
            break
        if query_type == 0:
            queries[qid] = para_text

        elif query_type == 1:
            p1 = subprocess.Popen(cmd_template.substitute(text=para_text),
                                  shell=True, stdout=subprocess.PIPE)
            output = p1.communicate()[0]
            returned_json = json.loads(output)
            named_entities = []
            try:
                entities = returned_json["Resources"]
            except KeyError:
                continue
            else:
                for entitiy_struct in entities:
                    named_entities.append(entitiy_struct["@surfaceForm"])
                queries[qid] = " ".join(named_entities)

    query_factory.gene_query_with_numeric_filter(query_file_path,
                                    queries,index_dir,published_date,
                                    "published_date",run_id="test")



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query_dir")
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
    parser.add_argument("--index_dir",default="/infolab/node4/lukuang/trec_news/data/washington_post/index/v2")
    parser.add_argument("--number_of_results","-rn",default=10,type=int)
    args=parser.parse_args()

    #load the testing query document
    test_query_db = redis.Redis(host=RedisDB.host,
                                      port=RedisDB.port,
                                      db=RedisDB.test_query_db)
    
    doc_db = redis.Redis(host=RedisDB.host,
                          port=RedisDB.port,
                          db=RedisDB.doc_db)

    for qid in test_query_db.keys():
        gene_single_query_file(args.number_of_results,args.query_type,
                               args.rule,args.index_dir,args.query_dir,
                               test_query_db,doc_db,
                               qid)



if __name__=="__main__":
    main()

