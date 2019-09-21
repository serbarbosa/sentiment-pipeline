import sys
sys.path.insert(1,'../utils')
import utils

"""
    PARA USAR O TEXTO EM UTF-8

with open('wordnetaffectbr_valencia.csv', 'rb') as word_net:
    data = word_net.read()
    newData = data.decode('iso-8859-1').encode('utf-8')

    print(newData.decode('utf-8'))

"""

#script para processar os lexicos da wordnetaffectbr e da sentilex-pt gerando uma saida padronizada em arquivos com palavras positivas e negativas
with open('positivas.txt', 'w', encoding='utf8') as pos, open('negativas.txt', 'w', encoding='utf8') as neg:
    #para wordnet primeiro
    with open('wordnetaffectbr_valencia.csv', 'rb') as word_net:
        data = word_net.read()
        uData = data.decode('iso-8859-1').encode('utf-8').decode('utf-8').split('\r\n')
        
        for expression in uData:
            try:
                if(expression[-1] == '+'):
                    pos.write(expression.split(';')[0] + '\n')
                else:
                    neg.write(expression.split(';')[0] + '\n')
            except IndexError:
                #string vazia, apenas ignora
                pass
    #para LIWC
    with open('LIWC2007_Portugues_win.dic.txt', 'rb') as liwc:
        
        #le os dados como utf-8 e faz tratamento pois sera usado como ascii
        data = liwc.read()
        uData = data.decode('iso-8859-1').encode('utf-8').decode('utf-8').split('%')
        pos_id = 126
        neg_id = 127
        words_line = uData[-1].split('\r\n')
        
        for word_line in words_line:
            word_split = word_line.split('\t')
            for i in range(1, len(word_split)):
                if int(word_split[i]) == 126:
                    pos.write(utils.remove_invalid_char(word_split[0]) + "\n")

                elif int(word_split[i]) == 127:
                    neg.write(utils.remove_invalid_char(word_split[0]) + "\n")

    
    #para sentilex-pt
    ''' Esse lexico classifica expressoes, mas o filtro ainda nao suporta a comparacao com expressoes
    with open('/home/sergio/sergio/usp/opinando/filtroSubjetividade/SentiLex-PT02/SentiLex-flex-PT02.txt', 'r') as sentilex:
        data = sentilex.read()
        uData = data.encode('utf-8').decode('utf-8')
        
        uData = utils.find_equivalent_char(uData).split('\n')
        for line in uData:
            values = line.split(',')
            for el in values[1].split(';'):
                if(el == 'POL:N0=-1' or el == 'POL:N1=-1'):
                    neg.write(values[0] + '\n')
                elif(el == 'POL:N0=1' or el == 'POL:N1=1'):
                    pos.write(values[0] + '\n')
    '''




