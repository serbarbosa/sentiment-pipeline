# -*- coding: utf-8 -*-
'''
Created on 19/02/2015

@author: Roque Lopez
'''
from __future__ import unicode_literals
from uteis import utils_opizer
import random
import os
import codecs
import re

class HuLiu_Summarizer(object):
    '''
    Class that implements HuLiu method
    '''

    def __init__(self, review_data, review_key, id_key, aspect_manager):
        self.__aspect_manager = aspect_manager
        self.__data = {}
        self.__sentences = {}
        self.__read_files(review_data, review_key, id_key)

    def __read_files(self, review_data, review_key, id_key):
        ''' Read the files (opinions) '''
        for review in review_data:
            sentences = utils_opizer.get_sentences(review[review_key])
            for (id_sentence, text_sentence) in sentences:
                annotations = self.__aspect_manager.get_data_sentence(str(review[id_key]), str(id_sentence))['annotations']
                self.__process_annotations(str(review[id_key])+'_'+id_sentence, annotations, text_sentence)

    def __process_annotations(self, id_sentence, annotations, sentence):
        ''' Process the annotations of a sentence getting the aspects and their polarities and frequencies '''
        if id_sentence not in self.__sentences: 
                self.__sentences[id_sentence] =  sentence

        for annotation in annotations:
            aspect = annotation['aspect']
            polarity = annotation['polarity']           

            if aspect not in self.__data: 
                self.__data[aspect] = {'+':{}, '-':{}, 'frequency':0}

            if id_sentence not in self.__data[aspect][polarity]: 
                self.__data[aspect][polarity][id_sentence] = 0

            self.__data[aspect][polarity][id_sentence]  += 1
            self.__data[aspect]['frequency'] += 1

    def create_summary(self, number_aspects, number_sentences):
        ''' Create a summary given a number of aspects  and sentences  for the summary '''
        top_aspects = sorted(self.__data.items(), key=lambda x:x[1]['frequency'], reverse=True)

        if number_aspects > len(top_aspects): number_aspects =  len(top_aspects)
        text = ""

        for (aspect, data) in top_aspects[:number_aspects]:
            text += "Aspecto: %s \n" % aspect
            pos_size = len(self.__data[aspect]['+'])            
            text += "   Sentenças Positivas: %s\n" % pos_size
            items = min(number_sentences, pos_size)
            positive_sentences = self.__get_sentence_ramdonly(aspect, '+')
 
            for i in range(items):
                text += "  - %s\n" % self.__sentences[positive_sentences[i][0]]

            neg_size = len(self.__data[aspect]['-'])
            text += "   Sentenças Negativas: %s\n" % neg_size
            items = min(number_sentences, neg_size)
            negative_sentences = self.__get_sentence_ramdonly(aspect, '-')

            for i in range(items):
                text += "  - %s\n" % self.__sentences[negative_sentences[i][0]]

        return text

    def __get_sentence_ramdonly(self, aspect, polarity):
        ''' Return a sentence list sorted randomly '''
        tuple_list = self.__data[aspect][polarity].items()
        return sorted(tuple_list, key=lambda x:random.random())

    def print_summary(self, top, number_comments):
        ''' Print the summary '''
        top_aspects = sorted(self.__data.items(), key=lambda x:x[1]['frequency'], reverse=True)
        if top > len(top_aspects): top =  len(top_aspects)

        for (aspect, data) in top_aspects[:top]:
            print ("Aspecto: ", aspect)
            pos_size = len(self.__data[aspect]['+'])
            neg_size = len(self.__data[aspect]['-'])
            print ("  Sentenças Positivas:", pos_size)
            items = min(number_comments, pos_size)
            for i in range(items):
                print ("  - ", self.__data[aspect]['+'][i])

            print ("  Sentenças Negativas:", neg_size)
            items = min(number_comments, neg_size)
            for i in range(items):
                print ("  - ", self.__data[aspect]['-'][i])
