headlessCsv:
	scrapy crawl buscape_crawler -s HTTPCASH_ENABLED=1 -o reviews.csv -a search='$(search)' -t headless
csv:
	scrapy crawl buscape_crawler -s HTTPCASH_ENABLED=1 -o reviews.csv -a search='$(search)' --nolog
run:
	scrapy crawl buscape_crawler -s HTTPCASH_ENABLED=1 -a search='$(search)'
