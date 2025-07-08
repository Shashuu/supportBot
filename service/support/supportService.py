import json
from utils.commonUtil import cleansedText, formatCleanseTheRecord

from concurrent.futures import ThreadPoolExecutor
from constants.constants import defaultSearchRes

class SupportService:
    def __init__(self, reqHandler, embGenURL, searchURL, answerHandler, threshold, log, *args, **kwargs):
        self.reqHandler = reqHandler

        self.embGenURL = embGenURL
        self.searchURL = searchURL

        self.answerHandler = answerHandler

        self.executor = ThreadPoolExecutor(max_workers = 2*len(searchURL))

        self.threshold = threshold
        
        self.log = log

    def getPotentialResult(self, searchResults):
        candidate = searchResults[0]["data"][0] if searchResults[0]["data"][0]["score"] > searchResults[1]["data"][0]["score"] else searchResults[1]["data"][0]
        return candidate["text"], candidate["score"]
    
    def getEmbedding(self, query):
        try:
            embRes = self.reqHandler.post(url = self.embGenURL, payload = json.dumps({"data": query}))
            embRes.raise_for_status()

            embResJSON = embRes.json()

            emb = embResJSON.get("data", {"embedding": []})["embedding"]

            if emb:
                return True, emb
            
            self.log.exception(f"found empty embedding, for quert {query}")
            return False, emb
        except Exception as e:
            self.log.exception(f"failed while interacting to generate the embedding, with reason {str(e)}")
            return False, list()

    def getCandidates(self, embedding):
        try:
            payload = json.dumps({
                "embedding": embedding
                })
            
            searchResults = self.executor.map(lambda args: self.reqHandler.post(*args), [(url, payload) for url in self.searchURL])
            searchResJSONs = [res.json() for res in searchResults]

            return True, searchResJSONs
        except Exception as e:
            self.log.exception(f"failed to get the candidates with reason {str(e)}")
            return False, list()
    
    def getAnswer(self, query, context):
        response = self.answerHandler.generate(query, context)
        return response
    
    def cleanQuery(self, query):
        return formatCleanseTheRecord(cleansedText(query))
    
    def checkTheThreshold(self, score):
        return True if score > self.threshold else False

    def getSupport(self, query):
        query = self.cleanQuery(query) 
        status, emb = self.getEmbedding(query=query)
        candidate = None
        if not status:
            self.log.error(f"failed to retrieve the embedding")
            return "try after sometime!", candidate
        searchStatus, searchResults = self.getCandidates(embedding=emb)
        answer = defaultSearchRes
        

        if searchStatus:
            print(searchResults)
            candidate, score = self.getPotentialResult(searchResults = searchResults)
            if not self.checkTheThreshold(score):
                return answer, None
            answer = self.getAnswer(query, json.dumps(candidate))
            
        return answer, candidate
        