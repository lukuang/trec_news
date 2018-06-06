"""
import documents from the results to the redis database
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


def load_docid_from_file(src_file):
    result_dict = {}
    docids = {}
    with open(src_file) as f:
        for line in f:
            parts = line.strip().split()
            phara_id = parts[0]
            docid = parts[2]
            score = float(parts[4])
            if phara_id not in result_dict:
                result_dict[phara_id] = set()
                docids[phara_id] = []
            if len(result_dict[phara_id]) >=2:
                continue
            elif score in result_dict[phara_id]:
                continue
            else:
                result_dict[phara_id].add(score)
                docids[phara_id].append(docid)
    return docids

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file_list","-fl",nargs='+')
    args=parser.parse_args()

    docids = {}
    for src_file in args.file_list:
        qid = os.path.basename(os.path.dirname(src_file ))
        docids[qid] = load_docid_from_file(src_file)
        
    # print "The results:"
    # print docids

    article_generator = ArticleGenerator()
    doc_info_map = {}
    for qid in docids:
        for phara_id in docids[qid]:
            for docid in docids[qid][phara_id]:
                if docid not in doc_info_map:
                    doc_info_map[docid] = {
                        "qid":qid,
                        "phara_ids":[phara_id]
                    }
                else:
                    doc_info_map[docid]["phara_ids"].append(phara_id)

    data_dir = "/infolab/node4/lukuang/trec_news/data/washington_post/WashingtonPost/data"
    articles = article_generator.generate_from_dir(data_dir,doc_info_map.keys())
    
    if len(articles) != len(doc_info_map):
        print "Warning: Found %d out of %d documents" %(len(articles),len(doc_info_map))

    result_doc_db = redis.Redis(host=RedisDB.host,
                                      port=RedisDB.port,
                                      db=RedisDB.result_doc_db)
    for single_article in articles:
        article_dict = single_article.dict
        docid =   article_dict.pop("docid")
        qid = doc_info_map[docid]["qid"]
        # article_dict["qid"] =  doc_info_map[docid]["qid"]     
        article_dict["phara_ids"] = doc_info_map[docid]["phara_ids"]

        article_json_str = json.dumps(article_dict)

        result_doc_db.hset(qid,docid,article_json_str)
        print "import document %s successful" %(docid)

if __name__=="__main__":
    main()

