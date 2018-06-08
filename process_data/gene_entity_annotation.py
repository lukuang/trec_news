"""
generate entity annotations for each paragraph
"""

import os
import json
import sys
import re
import argparse
import codecs

sys.path.append("/infolab/node4/lukuang/trec_news/trec_news/src")
from data import ParagraphDoc
from entity import dbpedia

def get_canonical_form(url):
    m = re.search("resource/(.+)$",url)
    return m.group(1)

def get_annotations(para_text,para_id,annotator):
    annotations = []
    
    returned_json = annotator.annotate(para_text)
    try:
        entities = returned_json["Resources"]
    except KeyError:
        pass
    else:
        for entitiy_struct in entities:
            surface_form = entitiy_struct["@surfaceForm"]
            canonical_form = get_canonical_form(entitiy_struct["@URI"])
            start = entitiy_struct["@offset"]
            end = int(start)+len(surface_form)
            end = str(end)
            sinlge_entity_annotation = "%s\t%s\t%s\t%s\t%s" %(para_id,start,end,surface_form,canonical_form)
            annotations.append(sinlge_entity_annotation)
    return annotations   

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("doc_dir")
    parser.add_argument("dest_dir")
    parser.add_argument("--job_id","-j",default=0,type=int)
    parser.add_argument("--number_of_job","-nj",default=1,type=int)
    args=parser.parse_args()

    para_doc = ParagraphDoc()
    annotator = dbpedia.EntityAnnotator()
    count = 0
    if args.number_of_job <= args.job_id:
        error_str = "Job id cannot be larger or equal to the number of jobs!\n"
        error_str += "Job id: %d, number of job:%d\n" %(args.job_id,args.number_of_job)
        raise ValueError(error_str)
    for file_name in os.walk(args.doc_dir).next()[2]:
            file_path = os.path.join(args.doc_dir,file_name)
            # docs = para_doc.generate_from_dir(args.doc_dir)
            dest_file = os.path.join(args.dest_dir,file_name)
            count += 1
            if count %args.number_of_job != args.job_id:
                print "Skip %s, it belongs to other jobs" %(dest_file)
                continue
            if os.path.exists(dest_file): 
                print "Skip existing file %s" %(dest_file)
                continue
            docs = para_doc.generate_from_file(file_path)
            with codecs.open(dest_file,"w",'utf-8') as of:
                for para_id in docs:
                    para_text = docs[para_id]
                    annotations = get_annotations(para_text,para_id,
                                                  annotator)
                    for a in annotations:
                        of.write(a+"\n")



if __name__=="__main__":
    main()

