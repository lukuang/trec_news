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
from SPARQLWrapper import SPARQLWrapper, JSON

cmd_template = Template('curl -s http://$host:$port/rest/annotate   -H "Accept: application/json"   --data-urlencode "text=$text" --data "confidence=$confidence"')


class TypeGettor(object):
    """get the type of an entity
    """
    def __init__(self,end_point="http://dbpedia.org/sparql"):
        self._end_point = end_point
        self._sparql =  SPARQLWrapper(self._end_point)

        self._query_template = Template("""
                SELECT ?type
                WHERE {
                  <http://dbpedia.org/resource/$entity> rdf:type ?type.
                } LIMIT 100
            """)

    def get_entity_types(self,entity_string):
        entity_types = []
        self._sparql.setQuery(self._query_template.substitute(entity=entity_string))
        self._sparql.setReturnFormat(JSON)
        results = self._sparql.query().convert()
        if len(results["results"]["bindings"]) == 0:
            print 'Warning: no result for %s!' %()
            print results
        for result in results["results"]["bindings"]:
            value = result["type"]["value"]
            entity_types.append(value)
        return entity_types

    def check(self,entity_string):
        for value in self.get_entity_types(entity_string):
            if ('http://dbpedia.org/ontology/Place' == value or
                'http://dbpedia.org/ontology/Location' == value):
                return True
        

        return False


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

