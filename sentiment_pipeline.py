import os, os.path
import sys
import shutil
import time

#resolvendo imports para subdiretorios
main_dir = os.getcwd()
sys.path.insert(0,main_dir + '/classificador_aspectos')
sys.path.insert(0,main_dir + '/uteis')
#sys.path.insert(0,main_dir + '/filtro_subjetividade')

from review_crawler.crawl_reviews import run_crawler
from filtro_subjetividade.sbj_filter import Subjectivity_filter
from classificador_aspectos import aspect_classifier
from classificador_aspectos.aspect_plotter import Aspect_plotter
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

    def __init__(self, search = 'Samsung galaxy s7', normalize = True,classify_aspects = False,
                filter_quality_fuzzy=False, filter_subjectivity=True, crawl_reviews=True, main_key='revisao'):
        
        self.crawl_reviews = crawl_reviews
        self.search = search
        self.normalize = normalize
        self. classify_aspects = classify_aspects
        self.filter_quality_fuzzy = filter_quality_fuzzy
        self.filter_subjectivity = filter_subjectivity
        self.data = None
        self.data_size = 0
        self.data_folder = 'processed_data/'
        self.data_filename = 'data.json'
        self.main_key = main_key
        self.script_dir = os.getcwd()

    def clean_up(self):
        '''Reinicia o diretorio padrao, deletando todos os arquivos presentes nele.'''
        shutil.rmtree(self.data_folder)
        os.makedirs(self.data_folder)

    def set_data_folder(self, folder : str):
        '''Define a pasta destino para os dados.'''
        self.data_folder = folder

    def set_data_filename(self, filename : str):
        '''Define o nome de arquivo que será escrito.'''
        self.data_filename = filename
    
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
        with open(self.data_folder + self.data_filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f)
        if(free_data):
            self.data = None
    
    def write_results(self, data : List[Dict], filepath : str):
        '''Salva o dado informado no diretorio informado como arquivo .json.'''
        #TODO tratar tipo de dado incorreto
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f)
    
    def load_results(self, filepath : str) -> List[Dict]:
        'Carrega e retorna os dados do arquivo .json informado.'''
        #TODO tratar falha na leitura
        data = None
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    
    def run_filter_fuzzy(self, par1, par2):
        '''Faz filtragem dos dados por sua qualidade usando método fuzzy.'''
        pass

    def normalize_data(self):
        '''Normaliza os dados com enelvo.'''

        print("Inicializando normalizador ...")
        norm = normaliser.Normaliser()

        for i in range(self.data_size):
            self.data[i][self.main_key] = norm.normalise(self.data[i][self.main_key])
        
    def normalize_and_filter(self):
        '''Normaliza os dados com enelvo e em seguida realiza a filtragem por subjetividade.'''

        print("Inicializando normalizador ...")
        norm = normaliser.Normaliser()
        
        print("Inicializando filtro de subjetividade ...")
        sbj_filter = Subjectivity_filter('filtro_subjetividade')
        
        for i in range(self.data_size):
            if i % 100 == 0:
                print('filtrando: ' + str(i*100//self.data_size) + '%')
            self.data[i][self.main_key] = norm.normalise(self.data[i][self.main_key])
            self.data[i][self.main_key] = sbj_filter.run_filter(self.data[i][self.main_key])
        
        print('filtrando: 100%')
    
    def run(self, save_partial_results = False):
        
        # Verifica se será aplicado módulo para extrair revisoes de produtos
        if(self.crawl_reviews):
            self.clean_up()
            print("Resgatando revisões para '" + self.search + "' ...")
            os.chdir('review_crawler')
            run_crawler(self.search)
            os.chdir(self.script_dir)
            #copiando arquivo da saida do crawler para o diretorio padrao do script
            if(self.load_data_from_file('review_crawler/reviews.json')):
                if(save_partial_results):
                    self.write_results(self.data, self.data_folder + 'crawled_data.json')
            else:
                print('Nao foi possivel extrair revisoes')
                return

        #nesse ponto, não pode continuar se os dados não foram carregados ainda
        elif self.data == None:
            print('Nenhum dado disponivel ...')
            return
            
        if(self.filter_quality_fuzzy):
            print("Inicializando Topx e filtrando por qualidade")
            run_filter_fuzzy('','')
            if(save_partial_results):
                self.write_results(self.data, self.data_folder + 'fuzzy_filtered_data.json')

        if(not self.filter_subjectivity and self.normalize):

            self.normalize_data()   #modifica os dados carregados
            if(save_partial_results):
                self.write_results(self.data, self.data_folder + 'norm_data.json')

        elif(self.filter_subjectivity):
            self.normalize_and_filter() #modifica os dados carregados
            if(save_partial_results):
                self.write_results(self.data, self.data_folder + 'filtered_sbj_data.json')
            
        if(self.classify_aspects):
            
            os.chdir('classificador_aspectos')
            
            print("Inicializando classificador de aspectos")
            asp_classifier = aspect_classifier.Aspect_classifier()
            self.data = asp_classifier.run(self.data, self.main_key) 
           
            os.chdir(self.script_dir)
            
            if(save_partial_results):
                self.write_results(self.data, self.data_folder + 'classified_data.json')
            

            plotter = Aspect_plotter(self.data)
            plotter.plot_by_aspect(style='bars')
            plotter.plot_by_aspect(style='pie')
            plotter.plot_by_aspect(style='treemap')
            plotter.plot_general()
        
        #escreve dados apos todos os processamentos solicitados 
        self.write_data()


if __name__ == '__main__':
    
    p3 = 'brastemp ative'                               #200 +
    p4 = 'Brastemp BWK11AB Superior 11 Kg Branco'       #600 +
    p1 = 'iphone 6 16GB'                                #400 +
    p2 = 'iphone 5s 16GB'                               #1100 +
    p6 = 'Smartphone Samsung Galaxy J5 SM-J500M 16GB'   #1400 +

    sent = Sentiment_pipeline(search=p6,crawl_reviews=True, filter_subjectivity=True, classify_aspects=True)
    #sent.load_data_from_file('review_crawler/reviews.json')
    sent.run(save_partial_results=True)


