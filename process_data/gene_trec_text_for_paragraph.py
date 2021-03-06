"""
generate trec text and create a trec doc for each
paragraph for the Washington Post collection
"""

import os
import json
import sys
import re
import argparse
import codecs
import redis
from string import Template
# from myUtility import indri
# from myUtility.indri import TextFactory 

sys.path.append("/infolab/node4/lukuang/trec_news/trec_news/src")
from data import ArticleGenerator, Article

sys.path.append("/infolab/node4/lukuang/trec_news/trec_news/src")
from config.db import RedisDB

text_template = Template("""
<DOC>
\t<DOCNO>$did</DOCNO>
\t<published_date>$published_date</published_date>
\t<TEXT>
\t$body
\t</TEXT>
</DOC>\n""")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("doc_dir")
    parser.add_argument("dest_dir")
    args=parser.parse_args()

    #load the testing query document
    bl_query_db = redis.Redis(host=RedisDB.host,
                                 port=RedisDB.port,
                                 db=RedisDB.bl_query_db)

    required_docids = set()
    for qid in bl_query_db.keys():
        query_string = bl_query_db.get(qid)
        query_json = json.loads(query_string)
        docid = query_json["docid"]
        required_docids.add(docid)

    for file_name in sorted(os.walk(args.doc_dir).next()[2]):
        file_path = os.path.join(args.doc_dir,file_name)
        dest_file = os.path.join(args.dest_dir,file_name)
        if os.path.exists(dest_file):
            print "Skip an existing file %s" %(file_name)
            continue

        article_generator = ArticleGenerator(required_docids)
        articles = article_generator.generate_from_file(file_path)
        
        count = 0
        with codecs.open(dest_file,"w",'utf-8') as of:
            for doc in articles:
                pid = 0
                did = doc.docid
                published_date = doc.published_date
                for p in doc.paragraphs:

                    p_docid = "%s-%d" %(did,pid)
                    body = p
                    pid += 1
                    text = text_template.substitute(did=p_docid,
                                                    published_date=published_date,
                                                    body=body)
            
                    of.write(text)
                count += 1
                if count%10000 == 0:
                    print "wrote %d documents" %(count)



if __name__=="__main__":
    main()

