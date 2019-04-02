# -*- coding: utf-8 -*-
"""
utilities for paragraph analysis
"""

import os
import json
import sys
import re
import math
import subprocess
import argparse
import codecs
from string import Template

reload(sys)
sys.setdefaultencoding("utf-8")

def read_qrel(qrel_file):
    qrels = {}
    with open(qrel_file) as f:
        for line in f:
            line = line.strip()
            cols = line.split()
            qid = cols[0]
            docid = cols[2]
            rel = int(cols[-1])
            if qid not in qrels:
                qrels[qid] = {}
            qrels[qid][docid] = rel
    return qrels

def get_results(result_dir, cutoff):
    results = {}
    for qid in os.listdir(result_dir):
        old_pid = None
        line_num = 0
        if qid not in results:
            results[qid] = {}
        q_result_file = os.path.join(result_dir,qid)
        with open(q_result_file) as f:
            for line in f:
                cols = line.split()
                pid = cols[0]
                docid = cols[2]
                if pid not in results[qid]:
                    results[qid][pid] = []
                if len(results[qid][pid]) == cutoff:
                    continue
                else:
                    results[qid][pid].append(docid)
    return results


def safe_log(x, y, base = 2):
    try:
        value = math.log((x/y), 2 )
    except (ZeroDivisionError, ValueError) as e:
        value =  .0

    return value




def get_paragraph_words(para_index, docid, num_of_para):
    cmd_template = Template('dumpindex {0} dv `dumpindex {0} di docno {1}-$p_idx`'.format(para_index, docid))
    paragraph_words = {}
    for p_idx in xrange(num_of_para):
        cmd = cmd_template.substitute(p_idx=str(p_idx))
        pid = "Q%s"%(str(p_idx).zfill(2))
        paragraph_words[pid] = []
        p1 = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        start = False
        first = True
        for line in iter(p1.stdout.readline,''):
            if not start:
                if 'Terms' in line:
                    start = True
            else:
                # skip the first line of time stamp
                if first:
                    first = False
                else:
                    cols = line.split()
                    word = cols[2]
                    if word != '[OOV]':
                        paragraph_words[pid].append(word)
        if not paragraph_words[pid]:
            print 'Skip empty paragraph {}'.format(pid)
            paragraph_words.pop(pid, None)
    return paragraph_words



def get_paragraph_word_sets(para_index, docid, num_of_para):
    cmd_template = Template('dumpindex {0} dv `dumpindex {0} di docno {1}-$p_idx`'.format(para_index, docid))
    paragraph_words = {}
    for p_idx in xrange(num_of_para):
        cmd = cmd_template.substitute(p_idx=str(p_idx))
        pid = "Q%s"%(str(p_idx).zfill(2))
        paragraph_words[pid] = set()
        p1 = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        start = False
        first = True
        for line in iter(p1.stdout.readline,''):
            if not start:
                if 'Terms' in line:
                    start = True
            else:
                # skip the first line of time stamp
                if first:
                    first = False
                else:
                    cols = line.split()
                    word = cols[2]
                    if word != '[OOV]':
                        paragraph_words[pid].add(word)
        if not paragraph_words[pid]:
            print 'Skip empty paragraph {}'.format(pid)
            paragraph_words.pop(pid, None)
    return paragraph_words

def get_internal_docid(doc_index, ex_docid):
    cmd = 'dumpindex {} di docno {}'.format(doc_index, ex_docid)
    
    p1 = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in iter(p1.stdout.readline,''):
        return line.strip()
        

def get_num_doc(doc_index):
    cmd = 'dumpindex {} s'.format(doc_index)
    p1 = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in iter(p1.stdout.readline,''):
        m = re.search('documents:(.+)$', line)
        if m:
            return int(m.group(1).strip())

class DocVectorGenerator(object):
    def __init__(self, doc_index):
        self._doc_index = doc_index
        self._cache = {}

    def get_doc_vector(self, ipf_map):
        doc_vector = {}
        for word in ipf_map:
            if word not in self._cache:
                self._cache[word] = self._get_doc_vetor_for_word(word)
            doc_vector[word] = self._cache[word]
        return doc_vector


    def _get_doc_vetor_for_word(self,  word):
        cmd = 'dumpindex {} t {}'.format(self._doc_index, word)
        p1 = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        first = True
        word_doc_vector = []
        for line in iter(p1.stdout.readline,''):
            if first:
                first = False
            else:
                if line:
                    cols = line.split()
                    word_doc_vector.append(cols[0])
                else:
                    break

        return word_doc_vector
