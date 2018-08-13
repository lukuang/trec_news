"""
dump annotated collection to a json file
"""

import os
import json
import sys
import re
import argparse
import codecs
from collections import defaultdict
from string import Template
import gc

sys.path.append("/infolab/node4/lukuang/trec_news/trec_news/src")
from data import ParagraphDoc
from entity import dbpedia



def get_cannonical_form(url):
    m = re.search("resource/(.+)$",url)
    return m.group(1)

def get_annotation_from_text(text,annotator):
    text_entities = []
    
    returned_json = annotator.annotate(text)
    try:
        entities = returned_json["Resources"]
    except KeyError:
        pass
    else:
        for entitiy_struct in entities:
            surface_form = entitiy_struct["@surfaceForm"]
            cannonical_form = get_cannonical_form(entitiy_struct["@URI"])
            start = entitiy_struct["@offset"]
            end = int(start)+len(surface_form)
            single_entity = {
                "cannonical":cannonical_form,
                "start" : start,
                "end" : end,
                "string" : surface_form
            }
            text_entities.append(single_entity)
    return text_entities

def read_title_entity_annotation(title_entity_file):
    title_entities = defaultdict(list)
    with open(title_entity_file) as f:
        for line in f:
            parts = line.split()
            docid = parts[0]
            entity_start = parts[1]
            entity_end = parts[2]
            entity_string = parts[3]
            entity_cannonical = parts[4]
            single_entity = {
                                "cannonical":entity_cannonical,
                                "start" : int(entity_start),
                                "end" : int(entity_end),
                                "string" : entity_string
                            }
            title_entities[docid].append(single_entity)
                    
    return title_entities

def read_paragraph_entity_annotation(entity_file):
    pharagraph_entities = defaultdict(lambda: defaultdict(list))
    with open(entity_file) as f:
        for line in f:
            parts = line.split()
            phara_id = parts[0]
            entity_start = parts[1]
            entity_end = parts[2]
            entity_string = parts[3]
            entity_cannonical = parts[4]
            m = re.match("^(.+)-(\d+)",phara_id)
            try:
                docid = m.group(1)
                pid = int(m.group(2))
            except AttributeError:
                print "Malformatted line!"
                print line
            else:
                
                single_entity = {
                    "cannonical":entity_cannonical,
                    "start" : int(entity_start),
                    "end" : int(entity_end),
                    "string" : entity_string
                }
                pharagraph_entities[docid][pid].append(single_entity)
                    
    return pharagraph_entities

def annotating_entity(entity):
    """
    annotated entity with 'ENT' and the beginning and end
    Other non-word symbols ('_' included) are also replaced with it
    """
    entity = re.sub("[^0-9a-zA-Z]+", "ENT", entity)
    return " ENT%sENT " %(entity)

def annotating_text(text,entity_info):
    annotated_text = ""
    last_index = 0
    for e in entity_info:
        annotated_text += text[last_index:e["start"]-1]
        annotated_text += annotating_entity(e["cannonical"])
        last_index = e["end"]
    annotated_text += text[last_index:]
    return annotated_text

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection_dump","-cd",default="/infolab/node4/lukuang/trec_news/data/washington_post/collection_json_dump/v2/dump")
    parser.add_argument("--pharagraph_entity_dir","-ed",default="/infolab/node4/lukuang/trec_news/data/washington_post/paragraph_entities")
    parser.add_argument("--title_entity_file","-tf",default="/infolab/node4/lukuang/trec_news/data/washington_post/title_entities/title_entities")
    parser.add_argument("dest_file")
    args=parser.parse_args()

    collection = json.load(open(args.collection_dump))
    print "collection loaded"

    
    
    docids_with_entities = set()
    title_entities = read_title_entity_annotation(args.title_entity_file)
    for file_name in os.walk(args.pharagraph_entity_dir).next()[2]:
        print "read from file %s" %(file_name)
        entity_file = os.path.join(args.pharagraph_entity_dir,file_name)
        pharagraph_entities = read_paragraph_entity_annotation(entity_file)
        
        for docid in pharagraph_entities:
            # print "For document %s" %(docid)
            doc = collection[docid]
            docids_with_entities.add(docid)
            # print "print results only for paragraphs with entities"
            annotated_paragraphs = []

            for pid,paragraphs in enumerate(doc["paragraphs"]):
                # print len(doc["paragraphs"])
                # print type(doc["paragraphs"]),type(pid)
                # print pid
                # print paragraphs
                para_text = doc["paragraphs"][pid]
                if pid not in pharagraph_entities[docid]:
                    annotated_paragraphs.append(para_text)
                else:        
                    annotated_paragraphs.append(annotating_text(para_text,pharagraph_entities[docid][pid]))    
                    
            # get annotated title
            title_text = doc["title"]
            if title_entities[docid]:
                title_text = annotating_text(title_text, title_entities[docid])

            collection[docid]["title"] = title_text
            collection[docid]["paragraphs"] = annotated_paragraphs
               

    # process the documents without entities in their paragraphs
    for docid in collection:
        if docid not in docids_with_entities:
            doc = collection[docid]
            # print "print results only for paragraphs with entities"

            
            title_text = doc["title"]
            if title_entities[docid]:
                title_text = annotating_text(title_text, title_entities[docid])
            
            collection[docid]["title"] = title_text

    # docids_with_entities = ""
    dum_json_string = json.dumps(collection)
    # collection = ""
    del collection
    del docids_with_entities
    gc.collect()
    print "Dump the annotated collection!"
    with codecs.open(args.dest_file,"w",'utf-8') as of:
        of.write(dum_json_string)

if __name__=="__main__":
    main()

