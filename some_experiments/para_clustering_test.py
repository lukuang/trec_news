"""
Some testing on paragraph clustering
"""
from __future__ import division
import os
import json
import sys
import re
import argparse
import codecs
import nltk
import redis
import math
import itertools

sys.path.append("/infolab/node4/lukuang/trec_news/trec_news/src")
from config.db import RedisDB

def vector_to_lm(word_vector, pwc, mu):
    """
    convert word vector to language model
    """
    lm = {}
    ## empty language model for empty vector
    if 0 == len(word_vector) :
        return lm

    ## apply Dirichlet smoothing
    smoothing_sum = 0.0
    for term in word_vector :
        smoothing_sum += word_vector[term]
    
    denom = smoothing_sum + mu

    smoothed_lm = {}

    for term in word_vector:
        cwd = word_vector[term]
        try:
            prob = pwc[term]
        except KeyError:
            prob = pwc["[OOV]"]

        smoothed_lm[term] = (cwd + mu * prob) / denom

    return smoothed_lm, denom


def kl_div(word_vector1, word_vector2, pwc, mu) :
    '''
    Estimate the KL-divergence between two langauge models
    '''
    if (len(word_vector1) == 0 or len(word_vector2) == 0 ):
        return .0
    smoothed_lm1, denom1 = vector_to_lm(word_vector1, pwc, mu)
    smoothed_lm2, denom2 = vector_to_lm(word_vector2, pwc, mu)

    score = .0
    for term in smoothed_lm1 :
        delta = 0.0

        if term not in smoothed_lm2 :
            try:
                prob = pwc[term]
            except KeyError:
                prob = pwc["[OOV]"]

            pt = mu * prob / denom2
            delta = smoothed_lm1[term] * math.log(pt/smoothed_lm1[term])
        else :
            delta = smoothed_lm1[term] * math.log(smoothed_lm2[term]/smoothed_lm1[term])

        score += delta

    return score

def vector_to_lm_no_smoothing(word_vector):
    lm = {}
    count_sum = sum(word_vector.values())
    for w in word_vector:
        lm[w] = word_vector[w]/count_sum
    return lm

def cosine_dis(word_vector1, word_vector2) :
    norm = .0
    for w in word_vector1:
        norm += word_vector1[w]**2
    denom = math.sqrt(norm)
    norm = .0
    for w in word_vector2:
        norm += word_vector2[w]**2
    denom *= math.sqrt(norm)

    numerator = .0
    for w in word_vector1:
        if w in word_vector2:
            numerator += word_vector1[w]*word_vector2[w]

    return 1-(numerator/denom)


def initialize_clustering(paragraph_vectors):
    init_clusters = []
    for v in paragraph_vectors:
        init_clusters.append([v])
    return init_clusters

def cluster_dis(cluster1,cluster2, paragraph_vectors,pwc, mu):
    max_dis = .0
    for para_id1 in cluster1:
        for para_id2 in cluster2:
            # dis = kl_div(para_vector1, para_vector2, pwc, mu)
            dis = cosine_dis(paragraph_vectors[para_id1], paragraph_vectors[para_id2])
            print "new dis between para %d and para %d is:%f" %(para_id1,para_id2,dis)
            if dis > max_dis:
                max_dis = dis
    return max_dis 

def do_clustering(paragraph_vectors,pwc,stopwords, mu,threshold):
    clusters = initialize_clustering(range(len(paragraph_vectors)))
    
    continue_clustering = True
    while continue_clustering:
        merge = False
        for cluster_id1,cluster_id2 in itertools.combinations(range(len(clusters)), 2):
            max_dis = cluster_dis(clusters[cluster_id1], clusters[cluster_id2], paragraph_vectors,pwc, mu)
            if max_dis <= threshold:
                merge = True
                cluster_2 = clusters.pop(cluster_id2)
                clusters[cluster_id1] += cluster_2
                break

        if not merge:
            continue_clustering = False
    return clusters


def sanitize (sstr) :
  ## remove non-ascii characters
  sstr = ''.join(filter(lambda x: ord(x)<128, sstr))

  ## remove the underscore and other non-alphabetical characters
  sstr = re.sub(r'[\_\W]+', ' ', sstr)

  ## squeeze multiple spaces to one
  sstr = re.sub(r'\s+', ' ', sstr)

  ## remove leading spaces
  sstr = re.sub(r'^\s+', '', sstr)

  ## remove trailing spaces
  sstr = re.sub(r'\s+$', '', sstr)

  return sstr.lower()

def get_word_vector(para_string,stopwords):
    stemmer = nltk.stem.porter.PorterStemmer()

    cleaned_string = sanitize(para_string)

    word_vector = {}
    for term in re.findall("\w+", cleaned_string):
        if term in stopwords:
            continue
        stem = stemmer.stem(term)

        if term not in word_vector:
            word_vector[term] = 0
        word_vector[term] += 1

    return word_vector

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mu",type=int,default=1000)
    parser.add_argument("--threshold",type=float,default=0.5)
    parser.add_argument("--docid",default="2203bfb5aeb4cf0adb8997e0c7185c28")
    args=parser.parse_args()


    collection_stats_db = redis.Redis(host=RedisDB.host,
                                      port=RedisDB.port,
                                      db=RedisDB.collection_stats_db)

    stopwords = collection_stats_db.smembers("stopwords")
    pwc = collection_stats_db.hgetall("pwc")

    for term in pwc:
        pwc[term] = float(pwc[term])

    query_db = redis.Redis(host=RedisDB.host,
                                      port=RedisDB.port,
                                      db=RedisDB.query_db)
    doc_string = query_db.get(args.docid)

    paragraphs = json.loads(doc_string)["paragraphs"]

    print "There are %d paragraphs" %(len(paragraphs))
    paragraph_vectors = []
    for p in paragraphs:
        paragraph_vectors.append(get_word_vector(p,stopwords))

    clusters = do_clustering(paragraph_vectors,pwc,stopwords,args.mu,args.threshold)
    for cluster in clusters:
        print "for cluster with para ids: %s" %(" ".join(map(str,cluster)))
        print "para text:"
        for i in cluster:
            print "\t%s" %(paragraphs[i])
        print "-"*20

if __name__=="__main__":
    main()

