"""
generate trec text from the Washington Post collection
"""

import os
import json
import sys
import re
import argparse
import codecs
from string import Template
# from myUtility import indri
# from myUtility.indri import TextFactory 

sys.path.append("/infolab/node4/lukuang/trec_news/trec_news/src")
from data import ArticleGenerator, Article

text_template = Template("""
<DOC>
\t<DOCNO>$did</DOCNO>
\t<published_date>$published_date</published_date>
\t<TEXT>
\t\t<tt>$tt</tt>
\t\t<body>$body</body>
\t</TEXT>
</DOC>\n""")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("doc_dir")
    parser.add_argument("dest_dir")
    args=parser.parse_args()

    for file_name in os.walk(args.doc_dir).next()[2]:
        file_path = os.path.join(args.doc_dir,file_name)
        dest_file = os.path.join(args.dest_dir,file_name)
        if os.path.exists(dest_file):
            print "Skip an existing file %s" %(file_name)
            continue

        article_generator = ArticleGenerator()
        articles = article_generator.generate_from_file(file_path)
        
        count = 0
        with codecs.open(dest_file,"w",'utf-8') as of:
            for doc in articles:
                did = doc.docid
                published_date = doc.published_date
                tt = doc.title
                body = "\n".join(doc.paragraphs)
                
                text = text_template.substitute(did=did,published_date=published_date,
                                             tt=tt,body=body)
        
                of.write(text)
                count += 1
                if count%10000 == 0:
                    print "wrote %d documents" %(count)



if __name__=="__main__":
    main()

