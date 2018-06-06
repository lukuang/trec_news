"""
process generated trec documents
"""

import os
import json
import sys
import re
import argparse
import codecs

class BaseTrecDoc(object):
    """
    base class for getting documents
    from generated trec text files 
    """

    def generate_from_dir(self,dir_path,docids=None):
        documents = {}
        for file_path in os.walk(dir_path).next()[2]:
            file_path = os.path.join(dir_path,file_path)
            file_documents = self.generate_from_file(file_path,docids)
            
            documents.update(file_documents)

            # for debug
            # break

        print "There are in total %d documents in dir %s" \
            %(len(documents),dir_path)
        
        return documents

    def generate_from_file(self,file_path,docids=None):
        pass

class ParagraphDoc(BaseTrecDoc):
    """
    get paragraph documents
    """

    def generate_from_file(self,file_path,docids=None):

        print "process %s" %(file_path)
        documents = {}
        docid = ""
        doc_string = ""
        in_text = False
        with codecs.open(file_path,"r","utf-8") as f:
            for line in f:
                if re.match(r'<DOC>', line) :
                    continue
                elif re.match(r'\t<DOCNO>', line) :
                    m_did = re.match(r'\t<DOCNO>(.+?)<\/DOCNO>', line)
                    docid = m_did.group(1)
                    continue
                elif re.match(r'\t<published_date>', line) :
                    continue
                elif re.match(r'\t<TEXT>', line) :
                    in_text = True
                    # print "in text"
                elif re.match(r'\t</TEXT>', line) :
                    documents[docid] = doc_string
                    docid = ""
                    doc_string = ""
                    in_text = False

                    # for debug
                    # break
                elif in_text:
                    doc_string += line
                    # print "add a line"
                

        print "There are %d documents in file %s" \
                        %(len(documents),file_path)
        return documents


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("")
    args=parser.parse_args()

if __name__=="__main__":
    main()

