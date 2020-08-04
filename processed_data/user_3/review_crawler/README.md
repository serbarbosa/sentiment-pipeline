# reviewCrawler


Um script para resgatar revisões de usuários sobre determinado produto utilizando *Scrapy*.

Até o momento, as revisões são obtidas apenas do site buscapé.
Basicamente recebe-se o produto pelo qual se quer buscar e são extraídas as revisões do primeiro resultado do Buscapé.

O objetivo é usar o link do primeiro resultado para acessar também as outras lojas que vendem o mesmo produto
(americanas, submarino, magazine luiza) e aumentar a base de revisões do produto buscado.

---


**Execução**

É necessário ter o framework *Scrapy* para executar o crawler. Convenientemente o diretório desse README já possui um ambiente virtual com o *Scrapy*.
Para ativá-lo basta usar o comando:

```
source .venv/bin/activate
```

Então, para rodar o script pode-se optar por usar o `Makefile` ou `scrapy crawl` lembrando sempre de setar o parâmetro `search`.
Exemplo usando o Makefile (verificar arquivo Makefile para mais opções):

```
make csv search='brastemp ative'
```

Exemplo usando direto o *Scrapy* (não vai gerar csv):

```
scrapy crawl buscape_crawler -a search='brastemp ative'
```

**Saída**

As revisões encontradas serão sempre escritas em arquivos *.txt* individuais no diretório *reviewsFiles*. Note que os arquivos não são apagados a cada execução, apenas sobrescritos e, portanto, podem sobrar arquivos da execução anterior.

É possível ainda obter os resultados em arquivos *.csv*, *.json* ou qualquer outro formato suportado pelo *Scrapy* bastando apenas adicionar a tag correspondente na execução. Diferentemente dos arquivos *.txt*, essa saída mostrará mais dados, como a data da revisão, uma avaliação de 1 a 5 estrelas e se o usuário recomenda ou não o produto.

