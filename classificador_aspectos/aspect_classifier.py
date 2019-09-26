import pickle
import sys
import re
from typing import List, Dict
import os
import trie
from uteis import utils

#TODO Armazenar lexicos usando trie permitindo assim encontrar aspectos e sentimentos quando o
#radical das palavras for igual (sem perder muita performance)

class Aspect_classifier():

    def __init__(self, dir_path = '.'):
                
        self.explicit_aspects1 = self._load_lexicon(dir_path + '/Aspects_lexicon/explicit_aspects1.p')
        self.explicit_aspects2 = self._load_lexicon(dir_path + '/Aspects_lexicon/explicit_aspects2.p')
        self.implicit_aspects1 = self._load_lexicon(dir_path + '/Aspects_lexicon/implicit_aspects1.p') 
        self.implicit_aspects2 = self._load_lexicon(dir_path + '/Aspects_lexicon/implicit_aspects2.p') 
        sent_words_data = self._load_lexicon(dir_path + '/Sentiment_words/sent_words_polarity.p')
        self.sent_words = self.create_trie(sent_words_data)

    def _load_lexicon(self, filepath : str) -> dict:
        '''Faz leitura de um dicionario salvo com pickle e retorna a estrutura.'''
        structure = None
        with open(filepath, 'rb') as lex:
            structure = pickle.load(lex)
        
        return structure

    def create_trie(self, data : Dict):
        trie_node = trie.TrieNode()

        for key, value in data.items():
            trie.insert(trie_node, [key, value])
        
        return trie_node
    
    def _extract_keywords_slowstage(self, text : str):
        
        aspects = []
        for k, v in self.explicit_aspects2.items():
            index = text.find(k)
            if index >= 0:
                pos = len(text[:index].split(' '))
                aspects.append([k, pos])
        for k, v in self.implicit_aspects2.items():
            index = text.find(k)
            if index >= 0:
                pos = len(text[:index].split(' '))
                aspects.append([k,pos])
        return aspects

    def _extract_keywords(self, split_sentence : list):
        '''
            Percorre a frase extraindo os aspectos e as palavras de sentimento.
            
            return : Uma lista contendo a lista de aspectos na primeira posição 
                     e uma lista de palavras de sentimento na segunda.
                     Cada item da lista de aspecto/sentimento contem um par com
                     a palavra e sua posicao na frase.
        '''
        
        aspects = []
        rev_sent_words = []
        for i in range(len(split_sentence)):
            word = split_sentence[i]
            if word in self.explicit_aspects1:
                aspects.append([word, i])
            elif word in self.implicit_aspects1:
                aspects.append([self.implicit_aspects1[word], i])
            if trie.search(self.sent_words, word)[0]:
                rev_sent_words.append([word, i])
        
        return [aspects, rev_sent_words]
        
                                                #list[str, int]     #list[list[str, int]] #list[str, int]
    def _get_nearest_sentword(self, aspectNpos : list, rev_sent_words : list) -> list:
        
        min_dist = [rev_sent_words[0], abs(aspectNpos[1] - rev_sent_words[0][1])]
        
        for sent_word in rev_sent_words:
            #calcula distancia entre aspecto e palavra de sentimento
            dist = abs(aspectNpos[1] - sent_word[1])
            
            #mantem a palavra de sentimento que estiver mais proxima
            if(dist < min_dist[1]): 
                min_dist[0] = sent_word
                min_dist[1] = dist
            
        return min_dist[0]
                                                 #list[str]     #list[str, int]   #list[str, int]
    def _get_sub_sentence(self, split_sentence : List[str], aspect : List, sent_word : List) -> str: 
        '''Retorna um trecho da frase dado contido entre um aspecto e uma palavra de sentimento.'''
        
        #definindo um intervalo valido
        start, end = aspect[1], sent_word[1]
        if(start > end):
            start, end = end, start

        if(start > 0) : start -= 1
        if(end < len(split_sentence)-1):
                end += 1
        
        sub_sentence = ''
        for i in range(start, end+1):
            sub_sentence += split_sentence[i] + ' '
        return sub_sentence
    

    def _get_sentiment_orientation(self, sent_word : str, sub_sentence : str) -> str:
        ''' Recupera a orientação de uma palavra de sentimento e verifica se houve inversão.'''
        
        modifiers = ['nao', 'nao e', 'jamais', 'nada', 'nem', 'nenhum', 'ninguem', 'nunca', 'tampouco']

        #recupera da hash o sentimento correspondente
        orientantion = trie.search(self.sent_words, sent_word)[1]
        #verifica se existe um modificador no trecho entre o aspecto e a palavra de sentimento
        for modifier in modifiers:
            if modifier in sub_sentence:
                #inverte orientacao
                orientantion = '+' if orientantion == '-' else '-'
                #finaliza checagem
                break
        return orientantion
        

    def _sent_analisys(self, review : str):
        
        #separa revisao em frases. vai processar uma por vez.
        sentences = utils.split_into_sentences(review)
        opinions = []
        
        for sentence in sentences:
            split_sentence = sentence.split(' ')
            keywords = self._extract_keywords(split_sentence) #[aspects, sent_words]
            extra_aspects = self._extract_keywords_slowstage(sentence)
            keywords[0] += extra_aspects
#            print(keywords) 
            #caso onde nao foram encontradas palavras de sentimento
            if(len(keywords[1]) == 0):
                for aspect in keywords[0]:
                    opinions.append({'aspecto' : aspect[0], 'polaridade' : '', 'palavra_sent' : 'x'})
            
            #caso onde encontrou-se sentimento
            else:
                for aspect in keywords[0]:
                    sent_word = self._get_nearest_sentword(aspect, keywords[1])
                    #recuperando trecho entre aspecto e palavra de sentimento 
                    sub_sentence = self._get_sub_sentence(split_sentence, aspect, sent_word)
                    orientation = self._get_sentiment_orientation(sent_word[0], sub_sentence)
                    opinions.append({'aspecto' : aspect[0], 'polaridade' : orientation, 'palavra_sent' : sent_word[0]})
#                    print(opinions[-1])        
        return opinions

    def run(self, data : List[Dict], data_key : str) -> List[Dict]:
        
        identified_aspects = []
        
        for i in range(len(data)):
            
            ascii_data = utils.find_equivalent_char(data[i][data_key])
            identified_aspects += self._sent_analisys(ascii_data)
        
        return identified_aspects        

