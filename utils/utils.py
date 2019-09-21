import re

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

def remove_invalid_char(word):
    
    valid_word = ''
    for char in word:
        if char != '*':
            valid_word += char
    return valid_word

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
    
   
