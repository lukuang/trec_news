"""
generate title entity annotation
"""

import os
import json
import sys
import re
import argparse
import codecs
import subprocess
import gc
import copy
# from guppy import hpy

sys.path.append("/infolab/node4/lukuang/trec_news/trec_news/src")
from entity import dbpedia

def get_job_titles(all_titles,number_of_job,job_id):
    count = 0
    titles = []
    for title_struct in all_titles:
        count += 1
        if count %number_of_job != job_id:
            continue
        else:
            titles.append(title_struct)

    return titles

def get_all_titles(collection_dump):
    with open(collection_dump) as f:
        collection = json.load(f)
    print "collection loaded"
    all_titles = []
    for docid in sorted(collection.keys()):
        # print docid
        
        docid = copy.copy(docid)
        all_titles.append((docid,copy.copy(collection[docid]["title"])))
        collection.pop(docid,None)
        # break
    collection = []
    gc.collect()

    
    return all_titles

def get_canonical_form(url):
    m = re.search("resource/(.+)$",url)
    return m.group(1)

def get_annotations(title_text,docid,annotator):
    annotations = []
    
    returned_json = annotator.annotate(title_text)
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
            sinlge_entity_annotation = "%s\t%s\t%s\t%s\t%s" %(docid,start,end,surface_form,canonical_form)
            annotations.append(sinlge_entity_annotation)
    return annotations  

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection_dump","-cd",default="/infolab/node4/lukuang/trec_news/data/washington_post/collection_json_dump/v2/dump")
    parser.add_argument("--job_id","-j",default=0,type=int)
    parser.add_argument("--number_of_job","-nj",default=1,type=int)
    parser.add_argument("dest_file")
    parser.add_argument("title_file")
    args=parser.parse_args()

    
    if args.number_of_job <= args.job_id:
        error_str = "Job id cannot be larger or equal to the number of jobs!\n"
        error_str += "Job id: %d, number of job:%d\n" %(args.job_id,args.number_of_job)
        raise ValueError(error_str)

    if not os.path.exists(args.title_file):
        all_titles = get_all_titles(args.collection_dump)
        with codecs.open(args.title_file,"w","utf-8") as f:
            f.write(json.dumps(all_titles))
    else:
        all_titles=json.load(codecs.open(args.title_file,"r","utf-8"))

    print "get all titles"
    titles = get_job_titles(all_titles,args.number_of_job,args.job_id)
    print len(titles)
    # subprocess.call("free -mh")
    print "title loaded"
    # hp = hpy()
    # h = hp.heap()
    # print h
    annotator = dbpedia.EntityAnnotator()
    with codecs.open(args.dest_file,"w","utf-8") as of:
        for title_struct in titles:
            docid = title_struct[0]
            title = title_struct[1]
            annotations = get_annotations(title,docid,annotator)
            for sinlge_entity_annotation in annotations:
                of.write(sinlge_entity_annotation+"\n")

if __name__=="__main__":
    main()

