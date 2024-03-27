
import spacy

'''
Model from sciSpacy
https://github.com/allenai/scispacy?tab=readme-ov-file 
pip installing scispacy needs me to upgrade my C++ VS installer
takes too much space, so i'm using just the model and loading it with spacy
more functionalities can be added using scispacy
'''
class QueryGenerator:
    def __init__(self):
        self.nlp = spacy.load("en_core_sci_sm")

    def generate(self, text):
        doc = self.nlp(text)

        print("Noun phrases:", [chunk.text for chunk in doc.noun_chunks])
        print("Verbs:", [token.lemma_ for token in doc if token.pos_ == "VERB"])

        entities = []
        for entity in doc.ents:
            entities.append((entity.text, entity.label_))

        return entities



