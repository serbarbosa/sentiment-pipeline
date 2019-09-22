import re

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
        sentences = split_into_sentences(data)
        
        for sentence in sentences:
            if(self.is_subjective(sentence)):
                filtered += sentence
            #else:
                #print(" - apagando: '" + sentence + "'")
        
        return filtered

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


#exemplo de uso
#sbj_filter = Subjectivity_filter('.')
#sbj_filter.run_filter('asciiReviews/2.txt')
