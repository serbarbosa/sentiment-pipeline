import os
from typing import List, Dict
import json

def run_fuzzy(data : List[Dict]) -> List[Dict]:
    '''Recebe um arquivo json carregado e faz chamada do metodo fuzzy devolvendo
    o json filtrado.'''
    
    #deixando compativel com entrada do topXfuzzy
    compatible_data = ''
    for review in data:
        compatible_data += review['revisao'].replace('\n', '').replace('\t', '').replace('\r', '') + "\t1\n"
    
    #escrevendo arquivo de entrada para o fuzzy e rodando metodo
    with open('in.txt', 'w') as f:
        f.write(compatible_data)
        del compatible_data #nao sera mais usado..

    command = 'java -jar "ProjetoFinal.jar" "in.txt"'
    os.system(command)

    #lendo saida e gerando json com as revisoes aceitas
    fuzzy_output = None
    with open('in.txt.res', 'r') as f:
        fuzzy_output = f.read().split('\n')[1:-1]
    
    for i in range(len(fuzzy_output)):
        if fuzzy_output[i].split(',')[-1] == 'IF':
            data[i]['revisao'] = ''
    
    return data


