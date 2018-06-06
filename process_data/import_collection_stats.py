"""
import collection stats
"""

import os
import json
import sys
import re
import argparse
import codecs
import redis
import subprocess

sys.path.append("/infolab/node4/lukuang/trec_news/trec_news/src")
from config.db import RedisDB

def load_stopwords(new_path=None):
    if new_path:
        file_path = new_path
    else:
        file_path = "/infolab/node4/lukuang/trec_news/data/other/stopwords.json"
    stopwords = json.load(open(file_path))
    return stopwords

def get_pwc(index_dir):
    """
    get pwc from index
    """
    pwc = {}
    p1 = subprocess.Popen(["dumpindex",index_dir,"v"], stdout=subprocess.PIPE)
    # output = p1.communicate()[0]
    total = .0
    for line in iter(p1.stdout.readline,''):
        parts = line.split()
        if parts[0] == "TOTAL":
            total = float(parts[1])

            # store a value for out of vocabulary words
            pwc["[OOV]"] = 1000.0/total
        else:
            stem = parts[0]
            try:
                stem_frequency = int(parts[1])
            except Exception:
                print line
                print parts
                sys.exit(-1)
            pwc[stem] = stem_frequency/total
    return pwc

def main():

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index_dir","-id",default="/infolab/node4/lukuang/trec_news/data/washington_post/index")
    parser.add_argument("--stopwords_path")
    args=parser.parse_args()

    collection_stats_db = redis.Redis(host=RedisDB.host,
                         port=RedisDB.port,
                         db=RedisDB.collection_stats_db)

    stopwords = load_stopwords(args.stopwords_path)
    pwc =  get_pwc(args.index_dir)

    
    # import stopwords
    print "import stopwords"
    collection_stats_db.sadd("stopwords",*stopwords.keys())
    
    # import pwc
    size = len(pwc)
    print "There are %d words" %(size)
    
    percentage = int(0.1*size)
    count = 0
    
    for w in pwc:
        if w in stopwords:
            continue
        value = pwc[w]
        collection_stats_db.hset("pwc",w,value)
        count += 1
        if count%percentage==0:
            print "\rhave process %.2f%%" %(100.0*count/size)




if __name__=="__main__":
    main()

