from scraper.interface import Parser

import requests
from bs4 import BeautifulSoup

from utils.commonUtil import pathConstruct, saveFile
from constants.constants import FileExt

class WebScraper(Parser):
    def __init__(self, conf, log, *args, **kwargs):
        self.baseURL = conf["baseURL"]
        self.outpath = pathConstruct(conf["outDir"], conf["outFile"])
        self.log = log

        self.interimURLs = list()
        self.parsedURLs = set()
        self.faqs = dict()
    
    def get_parser_obj(self, content):
        return BeautifulSoup(content, "html.parser")
    
    def add_faq(self, ques, ans):
        self.faqs.update({ques: ans})
    
    def get_content(self, url):
        res = requests.get(url=url)
        
        try:
            res.raise_for_status()
            return res.content
        except Exception as e:
            self.log.exception(f"failed to extract content with reason {str(e)}")      
            return None
    
    def extract_faq_question(self, parseTree):
        ques = ""
        try:
            tabLabelElem = parseTree.find("label", class_="tab-label")
            if not tabLabelElem:
                return None
            
            spanElem = tabLabelElem.find("span")
            if not spanElem:
                return None
            
            if spanElem.text:
                ques = str(spanElem.text).strip() 
        except Exception as e:
            self.log.exception(f"failed while extracting faq question with the reason {str(e)}")
        
        return ques
    
    def extract_faq_answer(self, parseTree):
        answer = ""
        try:
            tabContentElem = parseTree.find("div", class_="tab-content")
            if not tabContentElem:
                return None
            
            spanElem = tabContentElem.find("div", class_="content")
            if not spanElem:
                return None
            
            for child in spanElem.children:
                answer += child.text
                answer += " "
        except Exception as e:
            self.log.exception(f"failed while extracting faq answer with the reason {str(e)}")

        return answer

    def extract_faq(self, parseTree):
        faqs = dict()
        
        try:
            listOfContents = parseTree.findAll("div", class_= "list-content")

            for listOfContent in listOfContents:
                for subSection in listOfContent.findAll("div", class_= "tab"):
                    ques = self.extract_faq_question(subSection)
                    sol = self.extract_faq_answer(subSection)

                    if ques and sol:
                        faqs[ques] = sol
        except Exception as e:
            self.log.exception(f"failed while extracting faq Q&A with the reason {str(e)}")
        
        return faqs

    def extract_parent_urls(self, parseTree):
        links = set()

        try:
            gridItems = parseTree.findAll("div", class_="cat-grid")   
            if not gridItems:
                return links
            
            for gridItem in gridItems:
                items = gridItem.findAll("a", class_="learn-more")
                if not items:
                    continue
                
                for item in items:
                    if item.get("href"):
                        links.add(item["href"])
        except Exception as e:
            self.log.exception(f"failed while extracting parent urls with the reason {str(e)}")

        return list(links)

    def extract_child_urls(self, parseTree):
        links = set()
        try:
            listItems = parseTree.findAll("div", class_ ="list-item")
            
            if not listItems:
                return links
            
            for listItemSec in listItems:
                unorderedList = listItemSec.findAll("ul")
                for listItem in unorderedList:                
                    items = listItem.findAll("li")
                    for item in items:
                        aElement = item.find("a")
                        if aElement.get("href"):
                            links.add(aElement["href"])
        except Exception as e:
            self.log.exception(f"failed while extracting child urls with the reason {str(e)}")
        
        return links        

    def parse_content(self, parseTree):
        extracted_urls = self.extract_child_urls(parseTree)
        for url in extracted_urls:
            if (url not in self.parsedURLs) and (url not in self.interimURLs):
                self.interimURLs.append(url)

        extracted_faqs = self.extract_faq(parseTree)
        for ques, ans in extracted_faqs.items():
            self.add_faq(ques, ans)

    def start(self):
        baseObj = self.get_content(self.baseURL)
        baseTree = self.get_parser_obj(baseObj)
        self.parentURLs = self.extract_parent_urls(baseTree)
        self.interimURLs.extend(self.parentURLs)
        olderFAQCount = 0

        while self.interimURLs:
            url = self.interimURLs[0]       
            self.log.info(f"started processing for url {url}")
            content = self.get_content(url=url)

            parseTree = self.get_parser_obj(content)
            self.parse_content(parseTree)

            self.parsedURLs.add(url)
            self.interimURLs.pop(0)
            self.log.info(f"completed processing for url {url} and added {len(self.faqs) - olderFAQCount} FAQs.")
            olderFAQCount = len(self.faqs)
        
        self.log.info(f"no of questions extracted {len(self.faqs)}")
        saveFile(self.faqs, self.outpath, FileExt.JSON)

# ws = WebScraper(baseURL="https://www.angelone.in/support")
# ws.start()