# -*- coding: utf-8 -*-
'''
Created on 03/08/2014

@author: Roque Lopez
'''
from __future__ import unicode_literals
from ganesan_summarizer import Ganesan_Summarizer
#from gerani_summarizer import Gerani_Summarizer
from tadano_summarizer import Tadano_Summarizer
from huliu_summarizer import HuLiu_Summarizer
from opizere_summarizer import Opizere_Summarizer
from opizera_summarizer import Opizera_Summarizer
from corpus_reader import Corpus_reader
import os
import sys

def run_opizer(method, data, review_key, annotation_key, id_key):
   
    
    corpus_reader = Corpus_reader(data, annotation_key)
    
    summarizer = None
    summary = None
    if method == 'opizera':
        summarizer = Opizera_Summarizer(data, review_key, id_key, corpus_reader)
        summary = summarizer.create_summary(5)
    
    elif method == 'opizere':
        summarizer = Opizere_Summarizer(data, review_key, id_key, corpus_reader)
        summary = summarizer.create_summary(5, 1)
    
    elif method == 'huliu':
        summarizer = HuLiu_Summarizer(data, review_key, id_key, corpus_reader)
        summary = summarizer.create_summary(5, 1)
    
    elif method == 'tadano':
        summarizer = Tadano_Summarizer(data, review_key, id_key, corpus_reader)
        summary = summarizer.create_summary(5, 2)
    
    elif method == 'gerani':
        summarizer = Gerani_Summarizer(data, review_key, id_key, corpus_reader)
        summary = summarizer.create_summary(5)
    
    elif method == 'ganesan':
        summarizer = Ganesan_Summarizer(data, review_key, id_key, corpus_reader)
        summary = summarizer.create_summary(5)

    print(summary)
'''    
    for item in os.listdir(reviews_path):
        print ("Generating summary for %s" % item)
        item_path = os.path.join(reviews_path, item)
        if summarizer == "huliu":
            hu_liu = HuLiu_Summarizer(item, item_path, corpus_reader)
            hu_liu.create_summary("../resource/automatic_summaries/hu_liu", 5, 1)
        elif summarizer == "tadano":
            tadano = Tadano_Summarizer(item, item_path, corpus_reader)
            tadano.create_summary("../resource/automatic_summaries/tadano/", 5, 2)
        elif summarizer == "opizere":
            opizere = Opizere_Summarizer(item, item_path, corpus_reader)
            opizere.create_summary("../resource/automatic_summaries/opizere/", 5, 1)
        elif summarizer == "ganesan":
            ganesan = Ganesan_Summarizer(item, item_path, corpus_reader)
            ganesan.create_summary("../resource/automatic_summaries/ganesan/", 5)
        elif summarizer == "gerani":
            gerani = Gerani_Summarizer(item, item_path, corpus_reader)
            gerani.create_summary("../resource/automatic_summaries/gerani/", 5)
        elif summarizer == "opizera":
            opizera = Opizera_Summarizer(item, item_path, corpus_reader)
            opizera.create_summary("../resource/automatic_summaries/opizera/", 5)
'''
