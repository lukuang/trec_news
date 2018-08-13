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
    parser.add_argument("--collection_dump_root","-cdr",default="/infolab/node4/lukuang/trec_news/data/washington_post/collection_json_dump/")
    parser.add_argument("--document_type","-dt",choices=range(2),default=0,type=int,
        help="""
            Choose the index type:
                0: normal
                1: annotated
        """)
    args=parser.parse_args()

    query_dbs = [
        RedisDB.bl_query_db,
        RedisDB.er_query_db,
        RedisDB.test_query_db
    ]

    docids = set()
    if args.document_type == 0:
        collection_dump = os.path.join(args.collection_dump_root,"v2","dump")
        doc_db = redis.Redis(host=RedisDB.host,
                          port=RedisDB.port,
                          db=RedisDB.doc_db)
    else:
        collection_dump = os.path.join(args.collection_dump_root,"annotated","dump")
        doc_db = redis.Redis(host=RedisDB.host,
                              port=RedisDB.port,
                              db=RedisDB.annotated_doc_db)
    collection = json.load(open(collection_dump))

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
    
    
    print "There are %d documents" %(len(docids))
    




        


if __name__=="__main__":
    main()

