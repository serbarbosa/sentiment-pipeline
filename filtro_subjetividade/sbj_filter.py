import re
from uteis import utils

class Subjectivity_filter():

    def __init__(self, path):
        
        pos_lex = path+'/positivas.txt'
        neg_lex = path+'/negativas.txt'
        self.pos_dict = {}
        self.neg_dict = {}
        self.create_dictionary(self.pos_dict, pos_lex)
        self.create_dictionary(self.neg_dict, neg_lex)
        
    def create_dictionary(self, dic, file_name):
        
        with open(file_name, 'r') as lex:
            data = lex.read().split('\n')[:-1]
            for i in range(len(data)):
                if(len(data[i]) > 0):
                    dic[data[i]] = i
    
    def is_subjective(self, sentence):
        words = sentence.split(' ')
        positive = 0
        negative = 0
        
        for word in words:
            if len(word) > 0:
                if word in self.pos_dict:
                    positive += 1
                if word in self.neg_dict:
                    negative += 1
        
        return positive - negative != 0

    def run_filter(self, data : str) -> str:
        
        filtered = ''
        sentences = utils.split_into_sentences(data)
        
        for sentence in sentences:
            if(self.is_subjective(sentence)):
                filtered += sentence
#            else:
#                print(" - apagando: '" + sentence + "'")
        
        return filtered

#exemplo de uso
#sbj_filter = Subjectivity_filter('.')
#sbj_filter.run_filter('asciiReviews/2.txt')
