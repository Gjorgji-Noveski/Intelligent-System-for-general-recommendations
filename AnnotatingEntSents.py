import os
import re
from WordSetAndMappings import DATASET, ARCHITECTURE_TYPE, ACTIVATION_FUNC, BUILDING_BLOCKS
EXTRACTED_ENT_SENTS_PATH = r'C:\Users\Gjorgji Noveski\Desktop\nov spacy test\Extracted Entity Sents, one phrase entity'
ANNOTATED_ENT_SENTS_PATH = r'C:\Users\Gjorgji Noveski\Desktop\nov spacy test\Annotated dataset AMA SO PRAZNO MESTO'

"""
Mozhe samo da barame za auto encoder pa posle da izvlecheme ako zborot pred nego e denoising, variational itn.
istoto mozhe i za neural network da bide, primer samo neural network da barame i posle da izvlecheme i za boltzman machine
"""

# TODO: DODADOV CNN nemashe,Anotiraj gi pak
##

CATEGORIES = {'dataset model': DATASET, 'architecture type model': ARCHITECTURE_TYPE,
              'activation function model': ACTIVATION_FUNC, 'building blocks model': BUILDING_BLOCKS}

"""
Annotates all the corpora and saves them in their dedicated folder (based on entity category, a.k.a model)
"""
def annotateByCategory(inputPath, outputPath):
    global CATEGORIES
    for file in os.listdir(inputPath):
        with open(os.path.abspath(os.path.join(inputPath, file)), mode='r', encoding='utf-8') as entSentFile:
            allLines = entSentFile.readlines()
        for category in CATEGORIES.keys():
            annotatedCategoryPath = os.path.join(outputPath, category)
            annotatedFile = os.path.join(annotatedCategoryPath, file)
            if not os.path.exists(annotatedCategoryPath):
                os.makedirs(annotatedCategoryPath)
            sentences = set()
            for line in allLines:
                line = line.replace('{', '').replace('}', '')

                # Extracting only the sentences that i managed to annotate
                annotatedAnEntity = False
                for entity in CATEGORIES[category]:
                    regex = r'(?<=\()' + entity + r's?(?=\))|(?<=\s)' + entity + r'(?=\s)'

                    # Using regex to search for singular and plural of entities and if they also appear in '( )' brackets.
                    matchObjIter = re.finditer(regex, line, flags=re.IGNORECASE)
                    for counter, match in enumerate(matchObjIter):
                        # using counter so i can annotate more than 1 entity in one sentence, without it the array positions won't be correct for the 2nd annotation
                        annotatedAnEntity = True
                        line = line[:match.start() + (2 * counter)] + '{' + match.group() + '}' + line[match.end() + (2 * counter):]


                # Ovie 2 for loops, ako ima neshto sto ne e prazno mesto pred entitetot i posle, mu dadavam prazno mesto, za da ima alignment so spacy tokenizer
                timesOpeningBracket = line.count('{')
                foundIdx = 0
                for i in range(timesOpeningBracket):
                    foundIdx = line.find('{', foundIdx +1)
                    if line[foundIdx - 1] != ' ':

                        line = line[:foundIdx] + ' ' + line[foundIdx:]

                timesClosingBracket = line.count('}')
                foundIdx = 0
                for i in range(timesClosingBracket):
                    foundIdx = line.find('}', foundIdx + 1)
                    if line[foundIdx + 1] != ' ':
                        line = line[:foundIdx + 1] + ' ' + line[foundIdx+1:]
                if annotatedAnEntity:
                    sentences.add(line)
            with open(annotatedFile, encoding='utf-8', mode='a')as fw:
                fw.writelines(sentences)
            print("Annotated " + category + ' - ' + file)


annotateByCategory(EXTRACTED_ENT_SENTS_PATH, ANNOTATED_ENT_SENTS_PATH)
