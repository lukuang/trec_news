# -*- coding: utf-8 -*-

class RedisDB(object) :
  '''
  Configuration of Redis DB
  '''
  host = 'headnode'
  port = 3013

  # specifications of DBs

  ## general DB
  bl_query_db = 1
  er_query_db = 2
  collection_stats_db = 3
  result_doc_db = 4
  """
  doc_rank_db = 4
  cs_db = 5

  ## collection profile
  col_profile_db = 10
  col_ent_lm_db = 11
  col_ent_rank_db = 12
  col_doc_rank_db = 13

  # by utilizing query entites
  qent_col_ent_rank_db = 16
  qent_col_doc_rank_db = 17
  only_qent_col_doc_rank_db = 18

  ## Freebase profile
  fb_profile_db = 20
  fb_ent_lm_db = 21
  fb_ent_rank_db = 22
  fb_doc_rank_db = 23

  # by utilizing query entities
  qent_fb_ent_rank_db = 26
  qent_fb_doc_rank_db = 27
  only_qent_fb_doc_rank_db = 28
  """

  # specifications of hash tables
  query_title_hash = 'query_title_hash'
  query_desc_hash = 'query_desc_hash'

  # specifications of lists

