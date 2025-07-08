'''
from transformers import pipeline

class AnswerGen:
    def __init__(self, task, model, maxLength, *args, **kwargs):
        self.model = pipeline(task=task, model=model)
        self.maxLength = maxLength
    
    def generate(self, query, context):
        res = self.model({"question": query, "context": context}, max_length=self.maxLength)
        return res["answer"]
'''

from transformers import AutoTokenizer, AutoModelForCausalLM
from constants.constants import queryAnsString

class AnswerGen:
    def __init__(self, model_id, maxLength, *args, **kwargs):
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(model_id)
        self.maxLength = maxLength
    
    def generate(self, query, context):
        inputs = self.tokenizer(queryAnsString.format(query, context), return_tensors="pt")
        res = self.model.generate(**inputs, max_new_tokens=self.maxLength)
        sol = self.tokenizer.decode(res[0], skip_special_tokens=True)
        return sol.split('AAAAAAAnswer:')[1].strip('\n')
