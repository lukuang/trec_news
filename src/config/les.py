# -*- coding: utf-8 -*-

class LES(object) :
  '''
  Configurations related to rank on latent entity space
  '''

  '''
  collection based profile
  '''
  ## enum of proximity kernel functions
  CONSTANT_KERNEL = 0
  GAUSSIAN_KERNEL = 1
  TRIANGLE_KERNEL = 2
  COSINE_KERNEL = 3

  ## currently selected kernel
  SEL_PROX_KERNEL = GAUSSIAN_KERNEL
  #SEL_PROX_KERNEL = CONSTANT_KERNEL

  ## threshold to decide whether the annotation is valid
  VALID_ANNT_THRED = 0.95

  ## the size of context window we are trying to extract
  CONTEXT_WINDOW = 60
  #CONTEXT_WINDOW = 50000 ## for debug purpose only

  ## the window size a context will be trimed to
  TRIM_WINDOW = 40

  ## the length of virtual document for entity profile (i.e., ENT_LM)
  TRIM_LEN = 400

  ## threshold to ignore trival entities with only a few contexts
  ENT_CONTEXT_THRED = 3
  #ENT_CONTEXT_THRED = 20

  ## proximity kernel related constants
  GAUSSIAN_CONST = 2 * TRIM_WINDOW * TRIM_WINDOW

  ## LES rank prefix
  COL_LES_RANK_PREFIX = 'COL-LES-BL-'


  '''
  Freebase based profile
  '''
  ## entity profile LM: Maximum Likelihood estimation
  FB_PROFILE_LM = 'ML'

  ## LES rank prefix
  FB_LES_RANK_PREFIX = 'FB-LES-BL-'

  ## threshold to ignore trival entities with only a few contexts
  FB_ENT_CONTEXT_THRED = 3
  #FB_ENT_CONTEXT_THRED = 20

  '''
  Freebase based profile
  '''
  ## the coefficient for linear interpolation of hybrid profile
  HYBRID_LAMBDA = 0.5


  '''
  entity and document ranking
  '''
  ## \mu for Dirichlet smoothing
  MU_E = 1000.0     ## for entity model
  MU_D = 1000.0     ## for document model

  ## default value for unseen terms
  ## roughly (10 / TOTAL_TERM_COUNT)
  PWC_UNSEEN = 0.00000010

  ## # of dimensions for latent entity space
  NUM_DIM = 10
  ## top K results for one query (top 20 suffice for evaluation)
  TOP_K = 20

  ## maximum of dimensions for latent entity space
  MAX_LES_DIM = 100

  ## per-query corpus directory
  PER_QUERY_CORPUS_DIR = 'corpus/split/'
  ## suffix for trec corpus files
  TREC_FILE_SUFFIX = '.trectext'

  DLM_KEY = 'dlm'

  '''
  Relevance model, for entity ranking
  '''
  RM3_TOP_K = 20
  RM3_ALPHA = 0.5
  RM3_NUM_TERM = 400

