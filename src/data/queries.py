"""
class for processing query files
"""

import os
import json
import sys
import re
import argparse
import codecs
import xml.etree.ElementTree as ET

class NewsQueryBase(object):
    """
    base class for processing
    news query file
    """
    def __init__(self,query_file):
        self._query_file = query_file
        self._queries = []
        self._process_query_file()

    def _process_query_file(self):
        pass
        
    @property
    def queries(self):
        return self._queries


class BQuery(NewsQueryBase):
    """
    class for handling query file 
    of background linking
    """
    def __init__(self,bquery_file):
        super(BQuery, self).__init__(bquery_file)

    def _process_query_file(self):
        doc_string = ""
        with open(self._query_file) as f:
            doc_string = f.read()
            doc_string = "<query>\n%s</query>" %(doc_string)
        root = ET.fromstring(x)
        for query in root:
            qid_string =  root.find("num").text
            qid_string = re.sub("Number:","",qid_string)
            qid = re.search("\w+",qid_string).group(0)

            docid = root.find("docid").text
            url = root.find("url").text
            single_query = {
                                "qid":qid,
                                "docid":docid,
                                "url":url
                            }
            self._queries.append(single_query)

class EQuery(NewsQueryBase):
    """
    class for handling query file 
    of entity ranking
    """
    def __init__(self,bquery_file):
        super(BQuery, self).__init__(bquery_file)

    def _process_query_file(self):
        doc_string = ""
        with open(self._query_file) as f:
            doc_string = f.read()
            doc_string = "<query>\n%s</query>" %(doc_string)
        root = ET.fromstring(x)
        for query in root:
            qid_string =  root.find("num").text
            qid_string = re.sub("Number:","",qid_string)
            qid = re.search("\w+",qid_string).group(0)

            docid = root.find("docno").text
            url = root.find("url").text
            single_query = {
                                "qid":qid,
                                "docid":docid,
                                "url":url
                            }
            self._queries.append(single_query)





def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("")
    args=parser.parse_args()

if __name__=="__main__":
    main()

