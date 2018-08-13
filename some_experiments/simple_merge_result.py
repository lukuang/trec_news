"""
merge_results from paragraphs depending on 
1. votes from paragraphs
2. relevance score to paragraphs
"""

import os
import json
import sys
import re
import argparse
import codecs
from collections import Counter,defaultdict

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("src_dir")
    parser.add_argument("dest_file")
    parser.add_argument("--run_tag","-rt",default="test")
    parser.add_argument("--how_to_merge","-hm",default=1,choices=range(2),type=int,
            help="""
                Choose how to merge the results:
                    0: vote + highest score,
                    1: highest score
            """)
    args=parser.parse_args()

    with open(args.dest_file,"w") as of:

        for qid in os.walk(args.src_dir).next()[2]:
            src_file = os.path.join(args.src_dir,qid)

            line_prefix = "%s\tQ0" %(qid)
            
            counts = Counter()
            scores = Counter()
            total_doc_count = 0
            with open(src_file) as f:
                for line in f:
                    total_doc_count += 1
                    parts = line.strip().split()
                    docid = parts[2]
                    score = float(parts[4])

                    counts[docid] += 1 
                    scores[docid] = max(score, scores[docid])

            if args.how_to_merge == 0:
                dict_to_rank = defaultdict(dict)
                for docid in counts:
                    count = counts[docid]
                    dict_to_rank[count][docid] = scores[docid]

                rank = 1
                rank_score = total_doc_count
                for dict_tuple in sorted(dict_to_rank.items(),key=lambda x:x[0],reverse=True):
                    score_dict = dict_tuple[1]
                    for score_tuple in sorted(score_dict.items(),key=lambda x:x[1],reverse=True):
                        docid = score_tuple[0]

                        line = "%s\t%s\t%d\t%d\t%s\n" %(line_prefix,docid,rank,rank_score,args.run_tag)
                        rank += 1
                        rank_score -= 1
                        of.write(line)
            else:
                rank = 1
                for score_tuple in sorted(scores.items(),key=lambda x:x[1],reverse=True):
                    docid = score_tuple[0]
                    rank_score = score_tuple[1]
                    line = "%s\t%s\t%d\t%f\t%s\n" %(line_prefix,docid,rank,rank_score,args.run_tag)
                    rank += 1
                    of.write(line)


if __name__=="__main__":
    main()

