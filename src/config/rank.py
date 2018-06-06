# -*- coding: utf-8 -*-

class Rank(object) :
  '''
  Configurations of document ranking lists from different models
  '''

  # the pattern for the hash name in DB for each retrieval model
  INDRI_PAT = 'indri-%s'      ## Indri top 3000 baseline
  DIR_PAT = 'dir-%s'          ## LM baseline
  LES_COL_PAT = 'les-col-%s'  ## LES (collection profile)
  LES_FB_PAT = 'les-fb-%s'    ## LES (Freebase profile)
  LES_QENT_COL_PAT = 'les-qent-col-%s'    ## LES (colletion profile)
  LES_QENT_FB_PAT = 'les-qent-fb-%s'      ## LES (Freebase profile)

