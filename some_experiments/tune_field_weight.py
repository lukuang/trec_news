"""
tune field weights (tt, body) for different types of queries
"""

import os
import json
import sys
import re
import argparse
import codecs
import subprocess

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("src_dir")
    parser.add_argument("dest_dir")
    parser.add_argument("--have_weights","-hw",action="store_true")
    parser.add_argument("--qrel_file",default="/infolab/node4/lukuang/trec_news/trec_news/some_experiments/test_qrel")
    args=parser.parse_args()

    for i in range(11):
        weight = .1 * i
        print "For title weight %f:" %(weight)
        dir_name = str(i)
        weight_dest_dir = os.path.join(args.dest_dir,dir_name)
        
        # create necessary directories
        if not os.path.exists(weight_dest_dir):
            os.mkdir(weight_dest_dir)
        
        for sub_dir_name in ["queries","results","top_two_results","top_five_results","merge","performance"]:
            sub_dir = os.path.join(weight_dest_dir,sub_dir_name)
            if not os.path.exists(sub_dir):
                os.mkdir(sub_dir)

        print "\tGenerating query files and run queries"
        for qid in os.walk(args.src_dir).next()[2]:
            # generate field query file
            query_file = os.path.join(args.src_dir,qid)
            dest_query_file = os.path.join(weight_dest_dir,"queries",qid)
            query_gene_args = ["python","generate_field_queries.py", query_file,dest_query_file,"-tw","%f" %(weight) ]
            if args.have_weights:
                query_gene_args.append("-hw")

            subprocess.call(query_gene_args)

            # run query
            dest_result_dir = os.path.join(weight_dest_dir,"results")
            dest_result_file = os.path.join(dest_result_dir,qid)
            run_query_args = "IndriRunQuery %s > %s" %(dest_query_file,dest_result_file)
            subprocess.call(run_query_args,shell=True)



        # get top two
        print "\tFind top two"
        dest_top_two_dir = os.path.join(weight_dest_dir,"top_two_results")
        get_top_two_args = ["python","find_top.py", dest_result_dir,dest_top_two_dir]
        subprocess.call(get_top_two_args)

        # get top two
        print "\tFind top five"
        dest_top_five_dir = os.path.join(weight_dest_dir,"top_five_results")
        get_top_five_args = ["python","find_top.py", dest_result_dir,dest_top_five_dir,"-nt","5"]
        subprocess.call(get_top_five_args)


        # merge two all results
        print "\tMerge"
        merge_dest_dir = os.path.join(weight_dest_dir,"merge") 
        merge_all_dest_file = os.path.join(merge_dest_dir,"merge_all")
        merge_top_two_dest_file = os.path.join(merge_dest_dir,"merge_top_two")
        merge_top_five_dest_file = os.path.join(merge_dest_dir,"merge_top_five")
        get_all_merge_args = ["python","simple_merge_result.py", dest_result_dir,merge_all_dest_file]
        subprocess.call(get_all_merge_args)
        get_top_two_merge_args = ["python","simple_merge_result.py", dest_top_two_dir,merge_top_two_dest_file]
        subprocess.call(get_top_two_merge_args)
        get_top_five_merge_args = ["python","simple_merge_result.py", dest_top_five_dir,merge_top_five_dest_file]
        subprocess.call(get_top_five_merge_args)

        # evaluate
        print "\tEvaluate"
        performance_dir = os.path.join(weight_dest_dir,"performance")
        performance_all_dest_file = os.path.join(performance_dir,"all")
        performance_top_two_dest_file = os.path.join(performance_dir,"top_two")
        performance_top_five_dest_file = os.path.join(performance_dir,"top_five")
        
        eval_all_args = 'trec_eval -q -m ndcg_cut %s %s | grep "ndcg_cut_5 " > %s' %(args.qrel_file,
                                                                                     merge_all_dest_file,
                                                                                     performance_all_dest_file)
        subprocess.call(eval_all_args,shell=True)

        eval_top_two_args = 'trec_eval -q -m ndcg_cut %s %s | grep "ndcg_cut_5 " > %s' %(args.qrel_file,
                                                                                     merge_top_two_dest_file,
                                                                                     performance_top_two_dest_file)
        subprocess.call(eval_top_two_args,shell=True)

        eval_top_five_args = 'trec_eval -q -m ndcg_cut %s %s | grep "ndcg_cut_5 " > %s' %(args.qrel_file,
                                                                                     merge_top_five_dest_file,
                                                                                     performance_top_five_dest_file)
        subprocess.call(eval_top_five_args,shell=True)






if __name__=="__main__":
    main()

