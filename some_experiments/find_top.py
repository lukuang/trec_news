"""
find top results for each paragraphs. 
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
    parser.add_argument("src_dir")
    parser.add_argument("dest_dir")
    parser.add_argument("--number_of_top","-nt",type=int,default=5)
    args=parser.parse_args()

    for file_name in os.walk(args.src_dir).next()[2]:
        src_file = os.path.join(args.src_dir,file_name)
        dest_file = os.path.join(args.dest_dir,file_name)


        result_dict = {}
        output_lines = []

        with open(src_file) as f:
            for line in f:
                parts = line.strip().split()
                qid = parts[0]
                score = float(parts[4])
                if qid not in result_dict:
                    result_dict[qid] = set()
                if len(result_dict[qid]) >=args.number_of_top:
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

