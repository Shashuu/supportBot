# scripts

# scrape the data from pdf and web
python3.8 scrape.py --conf config/scraperConfig.yaml

# indexer: load the scrapped data, cleansed, generate embedding and index
python3.8 indexer.py --indexDir data/indexes --dataDir data/scraper/out --extType json --conf config/index.yaml --embedConf config/embedConfig.yaml --indexConf config/searcher.yaml

# micro services

# embed generator : generate the embedding
python3.8 embedGen.py --conf config/embedConfig.yaml --port 8081

# embed searcher : load the index and search the req embedding
python3.8 embedSearcher.py --conf config/searcher.yaml --index data/indexes/pdf.index --lp logs/s1 --dataMap data/indexes/dataMap.json --port 8082
python3.8 embedSearcher.py --conf config/searcher.yaml --index data/indexes/web.index --lp logs/s2 --dataMap data/indexes/dataMap.json --port 8083 

# support bot : 
# call embedding service
# call embed searcher, and return the string
# generate result string

python3.8 supportBot.py --conf config/supportBot.yaml