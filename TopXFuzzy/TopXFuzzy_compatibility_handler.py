import os
from typing import List, Dict
import json

def run_fuzzy(json_file : str) -> List[Dict]:
    
    data = None
    #recuperando dados do arquivo json
    with open(json_file, 'r', encoding='utf-8') as f:
        
        data = json.load(f)
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
    output_json = []
    for i in range(len(fuzzy_output)):
        if fuzzy_output[i].split(',')[-1] != 'IF':
            output_json.append(data[i])    
    
    print(output_json)
    return output_json


