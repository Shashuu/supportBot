import json
import re

class Cleanser:
    @staticmethod
    def format(record):
        return json.dumps(record).lower()

    @staticmethod
    def cleanse(string):
        return re.sub(r"[^\w\s]", '', string.strip().replace('\n', ' '))
    
    @staticmethod
    def basicCleanse(string):
        return string.replace("\n", " ").lower()

