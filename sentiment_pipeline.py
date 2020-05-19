import os, os.path
import sys
import shutil
import time

#resolvendo imports para subdiretorios
main_dir = os.path.join(__file__[:-len("sentiment_pipeline.py")])

sys.path.insert(0,main_dir + '/classificador_aspectos')
sys.path.insert(0,main_dir + '/TopXMLP')
sys.path.insert(0,main_dir + '/uteis')
sys.path.insert(0,main_dir + '/opizer')
sys.path.insert(0,main_dir + '/processed_data')
#sys.path.insert(0,main_dir + '/filtro_subjetividade')

from review_crawler.crawl_reviews import run_crawler
from filtro_subjetividade.sbj_filter import Subjectivity_filter
from classificador_aspectos import aspect_classifier
from classificador_aspectos.aspect_plotter import Aspect_plotter
#from TopXFuzzy.TopXFuzzy_compatibility_handler import run_fuzzy
from TopXMLP.mlp_filter import run_mlp_filter
from opizer.main import run_opizer

import json
from typing import List, Dict

#tentando importar enelvo
try:
    from enelvo import normaliser
except ModuleNotFoundError:
    print('enelvo is not installed')
    print("run the command 'pip install --user -r enelvoApi/requirements.txt' to install dependencies")
    print("then run the command 'python3 enelvoApi/setupe.py install' to install enelvo")
    print("you may need administrators permission")
    exit()

class Sentiment_pipeline():

    def __init__(self, search = '', normalize = True,classify_aspects = False,
                filter_quality_fuzzy=False, filter_quality_mlp=True, filter_subjectivity=True, crawl_reviews=True, main_key='revisao',
                summarize='opizere'):
       
        #atribuindo controle para quais operacoes serao realizadas
        self.crawl_reviews = crawl_reviews
        self.normalize = normalize
        self.summarize = summarize
        self.classify_aspects = classify_aspects
        self.filter_quality_fuzzy = filter_quality_fuzzy
        self.filter_subjectivity = filter_subjectivity
        self.filter_quality_mlp = filter_quality_mlp

        self.search = search
        self.data = None
        self.data_size = 0
        self.main_key = main_key
        self.annot_key = self.main_key + '_anot'
        self.script_dir = main_dir
        self.user_name = self.create_data_dir()
        self.data_folder = os.path.join('processed_data', self.user_name)
        self.data_filename = 'data.json'

            


    def create_data_dir(self):
        '''Cria um diretorio unico para cada execucao ---exclusivo da versao web'''

        #acessando diretorio do script
        called_dir = os.getcwd()
        os.chdir(os.path.join(self.script_dir, "processed_data"))

        #recuperando nome dos diretorios sendo usados atualmente
        dirs = os.listdir('.')
        #calculando numero do usuario dessa execucao, baseado no arquivo de maior numero
        user_name = 'user_0'
        if len(dirs) > 0:
            user_name = 'user_' + str(int(max(dirs)[len('user_'):]) + 1)
        
        #criando diretorio de dados pro usuario
        os.makedirs(user_name)
        
        #se for resgatar revisoes da web
        if self.crawl_reviews:
            #entao copia crawler exclusivo para o usuario
            src = os.path.join(called_dir, self.script_dir, 'review_crawler')
            dest = os.path.join(user_name, "review_crawler")
            destination = shutil.copytree(src, dest)
        
        #retornando ao diretorio da interface
        os.chdir(called_dir)
        
        return user_name
        
    
    def set_script_dir(self, path):
        self.script_dir = path

    def clean_up(self):
        '''Reinicia o diretorio padrao, deletando todos os arquivos presentes nele.'''
        '''Versao web funciona um pouco diferente. Deve-se remover sempre os dados processados na ultima execucao e deixa-los removidos'''
        
        shutil.rmtree(self.data_folder)
        #os.makedirs(self.data_folder)  ---versao desktop apenas
        

    def set_data_folder(self, folder : str):
        '''Define a pasta destino para os dados.'''
        self.data_folder = folder

    def set_data_filename(self, filename : str):
        '''Define o nome de arquivo que será escrito.'''
        self.data_filename = filename
    
    def set_data(self, data, separator="\n"):
        '''Recebe revisoes como entrada e as trata utilizando o separador informado'''
        self.data = []
        id = 0
        for review in data.split(separator):
            self.data.append({'revisao' : review, 'id' : id, 'estrelas' : '-'})
            id += 1

        self.data_size = len(self.data)

    def load_data(self) -> bool:
        '''Carrega os dados salvos da fonte padrão.

            Return : True ou False indicando se conseguiu ler os dados
        '''

        filename = self.data_folder + self.data_filename
        if(os.path.getsize(filename) == 0): return False
        
        with open(self.data_folder + self.data_filename, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.data_size = len(self.data)
        
        return True

    def load_data_from_file(self, filepath : str) -> bool:
        '''Carrega dados a partir do caminho informado.

            Return : True ou False indicando se conseguiu ler os dados
        '''
        if(os.path.getsize(filepath) == 0): return False
       
        with open(filepath, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.data_size = len(self.data)
        
        return True

    def write_data(self, free_data=False):
        '''Escreve dados para o destino padrão.'''
        with open(os.path.join(self.data_folder, self.data_filename), 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)
        if(free_data):
            self.data = None
    
    def write_results(self, data : List[Dict], filepath : str):
        '''Salva o dado informado no diretorio informado como arquivo .json.'''
        #TODO tratar tipo de dado incorreto
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    def load_results(self, filepath : str) -> List[Dict]:
        'Carrega e retorna os dados do arquivo .json informado.'''
        #TODO tratar falha na leitura
        data = None
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    
    def normalize_data(self):
        '''Normaliza os dados com enelvo.'''

        #print("Inicializando normalizador ...")
        norm = normaliser.Normaliser()
        for i in range(self.data_size):
            self.data[i][self.main_key] = norm.normalise(self.data[i][self.main_key])
        
    def normalize_and_filter(self):
        '''Normaliza os dados com enelvo e em seguida realiza a filtragem por subjetividade.'''

        #print("Inicializando normalizador ...")
        norm = normaliser.Normaliser()
        
        #print("Inicializando filtro de subjetividade ...")
        sbj_filter = Subjectivity_filter('filtro_subjetividade')
        
        for i in range(self.data_size):
            #if i % 100 == 0:
                #print('filtrando: ' + str(i*100//self.data_size) + '%')
            self.data[i][self.main_key] = norm.normalise(self.data[i][self.main_key])
            self.data[i][self.main_key] = sbj_filter.run_filter(self.data[i][self.main_key])
        
        #print('filtrando: 100%')
    
    def run(self, save_partial_results = False):
       
        called_dir = os.getcwd()
        os.chdir(self.script_dir)
        try:
            # Verifica se será aplicado módulo para extrair revisoes de produtos
            if(self.crawl_reviews):
                #print("Resgatando revisões para '" + self.search + "' ...")
                #os.chdir(self.script_dir + "/" + 'review_crawler')
                #na versao web, cada usuario precisa ter seu proprio crawler
                os.chdir(os.path.join(self.script_dir, self.data_folder, "review_crawler"))
                run_crawler(self.search)
                os.chdir(self.script_dir)
                #copiando arquivo da saida do crawler para o diretorio padrao do script
                if(self.load_data_from_file(os.path.join(self.data_folder, 'review_crawler/reviews.json'))):
                    if(save_partial_results):
                        self.write_results(self.data, self.data_folder + 'crawled_data.json')
                    print("Revisões encontradas:")
                    print(self.data_size)
                else:
                    print('Não foi possível extrair revisões.')
                    return

            # nesse ponto, não pode continuar se os dados não foram carregados ainda
            elif self.data == None:
                print('Nenhum dado disponivel ...')
                return
            
            # --- Filtro de Qualidade de Revisao ---
            if(self.filter_quality_mlp):
                os.chdir('TopXMLP')
                #print("Inicializando TopX-MLP e filtrando por qualidade")
                self.data = run_mlp_filter((self.data, self.main_key), self.data_size, grade='good', metric=1) 
                os.chdir(self.script_dir)
                if(save_partial_results):
                    self.write_results(self.data, self.data_folder + 'mlp_filtered_data.json')
            
            # FILTRO FUZZY NAO DISPONIVEL PARA VERSAO WEB
            #elif(self.filter_quality_fuzzy):
                #print("Inicializando TopX Fuzzy e filtrando por qualidade")
                #os.chdir('TopXFuzzy')
                #self.data = run_fuzzy(self.data)
                #os.chdir(self.script_dir)
                #if(save_partial_results):
                #    self.write_results(self.data, self.data_folder + 'fuzzy_filtered_data.json')
            
            # --- Normalizador ---
            if(not self.filter_subjectivity and self.normalize):
                self.normalize_data()   #modifica os dados carregados
                if(save_partial_results):
                    self.write_results(self.data, self.data_folder + 'norm_data.json')

            # --- Normalizador com Filtro de Subjetividade---
            elif(self.filter_subjectivity):
                self.normalize_and_filter() #modifica os dados carregados
                if(save_partial_results):
                    self.write_results(self.data, self.data_folder + 'filtered_sbj_data.json')
                
            # --- Identificador e Classificador de Aspectos ---
            if(self.classify_aspects):
                
                os.chdir('classificador_aspectos')
                
                #print("Inicializando classificador de aspectos")
                asp_classifier = aspect_classifier.Aspect_classifier()
                self.plotter_data = asp_classifier.run(self.data, self.main_key) 
                 
                os.chdir(self.script_dir)
                
                if(save_partial_results):
                    self.write_results(self.plotter_data, self.data_folder + 'aspect_data_plot.json')
                
                # --- Plotagem dos Aspectos ---
                plotter = Aspect_plotter(self.plotter_data)
                #-- versao web ira apenas inicializar o plotter jogando json pra stdout
                #-- a plotagem de fato ficará a cargo do lado cliente
                #plotter.plot_by_aspect(style='bars')
                #plotter.plot_by_aspect(style='pie')
                #plotter.plot_by_aspect(style='treemap')
                #plotter.plot_general()
           

            self.write_data()
            # --- Sumarizador de Opiniao ---
            if(self.summarize != 'False'):
                os.chdir('opizer')
                run_opizer(self.summarize, self.data, self.main_key, self.annot_key, 'id') 
                os.chdir(self.script_dir)

                
            #escreve dados apos todos os processamentos solicitados 
            self.write_data()
            
            #apos finalizar processamento, deleta os dados gerados
            self.clean_up()

        except:
            #se algo der errado, eliminar rastros dos diretorios criados
            self.clean_up()

        os.chdir(called_dir)

if __name__ == '__main__':
   

    #p1 = 'brastemp ative'                               #200 +
    #p2 = 'Brastemp BWK11AB Superior 11 Kg Branco'       #600 +
    #p3 = 'iphone 6 16GB'                                #400 +
    #p4 = 'iphone 5s 16GB'                               #1100 +
    #p5 = 'Smartphone Samsung Galaxy J5 SM-J500M 16GB'   #1400 +
    #p6 = 'Smartphone Apple iPhone 7 32GB'               #70
    #p7 = 'Smartphone Motorola Moto G G7 Plus XT1965-2 64GB'
    

    operation = sys.argv[1]
    
    data = sys.argv[2]
    if operation == "pipeline":
    
        sent = Sentiment_pipeline(
                search=data,
                crawl_reviews=True,
                filter_subjectivity=True,
                classify_aspects=True,
                filter_quality_fuzzy=False,
                filter_quality_mlp=True,
                summarize='opizere'
                )
        #sent.load_data_from_file('review_crawler/reviews.json')
        #roda pipeline para versao web, portanto resultados intermediarios nao serao usados
        sent.run(save_partial_results=False)    

    
    #realizando apenas normalizacao com enelvo
    elif operation == "normalization":
        
        sent = Sentiment_pipeline(
                crawl_reviews=False,
                filter_subjectivity=False,
                classify_aspects=False,
                filter_quality_fuzzy=False,
                filter_quality_mlp=False,
                summarize='False',
                normalize=True
                )
        sent.set_data(data, separator='\n')
        sent.run(save_partial_results=False)
        #imprime o texto normalizado
        print("\n")
        for value in sent.data:
            print(value["revisao"])
    
    #realizando filtragem por qualidade
    elif operation == "qltFilter":
        
        sent = Sentiment_pipeline(
                crawl_reviews=False,
                filter_subjectivity=False,
                classify_aspects=False,
                filter_quality_fuzzy=False,
                filter_quality_mlp=True,
                summarize='False',
                normalize=False
                )
        sent.set_data(data, separator='\n')
        sent.run(save_partial_results=False)
        
        #imprime o texto processado
        print("\n")
        #configurando saida para formato legível
        for rev in sent.data:
            quality = int(rev['qualidade'])
            text = "Revisão de qualidade " + rev['qualidade'] + ' - '
            if quality > 1:
                text += 'mantida:\n'
                text += '\t'+rev['revisao'] + '\n'
            else:
                text += 'removida:\n'
                text += '\t'+rev['removido'] + '\n'
            print(text)

    #realizando filtragem por subjetividade
    elif operation == "sbjFilter":
        
        sent = Sentiment_pipeline(
                crawl_reviews=False,
                filter_subjectivity=True,
                classify_aspects=False,
                filter_quality_fuzzy=False,
                filter_quality_mlp=False,
                summarize='False',
                normalize=False
                )
        sent.set_data(data, separator = '\n')
        sent.run(save_partial_results=False)
        #imprime o texto processado
        print("\n")
        text = "Mostrando as sentenças mantidas:\n\t"
        for value in sent.data:
            text += value["revisao"]
        print(text)

    #realizando extracao e classificacao de aspectos
    elif operation == "aspect":
        
        sent = Sentiment_pipeline(
                crawl_reviews=False,
                filter_subjectivity=False,
                classify_aspects=True,
                filter_quality_fuzzy=False,
                filter_quality_mlp=False,
                summarize='False',
                normalize=False
                )

        sent.set_data(data, separator='\n')
        sent.run(save_partial_results=False)
        #imprime o texto processado
        print("\n")
        print(sent.data)
        #for value in sent.data:
        #    print(value["revisao"])

    #realizando sumarizacao
    elif operation == "opizer":
        
        sent = Sentiment_pipeline(
                crawl_reviews=False,
                filter_subjectivity=False,
                classify_aspects=True,
                filter_quality_fuzzy=False,
                filter_quality_mlp=False,
                summarize='opizere',
                normalize=False
                )
        sent.set_data(data, separator="\n")
        sent.run(save_partial_results=False)
        #imprime o texto normalizado
        #print("\n")
        #print(sent.data)
        #for value in sent.data:
        #    print(value["revisao"])
    



