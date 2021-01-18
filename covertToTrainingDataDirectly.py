import os
import random
import re
import pickle

ACTIVATION_CAT_PATH = r'C:\Users\Gjorgji Noveski\Desktop\nov spacy test\Annotated dataset\activation function model'
ARCHITECTURE_CAT_PATH = r'C:\Users\Gjorgji Noveski\Desktop\nov spacy test\Annotated dataset\architecture type model'
BULDING_CAT_PATH = r'C:\Users\Gjorgji Noveski\Desktop\nov spacy test\Annotated dataset\building blocks model'
DATASET_CAT_PATH = r'C:\Users\Gjorgji Noveski\Desktop\nov spacy test\Annotated dataset\dataset model'
OUTPUT_PATH = r'C:\Users\Gjorgji Noveski\Desktop\nov spacy test\Training testing bins'


## ("Uber blew through $1 million a week", [(0, 4, 'ORG')]),

# the first elements of startIdx and first elements of endIdx correspond to one one entity of the sentence,
# this continues to the end.
def convertLineToSpacyFormat(line, entity_name):
    startIdx = []
    endIdx = []
    points = []
    for counter, match in enumerate(re.finditer('(\{)', line)):
        idxEntStart = match.start() - (2 * counter)
        startIdx.append(idxEntStart)

    for counter, match in enumerate(re.finditer('(\})', line)):

        idxEntEnd = match.start() - (2 * counter) - 1
        endIdx.append(idxEntEnd)

    for start, end in zip(startIdx, endIdx):
        points.append((start, end, entity_name))
    # ova treba da go menjavash koga ke go trenirash deeplearning modelit i razlichno koga ke gi trenirash specialized ner models
    # deka specialized ner models datasetot e anotiram so {} a vo prviot e so []
    trainingFormatLine = (line.replace('{', '').replace('}', ''), {'entities': points})
    return trainingFormatLine


def main(input_dir, output_dir, train_test_split):
    if input_dir is None or output_dir is None:
        print('Please enter dir Path, and output dir Path')
        raise SystemExit(1)
    if not os.path.exists(input_dir):
        print('Please enter valid input path')
        raise SystemExit(1)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    allLines = []
    for file in os.listdir(input_dir):
        filePath = os.path.join(input_dir, file)
        with open(filePath, mode='r', encoding='utf-8')as f:
            allLines += f.readlines()

    if train_test_split is None:
        category = os.path.basename(input_dir)
        output_file = os.path.join(output_dir, category, 'training.bin')
        makeIntoBinary(allLines, output_file)

    else:
        split = int(len(allLines) * train_test_split)
        random.shuffle(allLines)
        train_data = allLines[:split]
        test_data = allLines[split:]
        category = os.path.basename(input_dir)
        output_file_train = os.path.join(output_dir, category, 'train_data.bin')
        output_file_test = os.path.join(output_dir, category, 'test_data.bin')
        makeIntoBinary(train_data, output_file_train, category)
        makeIntoBinary(test_data, output_file_test, category)


def makeIntoBinary(lines, output_file, entity_name):
    convertedLines = []
    for line in lines:
        spacyFormatLine = convertLineToSpacyFormat(line, entity_name)
        convertedLines.append(spacyFormatLine)

    with open(output_file, mode='wb')as f:
        pickle.dump(convertedLines, f)


if __name__ == '__main__':
    # main(ACTIVATION_CAT_PATH, OUTPUT_PATH, 0.8)
    # main(ARCHITECTURE_CAT_PATH, OUTPUT_PATH, 0.8)
    # main(BULDING_CAT_PATH, OUTPUT_PATH, 0.8)
    # main(DATASET_CAT_PATH, OUTPUT_PATH, 0.8)
