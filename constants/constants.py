from enum import Enum

class FileExt(Enum):
    PDF = "pdf"
    JSON = "json"
    INDEX = "index"

defaultSearchRes = "I Don't know"
queryAnsString = """You are a helpful assistant. Answer the question using ONLY the information provided.

Question: {}
Context: {}
AAAAAAAnswer:"""