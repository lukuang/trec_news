"""
import document and paragraph vectors for entities
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

def vector_add_one(entity_vectors,text_id,eid):
    if eid not in entity_vectors:
        entity_vectors[eid] = set()
    entity_vectors[eid].add(text_id)

def import_to_db(collection_stats_db,vector_name,entity_vectors):
    for eid in entity_vectors:
        value = json.dumps( list(entity_vectors[eid]) )
        collection_stats_db.hset(vector_name,eid,value)


def add_title_entities(title_entity_file,entity_doc_vectors):
    with open(title_entity_file) as f:
        for line in f:
            parts = line.split()
            docid = parts[0]
            eid = parts[4]
            vector_add_one(entity_doc_vectors,docid,eid)
            
                    

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paragraph_entity_dir","-ped",default="/infolab/node4/lukuang/trec_news/data/washington_post/paragraph_entities")
    parser.add_argument("--title_entity_file","-tf",default="/infolab/node4/lukuang/trec_news/data/washington_post/title_entities/title_entities")
    args=parser.parse_args()

    collection_stats_db = redis.Redis(host=RedisDB.host,
                         port=RedisDB.port,
                         db=RedisDB.collection_stats_db)

    entity_doc_vectors = {}
    entity_paragraph_vectors = {}

    # add title entities
    add_title_entities(args.title_entity_file,entity_doc_vectors)

    # add paragraph entities
    for file_name in os.walk(args.paragraph_entity_dir).next()[2]:
        file_path = os.path.join(args.paragraph_entity_dir,file_name)
        print "process file %s" %(file_path)
        


        with open(file_path) as f:
            for line in f:
                parts = line.split()

                pid = parts[0]
                eid = parts[4]
                vector_add_one(entity_paragraph_vectors,pid,eid)

                m = re.search("^(.+?)-\d+$",pid)
                try:
                    docid = m.group(1)
                except AttributeError:
                    raise ValueError("Mal-formatted pid %s!" %(pid))
                else:
                    vector_add_one(entity_doc_vectors,docid,eid)

    import_to_db(collection_stats_db,"entity_doc_vectors",entity_doc_vectors)
    import_to_db(collection_stats_db,"entity_paragraph_vectors",entity_paragraph_vectors)

        

if __name__=="__main__":
    main()

