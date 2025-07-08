import faiss
import numpy as np

from utils.commonUtil import pathConstruct

class SearcherIndexService:
    def __init__(self, dim, topK, log, indexPath=None, *args, **kwargs):
        if indexPath:
            #indexPath = pathConstruct(indexDir, indexName)
            self.ind = faiss.read_index(indexPath)
        else:
            self.ind = faiss.IndexFlatIP(dim)
            self.ind = faiss.IndexIDMap(self.ind)
        
        self.topK = int(topK)
        self.log = log
    
    def index(self, embedding, id):
        try:
            if embedding.ndim == 1:
                embedding = embedding.reshape(1, -1)
            self.ind.add_with_ids(np.array(embedding, dtype='float32'), np.array([id], dtype='int64'))
            return True
        except Exception as e:
            self.log.exception(f"failed to index with reason {str(e)}")
            return False
    
    def search(self, embedding):
        if type(embedding) == list:
            embedding = np.array(embedding, dtype='float32')
        if len(embedding.shape) == 1:
            embedding = embedding.reshape(1, -1)
        return self.ind.search(embedding, k=self.topK)
    
    def save(self, outpath):
        return faiss.write_index(self.ind, outpath)
    
    def count(self):
        return self.ind.ntotal
