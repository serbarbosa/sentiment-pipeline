import scrapy
import sys, os
import math

class BuscapeReviewSpider(scrapy.Spider):

    name = 'review_crawler'

    def __init__(self, search):
        buscape_url = 'https://www.amazon.com.br'
        #comeca acessando url correspondente a busca solicitada
        self.start_urls = [buscape_url + '/s?k=' + search.replace(' ', '+')]
        self.review_counter = 0
        self.review_amnt = 0
        self.per_page = 10       #numero de revisoes mostradas por pagina na amazon
        self.search = search
        self.maxReviews = 2000

    def parse(self, response):
        # Recupera o href para o primeiro resultado da busca.

        first_product = response.css('.a-size-mini.a-spacing-none a::attr(href)').get()
        #vamos agora acessar a pagina do produto
        yield scrapy.Request(
            response.urljoin(first_product),
            callback=self.parse_product_page
        )

    def parse_product_page(self, response):
        # Verifica se ha revisoes em portugues e acessa pagina de revisoes

        #recupera e imprime nome do produto acessado
        product_name = response.css("#productTitle::text").get().strip()
        if len(product_name) > 50:
            print(product_name[:50] + "(...)")
        else:
            print(product_name)

        reviews_page = response.css("#reviews-medley-footer a::attr(href)").get()
        yield scrapy.Request(
            response.urljoin(reviews_page),
            callback=self.parse_reviews_pages
        )


    def parse_reviews_pages(self, response):
        #verifica a quantidade de revisoes em portugues e solicita em loop a extração das revisoes ate um limite de 5000
        self.review_amnt = int(response.css("#filter-info-section span::text").get().split()[-2].replace('.', ''))
        if self.review_amnt > self.maxReviews:
            self.review_amnt = self.maxReviews
        page_amnt = math.ceil(self.review_amnt/self.per_page)
        url = response.url.split("?")[0]

        for i in range(1, page_amnt+1):
            yield scrapy.Request(                                             # adicao-> ie=UTF8&reviewerType=all_reviews&           
                url + "/ref=cm_cr_arp_d_paging_btm_next_"+str(i)+"?ie=UTF8&reviewerType=all_reviews&pageNumber="+str(i),
                callback=self.parse_reviews
            )

    def parse_reviews(self, response):

        #selecionando containers com revisoes
        reviews = response.css(".review")
        #para cada container de revisao, extrair e exportar dados desejados
        for i in range(len(reviews)):

            date = reviews[i].css('.review-date::text').get()[22:]
            stars = reviews[i].css('a::attr(title)').get()[0]
            recommended = ''    #amazon nao fornece essa classificacao
            title = reviews[i].css(".review-title span::text").get()
            helpful = ""
            review_body = reviews[i].css('.review-text-content span::text').get()

            try:
                helpful = reviews[i].css(".cr-vote span::text").get().split()[0]
            except:
                helpful = "0"

            #with open('reviewsFiles/' + str(self.review_counter) + '.txt', 'w') as rev:
            #    rev.write(review_body + '\n')
            self.review_counter += 1

            yield{
                'id' : self.review_counter-1,
                'data' : date,
                'estrelas' : stars,
                'relevancia' : helpful, #quantidade de upvotes dados pelos usuarios da plataforma
                'titulo' : title,
                'revisao' : review_body
            }
