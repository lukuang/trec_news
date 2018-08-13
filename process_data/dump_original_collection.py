"""
dump all the articles in the original collection to a json file
"""

import os
import json
import sys
import re
import argparse
import codecs

sys.path.append("/infolab/node4/lukuang/trec_news/trec_news/src")
from data import ArticleGenerator,Article

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data_dir","-dr",default="/infolab/node4/lukuang/trec_news/data/washington_post/WashingtonPost/v2/data")
    parser.add_argument("dump_dest")
    args=parser.parse_args()

    article_generator = ArticleGenerator()

    articles = article_generator.generate_from_dir(args.data_dir)
    
    print "There are  %d documents" %(len(articles))

    article_jsons = {}
    for single_article in articles:
        article_dict = single_article.dict
        docid = article_dict['docid']
        article_jsons[docid] = article_dict

    with open(args.dump_dest,"w") as f:
        f.write(json.dumps(article_jsons))

        # print "import document %s successful" %(docid)



if __name__=="__main__":
    main()

