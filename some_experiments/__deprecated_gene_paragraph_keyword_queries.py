"""
Generate queries for each paragraph to get scores of 
para vs. doc and para vs. para
"""

import os
import json
import sys
import re
import argparse
import codecs
from lxml import etree
import copy

def setup_weight(title_weight,have_weights):
    body_weight = 1.0 - title_weight
    def give_field_weight(text_string_match):
        text_string = text_string_match.group(2)
        replace_string = ""
        if have_weights:
            weight = 0.0
            is_weight = True
            for match in re.findall("\S+",text_string):
                if is_weight:
                    weight = float(match) 
                else:
                    new_title_weight = weight*title_weight
                    replace_string += "%f %s.(tt) " %(new_title_weight, match)
                    new_body_weight = weight*body_weight
                    replace_string += "%f %s.(body) " %(new_body_weight, match)

                is_weight = not is_weight
            return "#weight(%s)" %(replace_string)
        else:
            for match in re.findall("\S+",text_string):
                replace_string += "%f %s.(tt) " %(title_weight, match)
                replace_string += "%f %s.(body) " %(body_weight, match)
            return "#combine(%s)" %(replace_string)
                    

    return give_field_weight

def generate_doc_query_etree(doc_query_root,give_field_weight,search_index):
    doc_query_root.find("count").text = "500"
    doc_query_root.find("index").text = search_index
    for query in doc_query_root.iterfind("query"):
        query_string = query.find("text").text
        m = re.search("#(weight|combine)\(([^\)]+)\)",query_string)
        query_string = re.sub("#(weight|combine)\(([^\)]+)\)",give_field_weight,query_string)
        query_string = re.sub("#less","#equals",query_string)
        query.find("text").text = query_string

    return doc_query_root

def generate_para_query_etree(para_query_root,para_index):
    para_query_root.find("index").text = para_index
    para_query_root.find("count").text = "500"

    for query in para_query_root.iterfind("query"):
        query_string = query.find("text").text
        query_string = re.sub("#less","#equals",query_string)
        query.find("text").text = query_string

    return para_query_root

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("src_dir")
    parser.add_argument("dest_dir")
    parser.add_argument("--index_type","-it",choices=range(2),default=0,type=int,
        help="""
            Choose the index type:
                0: normal
                1: annotated
        """)
    parser.add_argument("--para_root_index",default="/infolab/node4/lukuang/trec_news/data/washington_post/paragraph_index/")
    parser.add_argument("--search_root_index",default="/infolab/node4/lukuang/trec_news/data/washington_post/index/")
    parser.add_argument("--have_weights","-hw",action="store_true")
    parser.add_argument("--title_weight","-tw",type=float,default=0.7,
        help="""
            weight of the title field (form 0.0 to 1.0)
            default set to 0.7, best for raw searching
        """
        )
    args=parser.parse_args()

    doc_query_dir = os.path.join(args.dest_dir,"doc_query")
    para_query_dir = os.path.join(args.dest_dir,"para_query")
    give_field_weight = setup_weight(args.title_weight, args.have_weights)
    
    if args.index_type == 0:
        para_index = os.path.join(args.para_root_index,"v2")
        search_index = os.path.join(args.search_root_index,"v2")

    else:
        para_index = os.path.join(args.para_root_index,"annotated")
        search_index = os.path.join(args.search_root_index,"annotated")
   

    print "\tGenerating query files and run queries"
    for qid in os.walk(args.src_dir).next()[2]:
        # generate field query file
        query_file = os.path.join(args.src_dir,qid)
        dest_doc_query_file = os.path.join(doc_query_dir,qid)
        dest_para_query_file = os.path.join(para_query_dir,qid)
        
        with open(query_file) as f:
            doc_query_root = etree.parse(f)

            para_query_root = copy.deepcopy(doc_query_root)
            
            para_query_root = generate_para_query_etree(para_query_root,para_index)

            doc_query_root = generate_doc_query_etree(doc_query_root,give_field_weight,search_index)


            with open(dest_doc_query_file,"w") as dqf:
               dqf.write( etree.tostring(doc_query_root, pretty_print=True))
            
            with open(dest_para_query_file,"w") as dqf:
               dqf.write( etree.tostring(para_query_root, pretty_print=True))

if __name__=="__main__":
    main()

