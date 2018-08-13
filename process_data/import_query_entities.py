"""
import all query entities (cannonical form) to the database
"""

import os
import json
import sys
import re
import argparse
import redis
import codecs
from collections import defaultdict

sys.path.append("/infolab/node4/lukuang/trec_news/trec_news/src")
from config.db import RedisDB


def read_paragraph_entities(pharagraph_entity_dir,document_ids):
    paragraph_entities = defaultdict(lambda: defaultdict(list))
    for file_name in os.walk(pharagraph_entity_dir).next()[2]:
        print "read from file %s" %(file_name)
        entity_file = os.path.join(pharagraph_entity_dir,file_name)
        with open(entity_file) as f:
            for line in f:
                parts = line.split()
                phara_id = parts[0]
                entity_cannonical = parts[4]
                m = re.match("^(.+)-(\d+)",phara_id)
                try:
                    docid = m.group(1)
                    pid = int(m.group(2))
                except AttributeError:
                    print "Malformatted line!"
                    print line
                else:
                    if docid not in document_ids:
                        continue
                    else:
                        paragraph_entities[docid][pid].append(entity_cannonical)
    return paragraph_entities

def read_title_entities(title_entity_file,document_ids):
    title_entities = defaultdict(list)
    with open(title_entity_file) as f:
        for line in f:
            parts = line.split()
            docid = parts[0]
            entity_cannonical = parts[4]
            if docid in document_ids:

                title_entities[docid].append(entity_cannonical)
                    
    return title_entities

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paragraph_entity_dir","-ped",default="/infolab/node4/lukuang/trec_news/data/washington_post/paragraph_entities")
    parser.add_argument("--title_entity_file","-tf",default="/infolab/node4/lukuang/trec_news/data/washington_post/title_entities/title_entities")
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
    
    print "get title entities"
    title_entities = read_title_entities(args.title_entity_file,document_ids)

    print "get paragraph entities"
    paragraph_entities = read_paragraph_entities(args.paragraph_entity_dir,document_ids)
    
    doc_entity_db =  redis.Redis(host=RedisDB.host,
                                      port=RedisDB.port,
                                      db=RedisDB.doc_entity_db)
    for docid in document_ids:
        entity_dict = {
                        "title": title_entities[docid],
                        "paragraphs": paragraph_entities[docid]
                      }
        doc_entity_db.set(docid,json.dumps(entity_dict))

        print "import document %s successful" %(docid)
    
    
    print "There are %d documents" %(len(document_ids))




if __name__=="__main__":
    main()

