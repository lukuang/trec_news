"""
get dbpedia entity type
"""

import os
import json
import sys
import redis
import re
import argparse
import codecs

sys.path.append("/infolab/node4/lukuang/trec_news/trec_news/src")
from config.db import RedisDB
from entity import dbpedia

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    args=parser.parse_args()


    query_dbs = [
        RedisDB.bl_query_db,
        RedisDB.er_query_db,
        RedisDB.test_query_db
    ]


    document_ids = set()
    print "Get document ids"
    for qdb in query_dbs:

        qdb_end_point = redis.Redis(host=RedisDB.host,
                                      port=RedisDB.port,
                                      db=qdb)

        for qid in qdb_end_point.keys():
            query_string = qdb_end_point.get(qid)
            query_json = json.loads(query_string)
            docid = query_json["docid"]
            document_ids.add(docid)

    doc_entity_db =  redis.Redis(host=RedisDB.host,
                                      port=RedisDB.port,
                                      db=RedisDB.doc_entity_db)

    all_entities = set()
    for docid in document_ids:
        entity_struct_json = doc_entity_db.get(docid)
        entity_struct = json.loads(entity_struct_json)

        #get paragraph entities
        for pid,entity_list in enumerate(entity_struct["paragraphs"]):
            for entity in entity_list:
                all_entities.add(entity)
        
        #get title entities
        for entity in entity_struct["title"]:
            all_entities.add(entity)

    print "There are %d entities" %(len(all_entities))

    entity_types_db =  redis.Redis(host=RedisDB.host,
                                      port=RedisDB.port,
                                      db=RedisDB.entity_types_db)
    count = 0
    type_gettor =  dbpedia.TypeGettor() 
    for entity in all_entities:
        if not entity_types_db.exists(entity):
            count += 1
            entity_types = type_gettor.get_entity_types(entity)
            if entity_types:
                entity_types_db.set(entity,entity_types)
            else:
                print "empty types for entity %s!" %(entity)

    print "Try to get entity types for %d entities" %(count)

if __name__=="__main__":
    main()

