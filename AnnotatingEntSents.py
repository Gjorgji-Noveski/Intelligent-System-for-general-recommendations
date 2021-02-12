import os
import re
import plac
from WordSetAndMappings import ARCHITECTURE_TYPE, ACTIVATION_FUNC, BUILDING_BLOCKS
EXTRACTED_ENT_SENTS_PATH = r'C:\Users\Gjorgji Noveski\Desktop\nov spacy test\Extracted Entity Sents, one phrase entity'
ANNOTATED_ENT_SENTS_PATH = r'C:\Users\Gjorgji Noveski\Desktop\nov spacy test\Annotated dataset AMA SO PRAZNO MESTO'
TRUE_OUTPUT_PATH =r'corpora/annotated'
"""
Mozhe samo da barame za auto encoder pa posle da izvlecheme ako zborot pred nego e denoising, variational itn.
istoto mozhe i za neural network da bide, primer samo neural network da barame i posle da izvlecheme i za boltzman machine
"""


CATEGORIES = {'architecture type model': ARCHITECTURE_TYPE, 'activation function model': ACTIVATION_FUNC,
              'building blocks model': BUILDING_BLOCKS}

"""
Annotates all the corpora and saves them in their dedicated folder (based on entity category, a.k.a model)
"""
def annotateByCategory(allLines, category):
    sentences = set()
    for line in allLines:
        line = line.replace('{', '').replace('}', '')
        # Extracting only the sentences that i managed to annotate
        annotatedAnEntity = False
        for entity in CATEGORIES[category]:
            regex = r'(?<=\()' + entity + r's?(?=\))|(?<=\s)' + entity + r's?(?=\s)'

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
            foundIdx = line.find('{', foundIdx + 2)
            if line[foundIdx - 1] != ' ':

                line = line[:foundIdx] + ' ' + line[foundIdx:]
        timesClosingBracket = line.count('}')
        foundIdx = 0
        for i in range(timesClosingBracket):
            foundIdx = line.find('}', foundIdx + 2)
            if line[foundIdx + 1] != ' ':
                line = line[:foundIdx + 1] + ' ' + line[foundIdx+1:]
        if annotatedAnEntity:
            sentences.add(line)
    return sentences

@plac.annotations(
    input_path=('Directory containing .txt files that need to be annotated using search words found in WordSetAndMappings.', 'option', 'i', str),
    output_path=('Directory where all the annotated files will be saved in the categories found in WordSetAndMappings.', 'option', 'o', str)
)
def main(input_path, output_path):
    """
    This script takes a directory containing .txt files as input. The text files contains lines of text that have entities
    in them. The script them processes the files and annotates them according the the categories in WordSetAndMappings.
    After that they are saving in the specified output_path.
    """
    global CATEGORIES
    if input_path is None:
        print('Please enter dir Path')
        raise SystemExit(1)
    if not os.path.exists(input_path):
        print('Please enter valid input path')
        raise SystemExit(1)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for file in os.listdir(input_path):
        with open(os.path.abspath(os.path.join(input_path, file)), mode='r', encoding='utf-8') as entSentFile:
            allLines = entSentFile.readlines()
        for category in CATEGORIES.keys():
            annotatedCategoryPath = os.path.join(output_path, category)
            annotatedFile = os.path.join(annotatedCategoryPath, file)
            if not os.path.exists(annotatedCategoryPath):
                os.makedirs(annotatedCategoryPath)
            annotatedSentences = annotateByCategory(allLines, category)

            with open(annotatedFile, encoding='utf-8', mode='a')as fw:
                fw.writelines(annotatedSentences)
            print("Annotated " + category + ' - ' + file)


if __name__ == '__main__':
    # plac.call(main)
    main(EXTRACTED_ENT_SENTS_PATH, TRUE_OUTPUT_PATH)
