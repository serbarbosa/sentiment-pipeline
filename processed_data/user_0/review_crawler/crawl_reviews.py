from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os
import shutil

def run_crawler(product):
    #seguindo a documentacao do scrapy ('run Scrapy from a script')
    
    json_filename = 'reviews.json'
    
    #deleta arquivo csv se esse ja existir
    try:
        os.remove(json_filename)
    except OSError:
        pass

    #personalizando configuracoes
    settings = get_project_settings()
    settings.set('LOG_ENABLED', False)
    settings.set('FEED_FORMAT', 'json')
    settings.set('FEED_URI', 'reviews.json')
    settings.set('FEED_EXPORT_ENCODING', 'utf-8')
    settings.set('ROBOTSTXT_OBEY', False)

    process = CrawlerProcess(settings)

    #limpando pasta para guardar as novas revisoes
    try:
        shutil.rmtree('reviewsFiles')
    except FileNotFoundError:
        pass
    os.makedirs('reviewsFiles')

    process.crawl('review_crawler', search=product)
    process.start()
    #os.system('scrapy crawl %s %s %s %s %s %s %s' % ('buscape_crawler', '-s', 'HTTPCASH_ENABLED=1', '-o', 'reviews.csv', '-a', 'search="'+search+'"'))


if __name__ == "__main__":
    
    run_crawler('iphone 6s 16GB')
    
    
    
    
