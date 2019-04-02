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
  doc_db = 4
  test_query_db = 5
  doc_entity_db = 6
  stemed_collection_stats_db = 14

  ## annotated DB
  annotated_collection_stats_db = 7
  annotated_doc_db = 8

  ## entity DB
  entity_types_db = 9

  ## word info DB
  para_word_info_db = 10
  annotated_para_word_info_db = 11
  doc_word_info_db = 12
  annotated_doc_word_info_db = 13


  """

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

