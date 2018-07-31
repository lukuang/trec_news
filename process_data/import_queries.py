"""
import queries into redis db
"""

import os
import json
import sys
import re
import redis
import argparse
import codecs

sys.path.append("/infolab/node4/lukuang/trec_news/trec_news/src")
from config.db import RedisDB
from data.queries import BQuery,EQuery

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query_type","-qt",choices=range(2),default=0,type=int,
        help="""
            Choose the query type:
                0: background linking
                1: entity ranking
        """)
    parser.add_argument("query_file")
    args=parser.parse_args()

    if args.query_type == 0:

        bl_query_db = redis.Redis(host=RedisDB.host,
                                      port=RedisDB.port,
                                      db=RedisDB.bl_query_db)
        bl_queries = BQuery(args.query_file)
        
        for query in bl_queries.queries:
            query_json_string = json.dumps(query)
            qid = query["qid"]
            bl_query_db.set(qid,query_json_string)

    elif args.query_type == 1:
        er_query_db = redis.Redis(host=RedisDB.host,
                                      port=RedisDB.port,
                                      db=RedisDB.er_query_db)
        er_queries = EQuery(args.query_file)
        
        for query in er_queries.queries:
            query_json_string = json.dumps(query)
            qid = query["qid"]
            er_query_db.set(qid,query_json_string)
    else:
        raise NotImplemented("query type %d is not Not Implemented" %(args.query_type))

if __name__=="__main__":
    main()

