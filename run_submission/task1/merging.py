"""
merge ranked results for paragraphs to a single result
list of a query
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
    parser.add_argument("--merge_cutoff","-mt",type=int,default=5)
    parser.add_argument("--how_to_merge","-hm",default=1,choices=range(4),type=int,
            help="""
                Choose how to merge the results:
                    0: vote + highest score,
                    1: highest score
                    2: simple merging formula based on
                        Jamie Callan's Paper (eq 5.10)
                    3: first result
            """)
    args=parser.parse_args()

    result_limit = 100
    with open(args.dest_file,"w") as of:
        for qid in os.walk(args.src_dir).next()[2]:
            src_file = os.path.join(args.src_dir,qid)
            print "process file %s" %(src_file)

            line_prefix = "%s\tQ0" %(qid)
            
            counts = Counter()
            max_scores = Counter()
            all_doc_scores = defaultdict( lambda: defaultdict(list))
            para_scores = defaultdict(list)
            score_struct = defaultdict( lambda: defaultdict(dict))
            total_doc_count = 0
            with open(src_file) as f:
                for line in f:
                    total_doc_count += 1
                    parts = line.strip().split()
                    pid = parts[0]
                    docid = parts[2]
                    score = float(parts[4])

                    counts[docid] += 1 
                    max_scores[docid] = max(score, max_scores[docid])
                    
                    # if len(para_scores[pid]) < 5:
                    score_struct[pid][score] = docid
                    para_scores[pid].append(score)
                    all_doc_scores[docid][pid] = score

            if args.how_to_merge == 0:
                dict_to_rank = defaultdict(dict)
                for docid in counts:
                    count = counts[docid]
                    dict_to_rank[count][docid] = max_scores[docid]

                rank = 1
                rank_score = total_doc_count
                for dict_tuple in sorted(dict_to_rank.items(),key=lambda x:x[0],reverse=True):
                    
                    score_dict = dict_tuple[1]
                    for score_tuple in sorted(score_dict.items(),key=lambda x:x[1],reverse=True):
                        docid = score_tuple[0]
                        if rank > result_limit:
                            continue
                        line = "%s\t%s\t%d\t%d\t%s\n" %(line_prefix,docid,rank,rank_score,args.run_tag)
                        rank += 1
                        rank_score -= 1
                        of.write(line)
            elif args.how_to_merge == 1:
                rank = 1
                for score_tuple in sorted(max_scores.items(),key=lambda x:x[1],reverse=True):
                    if rank > result_limit:
                        continue
                    docid = score_tuple[0]
                    rank_score = score_tuple[1]
                    line = "%s\t%s\t%d\t%f\t%s\n" %(line_prefix,docid,rank,rank_score,args.run_tag)
                    rank += 1
                    of.write(line)
            elif args.how_to_merge == 2:
                num_of_para = len(para_scores)
                para_avg_scores = {}
                for pid in para_scores:
                    para_avg_scores[pid] = sum(para_scores[pid])*1.0/args.merge_cutoff

                avg_para_score = sum(para_avg_scores.values())*1.0/num_of_para
                
                para_score_normalizer = {}
                for pid in para_avg_scores:
                    para_score_normalizer[pid] = num_of_para
                    para_score_normalizer[pid] *= para_avg_scores[pid]- avg_para_score
                    para_score_normalizer[pid] /= avg_para_score

                # print "Sorted paragraph scores for %s:" %(qid)
                # print sorted(para_avg_scores.items(),key=lambda x:x[1],reverse=True)
                # print sorted(para_score_normalizer.items(),key=lambda x:x[1],reverse=True)
                normalized_doc_scores = Counter()
                for docid in all_doc_scores:
                    for pid in all_doc_scores[docid]:
                        score = all_doc_scores[docid][pid]
                        doc_score_for_para = score* (1 + para_score_normalizer[pid] )
                        # if docid == "69d38a664cdb53d0e75b9f2101d7ad62" or docid == "667f6e0670afc0372ee886059b96d4c6":
                        #     print "compute %s:" %(docid)
                        #     print "%f *(1 + %f)" %(score,para_score_normalizer[pid])

                        normalized_doc_scores[docid] = max(normalized_doc_scores[docid],doc_score_for_para)

                rank = 1
                for score_tuple in sorted(normalized_doc_scores.items(),key=lambda x:x[1],reverse=True):
                    if rank > result_limit:
                        continue
                    docid = score_tuple[0]
                    rank_score = score_tuple[1]
                    line = "%s\t%s\t%d\t%f\t%s\n" %(line_prefix,docid,rank,rank_score,args.run_tag)
                    rank += 1
                    of.write(line)

            elif args.how_to_merge == 3:
                rank_docs = []
                changed = True
                # print "totlal count %d" %(total_doc_count)
                while changed:
                    round_docs = {}
                    for pid in score_struct.keys():
                        if score_struct[pid]:
                            first_score = max(score_struct[pid].keys())
                            docid = score_struct[pid][first_score]
                            round_docs[docid] = first_score
                            score_struct[pid].pop(first_score,None)
                        else:
                            score_struct.pop(pid,None)

                    # print "totlal count %d" %(total_doc_count)
                    for score_tuple in sorted(round_docs.items(),key=lambda x:x[1],reverse=True):
                        docid = score_tuple[0]
                        if docid not in rank_docs:
                            rank_docs.append(docid)
                    changed = (len(score_struct) != 0)
                rank_score = len(rank_docs)
                rank = 1
                for docid in rank_docs:
                    if rank > result_limit:
                        continue
                    line = "%s\t%s\t%d\t%f\t%s\n" %(line_prefix,docid,rank,rank_score,args.run_tag)
                    rank_score -= 1
                    rank += 1
                    of.write(line)

if __name__=="__main__":
    main()

