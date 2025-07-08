import argparse

#from scraper.webScraper import WebScraper
from service.scraper.PDFParser import PDFParser

from utils.commonUtil import getConfig, pathConstruct
from utils.logger import scrapperLogger

import warnings

warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser()
parser.add_argument("--conf")
args = parser.parse_args()

conf = getConfig(args.conf)

initArgs = conf["webScraper"]
initArgs["outpath"] = pathConstruct(initArgs["outDir"], initArgs["outFile"])
scraperLog = scrapperLogger(filename = initArgs["logPath"])

initArgs["log"] = scraperLog
#webscraper = WebScraper(**initArgs)
pdfparser = PDFParser(conf["pdfScraper"], log=scraperLog)

#webscraper.start()
pdfparser.start()