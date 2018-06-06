"""
find first two result for each paragraphs. 
We need first two since the first one might 
be the original article
"""

import os
import json
import sys
import re
import argparse
import codecs

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("src_file")
    args=parser.parse_args()

    dest_file = args.src_file+"_top_two"

    result_dict = {}
    output_lines = []

    with open(args.src_file) as f:
        for line in f:
            parts = line.strip().split()
            qid = parts[0]
            score = float(parts[4])
            if qid not in result_dict:
                result_dict[qid] = set()
            if len(result_dict[qid]) >=2:
                continue
            elif score in result_dict[qid]:
                continue
            else:
                result_dict[qid].add(score)
                output_lines.append(line)

    with open(dest_file,"w") as of:
        for line in output_lines:
            of.write(line)

if __name__=="__main__":
    main()

