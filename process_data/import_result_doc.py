"""
import documents from the results to the redis database
NOTE: the results file must be in the directory with the
name the same as the query id
"""

import os
import json
import sys
import re
import argparse
import codecs
import redis

sys.path.append("/infolab/node4/lukuang/trec_news/trec_news/src")
from config.db import RedisDB
from data import ArticleGenerator,Article


def load_docid_from_file(src_file,docids,doc_db):
    result_dict = {}
    with open(src_file) as f:
        for line in f:
            parts = line.strip().split()
            docid = parts[2]
           
            if not doc_db.exists(docid):
                docids.add(docid)
            else:
                print "skip existing document %s" %(docid)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection_dump","-cd",default="/infolab/node4/lukuang/trec_news/data/washington_post/collection_json_dump/v2/dump")
    parser.add_argument("file_list",nargs='+')
    args=parser.parse_args()

    docids = set()
    doc_db = redis.Redis(host=RedisDB.host,
                          port=RedisDB.port,
                          db=RedisDB.doc_db)

    

    for src_file in args.file_list:
        qid = os.path.basename(os.path.dirname(src_file ))
        load_docid_from_file(src_file,docids,doc_db)
    
    print "There are %d documents" %(len(docids))
    
    if len(docids) == 0:
        sys.exit(0)
    collection = json.load(open(args.collection_dump))
    print "collection loaded"

    # NOTE: the results file must be in the directory with the
    # name the same as the query id
    
    # print "The results:"
    # print docids

    for docid in docids:
        article_json = collection[docid]
        article_json_str = json.dumps(article_json)
        doc_db.set(docid,article_json_str)


        print "import document %s successful" %(docid)

if __name__=="__main__":
    main()

