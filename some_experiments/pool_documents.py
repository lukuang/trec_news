"""
pool documents to be judged
"""

import os
import json
import sys
import re
import argparse
import codecs
from collections import Counter,defaultdict
import subprocess

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qrel_file",default="/infolab/node4/lukuang/trec_news/trec_news/some_experiments/test_qrel")
    parser.add_argument("--pool_depth","-pd",type=int,default=5)
    parser.add_argument("src_dir")
    parser.add_argument("dest_file")
    args=parser.parse_args()

    print "Get judged documents"
    judged_docids = defaultdict(list)
    with open(args.qrel_file) as f:
        for line in f:
            parts = line.split()
            qid = parts[0]
            docid = parts[2]
            judged_docids[qid].append(docid)

    print "Get all merged files to be pooled"
    find_file_args = "find %s -type f -name merge*" %(args.src_dir)
    p1 = subprocess.Popen(find_file_args, shell=True,stdout=subprocess.PIPE)
    output = p1.communicate()[0]
    file_list = [x.strip() for x in output.split()]

    print "Get unjudged documents"
    unjudged_docids = defaultdict(Counter)
    for merge_file in file_list:
        # merge_file = os.path.join(args.src_dir,merge_file_name)
        with open(merge_file)  as f:
            file_docids = defaultdict(int)
            for line in f:
                parts = line.split()
                qid = parts[0]
                docid = parts[2]
                file_docids[qid] += 1
                if file_docids[qid] > args.pool_depth:
                    continue
                if docid not in judged_docids[qid]:
                    unjudged_docids[qid][docid] += 1

    print "Write the results to file"
    with open(args.dest_file,"w") as of:
        for qid in unjudged_docids:
            for e in unjudged_docids[qid].most_common():
                docid = e[0]
                count = e[1]
                of.write("%s\t%s\t%d\n" %(qid,docid,count))


if __name__=="__main__":
    main()

