import taggerManager
import tokensManager
import correctnessManager
import patternsManager
import annManager
import json
import utils

from typing import List, Dict

def run_mlp_filter(json_data : List[Dict], grade='good', metric=1 ) -> List[Dict]:
    
    grades = {'sufficient' : 1, 'good' : 2, 'excellent' : 3}

    #passou grade insufficient ou invalida, nao faz sentido filtrar nesse caso..
    if grade not in grades: return json_data 
    
    value = grades[grade]
    

    amnt = len(json_data)
    count = 0
    #repete pra cada revisao
    for entry in json_data:
        
        if(count % 100 == 0):
            print('filtrando: ' + str(count*100//amnt)+'%')
        count += 1

        text = utils.split_into_sentences(entry['revisao'])

        input_text = []
        output_text = []
        
        #reputacao do autor = 1
        text_features = [1]     
        
        #para cada frase da revisao
        for sentence in text:
            
            #na separacao acaba considerando pontuacoes como frases inteiras
            if len(sentence) < 5: continue

            #encontrando padroes
            tokens = tokensManager.GetTokens(sentence, 0)
            tagsTokens = taggerManager.TaggerComment(sentence)
            tags = taggerManager.TagsDict(tagsTokens)
            patt1, patt3, patt4, patt5 = patternsManager.GetPatternsDict(tags)
            
            number_tuples = len(patt1[1])+len(patt3[1])+len(patt3[1])+len(patt3[1])
            text_features.append(number_tuples)
                
            #corretude
            correctness = correctnessManager.Correctness(sentence)
            text_features.append(correctness)
            
            input_text.append(text_features)
            
            #classificacao 'good'
            output_text.append(value)   
        
        if(len(input_text) > 1):
            out = annManager.AnnTraining(input_text+input_text, output_text+output_text, 1)
            #se a nota da revisao for menor do que a solicitada, revisao e' apagada
            if(out[str(value)]['support'] < value):
                print('------ removendo ------')
                print(entry['revisao'])
                print()
                entry['revisao'] = ''
     
    return json_data 


