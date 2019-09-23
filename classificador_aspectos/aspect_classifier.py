import pickle
import sys
import re
from typing import List, Dict

#TODO Armazenar lexicos usando trie permitindo assim encontrar aspectos e sentimentos quando o
#radical das palavras for igual (sem perder muita performance)

class Aspect_classifier():

    def __init__(self, dir_path = '.'):
                
        self.explicit_aspects = self._load_lexicon(dir_path + '/Aspects_lexicon/explicit_aspects.p')
        self.implicit_aspects = self._load_lexicon(dir_path + '/Aspects_lexicon/implicit_aspects.p') 
        self.sent_words = self._load_lexicon(dir_path + '/Sentiment_words/sent_words_polarity.p')

    def _load_lexicon(self, filepath : str) -> dict:
        '''Faz leitura de um dicionario salvo com pickle e retorna a estrutura.'''
        structure = None
        with open(filepath, 'rb') as lex:
            structure = pickle.load(lex)
        
        return structure
            
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
            if word in self.explicit_aspects:
                aspects.append([word, i])
            elif word in self.implicit_aspects:
                aspects.append([self.implicit_aspects[word], i])
            elif word in self.sent_words:
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
        orientantion = self.sent_words[sent_word]
        
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
        sentences = split_into_sentences(review)
        opinions = []
        
        for sentence in sentences:
            split_sentence = sentence.split(' ')
            keywords = self._extract_keywords(split_sentence) #[aspects, sent_words]
            #print(keywords) 
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
                    #print(opinions[-1])        
        return opinions

    def run(self, data : List[Dict], data_key : str) -> List[Dict]:
        
        identified_aspects = []
        
        for i in range(len(data)):
            
            ascii_data = find_equivalent_char(data[i][data_key])
            identified_aspects += self._sent_analisys(ascii_data)
        
        return identified_aspects        


# -------   Funções uteis ----------

def find_equivalent_char(utf8Text : str) -> str:

    '''Mapeia caracteres do texto em utf-8 para caracteres validos em ascii.'''
    
    ascii_map = {
            'á' : 'a',
            'à' : 'a',
            'é' : 'e',
            'è' : 'e',
            'í' : 'i',
            'ì' : 'i',
            'ó' : 'o',
            'ò' : 'o',
            'ú' : 'u',
            'ù' : 'u',
            'ê' : 'e',
            'ô' : 'o',
            'ã' : 'a',
            'õ' : 'o',
            'ẽ' : 'e',
            'ũ' : 'u',
            'ç' : 'c',
            'ü' : 'u',
            'Á' : 'a',
            'À' : 'a',
            'Í' : 'i',
            'É' : 'e',
            'Ó' : 'o',
            'Ú' : 'u'
    }
    
    ascii_text = ''
    for i in range(len(utf8Text)):
        #busca na hash e copia o equivalente
        if(utf8Text[i] in ascii_map):
            ascii_text+= ascii_map[utf8Text[i]]
        else:
            #apenas copia a letra
            ascii_text += utf8Text[i]

    return ascii_text

def split_into_sentences(text):
    alphabets= "([A-Za-z])"
    prefixes = "(Sr|Sra|Srs|Sras|Srta)[.]"
    suffixes = "(Corp|Ltda|Sr)"
    starters = "(Sr|Srs|Sra|Dr)"
    acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
    websites = "[.](com|net|org|io|gov|br)"
    digits = "([0-9])"
    
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    text = re.sub(digits + "[.]" + digits,"\\1<prd>\\2",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences
