"""
import query documents
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

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection_dump","-cd",default="/infolab/node4/lukuang/trec_news/data/washington_post/collection_json_dump/v2/dump")
    args=parser.parse_args()

    query_dbs = [
        RedisDB.bl_query_db,
        RedisDB.er_query_db,
        RedisDB.test_query_db
    ]

    docids = set()
    doc_db = redis.Redis(host=RedisDB.host,
                          port=RedisDB.port,
                          db=RedisDB.doc_db)

    collection = json.load(open(args.collection_dump))
    print "collection loaded"
    for qdb in query_dbs:

        qdb_end_point = redis.Redis(host=RedisDB.host,
                                      port=RedisDB.port,
                                      db=qdb)

        for qid in qdb_end_point.keys():
            query_string = qdb_end_point.get(qid)
            query_json = json.loads(query_string)
            docid = query_json["docid"]
            docids.add(docid)
            article_json = collection[docid]
            article_json_str = json.dumps(article_json)
            doc_db.set(docid,article_json_str)
            print "import document %s successful" %(docid)
    
    
    print "There are %d documents" %(len(docid))
    




        


if __name__=="__main__":
    main()

