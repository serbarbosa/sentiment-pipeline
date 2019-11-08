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
        ''' Percorre a frase procurando por aspectos multi-palavra.''' 
        aspects = []
        for k, v in self.explicit_aspects2.items():
            index = text.find(k)
            if index >= 0:
                pos = len(text[:index].split(' '))-1
                aspects.append([k, pos, pos + len(k.split(' '))-1, ''])
        for k, v in self.implicit_aspects2.items():
            index = text.find(k)
            if index >= 0:
                pos = len(text[:index].split(' '))-1
                aspects.append([v,pos, pos + len(k.split(' '))-1, 'implicit'])
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
                aspects.append([word, i, i, ''])
            elif word in self.implicit_aspects1:
                aspects.append([self.implicit_aspects1[word], i, i,'implicit'])
            if trie.search(self.sent_words, word)[0]:
                rev_sent_words.append([word, i, i])
        return [aspects, rev_sent_words]
        
                                                #list[str, int]     #list[list[str, int]] #list[str, int]
    def _get_nearest_sentword(self, aspectNpos : list, rev_sent_words : list) -> list:
        
        min_dist = [rev_sent_words[0], 1000]
        
        for sent_word in rev_sent_words:
            #calcula distancia entre aspecto e palavra de sentimento
            dist = abs(aspectNpos[1] - sent_word[1])
            
            #mantem a palavra de sentimento que estiver mais proxima(que nao seja o aspecto)
            if(dist > 0  and dist < min_dist[1]): 
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
        #se quer incluir uma palavra anterior ao inicio para verificacao de modificadores 
        #nao pode ser pontuacao
        while start > 0 and len(split_sentence[start]) < 2:
            start -=1

        if(end < len(split_sentence)-1):
                end += 1
        
        sub_sentence = ''
        for i in range(start, end+1):
            sub_sentence += split_sentence[i] + ' '
        return sub_sentence
    

    def _get_sentiment_orientation(self, sent_word : str, sub_sentence : str) -> str:
        ''' Recupera a orientação de uma palavra de sentimento e verifica se houve inversão.'''
        
        modifiers = ['nao', 'nao e', 'jamais', 'nada', 'nem', 'nenhum', 'ninguem', 'nunca', 'tampouco', 'sem']

        #recupera da hash o sentimento correspondente
        orientation = trie.search(self.sent_words, sent_word)[1]
        #verifica se existe um modificador no trecho entre o aspecto e a palavra de sentimento
        for modifier in modifiers:
            if modifier in sub_sentence:
                #inverte orientacao
                orientation = '+' if orientation == '-' else '-'
                #finaliza checagem
                break
        return orientation
    
    def annotate_aspects(self, data : List[Dict], index : int, review_aspects : Dict, review_sentiments : Dict,
                                                                                opinion_matrix : List[List[str]]):
        '''
            Metodo que ira utilizar os aspectos e os sentimentos identificados e classificados para
            anotar a revisao no padrao de leitura para o sumarizador opizer.
        '''

        aspect_map = {}
        i = 0
        for k in review_aspects.keys():
            aspect_map[k] = 'A'+str(i)
            #cada aspecto podera ocorrer varias vezes. Todas as ocorrencias sao anotadas
            for annot in review_aspects[k]:
                #anotando aspecto 
                start_word = opinion_matrix[annot[0]][annot[1]]
                start_word = '['+start_word
                opinion_matrix[annot[0]][annot[1]] = start_word
                end_word = opinion_matrix[annot[0]][annot[2]]
                end_word = end_word + ']_[A'+str(i)+']'
                opinion_matrix[annot[0]][annot[2]] = end_word
            i+=1
        
        for sentiment in review_sentiments.values():
            #pra cada ocorrencia do sentimento, faz anotacao
            for occur in sentiment:
                #se passar a aceitar sentimento multipalavra, alterar aqui
                word = opinion_matrix[occur[2][0]][occur[2][1]]
                if '[' not in word:     #trata caso de 1 palavra de sentimento atrelada a varios aspectos
                    word = '[' + word + ']_[' + aspect_map[occur[0]] + ',' + occur[1] + ']'
                else:
                    word = word[:-1] + ';' + aspect_map[occur[0]] + ',' + occur[1] + ']'
                opinion_matrix[occur[2][0]][occur[2][1]] = word
                
        #montando anotacao para padrao de leitura do opizer
        annotation = '#Resenha_' + str(data[index]['id'])+'\n#Aspectos: '
        
        #anotando aspetos
        first_aspect = None        
        if aspect_map:
            first_aspect = list(aspect_map.keys())[0]
            annotation += aspect_map[first_aspect] + '_' + first_aspect
        for k, v in aspect_map.items():
            if k != first_aspect:
                annotation += ', '+v+'_'+k
        
        #anotando estrelas
        annotation +='\n#Estrelas: '+str(data[index]['estrelas'])+'\n'
        
        #anotando revisao
        for line in opinion_matrix:
            review_line = ''
            #remontando linha a partir da lista de palavras
            for word in line:
                if word != line[-1]:
                    review_line += word + ' '
                else:
                    review_line += word + '\n'
            annotation += review_line
        
        #escrevendo nova entrada no json com a anotacao
        data[index]['revisao_anot'] = annotation
        

    def _sent_analisys(self, data : List[Dict], index : int, review : str):
        
        #separa revisao em frases. vai processar uma por vez.
        sentences = utils.split_into_sentences(review)
        opinions = []
        
        opinion_matrix= []
        review_aspects = {}     #aspectos como chaves mapeando uma lista com as posicoes onde ocorrem
        review_sentiments = {}  #sentimentos como chaves mapeando uma lista aspecto, orientacao, posicao

        for i in range(len(sentences)):
            split_sentence = sentences[i].split(' ')
            opinion_matrix.append(split_sentence)
            keywords = self._extract_keywords(split_sentence) #[aspects, sent_words]
            extra_aspects = self._extract_keywords_slowstage(sentences[i])
            keywords[0] += extra_aspects    #keywords[0] possui todos os aspectos e a posicao de cada um na frase
            
            #mapeando aspectos para anotacao automatica
            for aspect in keywords[0]:
                if aspect[0] not in review_aspects:
                    review_aspects[aspect[0]] = [[i, aspect[1], aspect[2], aspect[3]]]
                else:
                    review_aspects[aspect[0]].append([i, aspect[1], aspect[2], aspect[3]])

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
                    
                    #mapeando sentimentos para anotacao automatica
                    if sent_word[0] not in review_sentiments:
                        review_sentiments[sent_word[0]] = [[aspect[0], orientation, [i, sent_word[1], sent_word[2]]]]
                    else:
                        review_sentiments[sent_word[0]].append([aspect[0], orientation, [i, sent_word[1], sent_word[2]]])

                    opinions.append({'aspecto' : aspect[0], 'polaridade' : orientation, 'palavra_sent' : sent_word[0]})

        self.annotate_aspects(data, index, review_aspects, review_sentiments, opinion_matrix)
        return opinions

    def run(self, data : List[Dict], data_key : str) -> List[Dict]:
        
        identified_aspects = []
        
        for i in range(len(data)):
            
            ascii_data = utils.find_equivalent_char(data[i][data_key])
            identified_aspects += self._sent_analisys(data, i, ascii_data)

        return identified_aspects        

