"""
annotate entities using dbpedia spotlight
"""

import os
import json
import sys
import re
import argparse
import codecs
from string import Template
import subprocess

cmd_template = Template('curl -s http://$host:$port/rest/annotate   -H "Accept: application/json"   --data-urlencode "text=$text" --data "confidence=$confidence"')

class EntityAnnotator(object):
    """
    use dbpedia spotlight to
    annotate entities
    """
    def __init__(self,config=None):
        if config is None:
            self._config = EntityAnnotator.Config()
        else:
            self._config = config 

    @classmethod
    def Config(cls,confidence=0.5,host="headnode",port=2222):
        config = {
            "confidence" : str(confidence),
            "host":host,
            "port":str(port)
        }
        return config

    def annotate(self,input_text):
        input_text = input_text.replace('"',r'\"')
        cmd = cmd_template.substitute(host=self._config["host"],
                                      port=self._config["port"],
                                      confidence=self._config["confidence"],
                                      text=input_text)
        p1 = subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE)
        output = p1.communicate()[0]
        try:
            returned_json = json.loads(output)
        except ValueError:
            print "error text:"
            print input_text
            return {}
        else:
            return returned_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("")
    args=parser.parse_args()

if __name__=="__main__":
    main()

