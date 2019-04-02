"""
generate index
"""

import os
import json
import sys
import re
import argparse
import codecs
# import myUtility
from myUtility.misc import gene_indri_index_para_file


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("corpus_dir")

    parser.add_argument("index_dir")
    parser.add_argument("--indri_para_path","-if",default="./index.para")
    parser.add_argument("--use_stopwords","-s",action="store_true")
    parser.add_argument("--index_type","-it",choices=range(2),default=0,type=int,
        help="""
            Choose the query type:
                0: articles
                1: paragraphs
        """)
    args=parser.parse_args()

    field_data = []
    field_data.append({"name":"published_date","type":"numeric"})
    if args.index_type == 0:
        field_data.append({"name":"tt","type":"text"})
        field_data.append({"name":"body","type":"text"})
    gene_indri_index_para_file(args.corpus_dir,args.indri_para_path,
                               args.index_dir,field_data=field_data,use_stopper=args.use_stopwords)

if __name__=="__main__":
    main()

