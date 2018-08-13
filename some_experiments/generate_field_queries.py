"""
from non-field queries to field queries (tt,body)
"""

import os
import json
import sys
import re
import argparse
import codecs
from lxml import etree

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

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("src_file")
    parser.add_argument("dest_file")
    parser.add_argument("--have_weights","-hw",action="store_true")
    parser.add_argument("--title_weight","-tw",type=float,default=0.5,
        help="""
            weight of the title field (form 0.0 to 1.0)
        """
        )
    args=parser.parse_args()

    if args.title_weight < 0.0 or args.title_weight > 1.0:
        raise ValueError("weight of the title field should be form 0.0 to 1.0")
    
    give_field_weight = setup_weight(args.title_weight, args.have_weights)
    with open(args.src_file) as f:
        root = etree.parse(f)
        for query in root.iterfind("query"):
            query_string = query.find("text").text
            query_string = re.sub("#(weight|combine)\(([^\)]+)\)",give_field_weight,query_string)
            # print query_string
            query.find("text").text = query_string

        with open(args.dest_file,"w") as of:
            of.write( etree.tostring(root, pretty_print=True) )


if __name__=="__main__":
    main()

