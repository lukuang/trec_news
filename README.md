# trec_news
for trec news track

## Table of Contents
- [Official Documents](#official-documents)  
- [Collection](#collection)  
- [Data Locations](data-locations)
- [Dbpedia Spotlight](dbpedia-spotlight)
- [Code](#code)
  - [Utility Modules](utility-modules)


## Official Documents
1. [Official Website](http://trec-news.org/)
2. [Guideline](https://docs.google.com/document/d/e/2PACX-1vSJvm30NV4aT4fRcf6x-J-AjvZqaWEw8DsjgXP1v3NlcWZZEtxZ9SwmuB-sQvcc_G7ER-BcUKJQoZHn/pub)
2. [Google Group](https://groups.google.com/forum/#!forum/trec-news-track) 

## Collection

[Washington Post](https://trec.nist.gov/data/wapost/). 

## Data Locations

All the data is located at ```/infolab/node4/lukuang/trec_news/data/washington_post/```:  
![Imgur](https://i.imgur.com/VbRA6vI.png)
1. orginial collection: ```WashingtonPost``` and the original downloaded file ```wapo.tar.gz```
2. trec format text, each trec document is an article: ```trec_text```
3. trec format text, each trec document is a paragraph of an articl: ```trec_text_paragraph```
4. Indri index for articles: ```index``` and the Indri parameter file for it: ```index.para```
5. Indri index for paragraphs: ```paragraph_index``` and the Indri parameter file for it: ```paragraph_index.para```
6. Directory for queries: ```queries``` (there are only a query file I manully created of background linking according to the 
examples and fromat described in the guideline)
7. Entity annotations for each paragraph: ```paragraph_entities``` (The generation process is on going)
8. Some testing of Indri index: ```date_test```. You can ignore it.

## Dbpedia Spotlight
The source code can be found [here](https://github.com/dbpedia-spotlight/dbpedia-spotlight). I used it for entity annotation. I downloaded the ".jar" file. The code resides at ```/infolab/node4/lukuang/code/dbpedia-spotlight```. It acts as a local server and receives rest api requests. You do not need to run it as I ran it. You just need to call the rest api. How to do it can be found in the code ```src/entity/dbpedia/dbpedia.py```

## Code
All code are located at ```/infolab/node4/lukuang/trec_news/trec_news/```

### Utility Modules
I created some modules that can be used. These modules reside at 


