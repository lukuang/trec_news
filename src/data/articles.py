"""
process Washtington Post articles
"""

import os
import json
import sys
import re
import argparse
import codecs
from bs4 import BeautifulSoup
from HTMLParser import HTMLParser

# according to the guideline,
# articl types to be discarded ( opinion or editorials)
  
DISCARD_TYPES = [
    "Opinion",
    "Letters to the Editor",
    "The Post's View"
]

class ArticleGenerator(object):
    """
    generate articles from file
    """

    def __init__(self):
        self._h =  HTMLParser()

     
    def generate_from_dir(self,dir_path,docids=None):
        articles = []
        for file_path in os.walk(dir_path).next()[2]:
            file_path = os.path.join(dir_path,file_path)
            file_articles = self.generate_from_file(file_path,docids)
            
            articles += file_articles
        
        print "There are in total %d articles in dir %s" \
            %(len(articles),dir_path)
        
        return articles

    def generate_from_file(self,file_path,docids=None):
        
        print "process %s" %(file_path)
        articles = []
        with codecs.open(file_path,"r","utf-8") as f:
            for line in f:
                try:
                    doc_json = json.loads(line)
                except ValueError:
                    # ignore non-json lines
                    pass
                else:
                    title = doc_json["title"]
                    if title is None:
                       title = "" 
                    docid = doc_json["id"]
                    if docids is not None:
                        if docid not in docids:
                            continue
                    published_date = doc_json["published_date"]
                    url = doc_json["article_url"]
                    images = []
                    paragraphs = []
                    discard = False
                    for c in doc_json["contents"]:
                        if c is None:
                            # print "The strange line is:"
                            # print line
                            # skip empty line
                            continue
                        elif c["type"] == "kicker":
                            # ignore some articles with unwanted
                            # types
                            if c["type"] in DISCARD_TYPES:
                                discard = True
                                break
                        elif c["type"] == "image":
                            images.append(c["imageURL"])
                        
                        elif c["type"] == "sanitized_html":
                            if re.match("^http\S+$",c["content"]):
                                continue
                            else:
                                clean_text = BeautifulSoup(c["content"],'lxml').text
                                clean_text = self._h.unescape(clean_text)
                                if re.match("^Read more:", clean_text):
                                    break
                                else:
                                    paragraphs.append(clean_text)

                    if not discard:
                        single_article = Article(title,docid,
                                                 published_date,url,
                                                 images,paragraphs)

                        articles.append(single_article)
                        
                        # for debug purpose
                        # break

        print "There are %d articles in file %s" \
                        %(len(articles),file_path)
        return articles



class Article(object):
    """
    store info of an article
    """
    def __init__(self,title,docid,published_date,url,images,paragraphs):
        self.title, self.docid, self.published_date = \
            title,docid,published_date
        self.url, self.images, self.paragraphs = \
            url,images,paragraphs

    def __str__(self):
        
        return str(self.dict)

    @property
    def dict(self):
        return {
                    "title":self.title,
                    "docid":self.docid,
                    "published_date":self.published_date,
                    "url":self.url,
                    "images":self.images,
                    "paragraphs":self.paragraphs,
                }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dir_path")
    args=parser.parse_args()

    article_generator = ArticleGenerator()
    articles = article_generator.generate_from_dir(args.dir_path)
    for i in articles:
        print i
if __name__=="__main__":
    main()

