from sentence_transformers import SentenceTransformer

class EmbedGen:
    def __init__(self, model, *args, **kwargs):
        self.model = SentenceTransformer(model)

    def getEmbed(self, sentence):
        return self.model.encode(sentence)
