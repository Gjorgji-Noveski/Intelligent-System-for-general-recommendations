from spacy import displacy
import spacy
import re
# DALI SO ILI BEZ PARSER/SENTECIZER ne pravi nekoja golema razlika vo delenje na rechenici

with open("C:/Users/Gjorgji Noveski/Desktop/Files for my Spacy work/Files for evaluating a model/za vezbanje.txt", encoding="UTF-8", mode='r') as f:
    sfe = f.read()
nlp = spacy.load('C:/Users/Gjorgji Noveski/Desktop/Files for my Spacy work/NLP models and bin training data/20eph 850sents')
nlp.disable_pipes('parser')
nlp.add_pipe(nlp.create_pipe('sentencizer'))
doc = nlp(sfe)
displacy.serve(doc, style='ent')