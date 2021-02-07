import os
import random
import re
import pickle
import plac


ACTIVATION_CAT_PATH = r'C:\Users\Gjorgji Noveski\Desktop\nov spacy test\Annotated dataset AMA SO PRAZNO MESTO\activation function model'

ARCHITECTURE_CAT_PATH = r'C:\Users\Gjorgji Noveski\Desktop\nov spacy test\Annotated dataset AMA SO PRAZNO MESTO\architecture type model'
OUTPUTPATH = r'C:\Users\Gjorgji Noveski\Desktop\test test'
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

@plac.annotations(
    input_dir=('Directory containing .txt files to be turned into binary files used in training/testing an NLP model.', 'option', 'i', str),
    output_dir=('Directory where the training/testing binaries will be located.', 'option', 'o', str),
    train_test_split=('Split ratio between the training and testing data, Ex. 0.7 = 70%% of data is for training, 30%% for testing.', 'option', 's', float))
def main(input_dir, output_dir, train_test_split):
    """
    This script takes a directory containing .txt files as input.
    The text files have to have sentences with entities which are annoteted using the '{ }' parentheses.
    It clears the parentheses and makes binary files which will be used for training an NLP model.
    """

    if input_dir is None:
        print('Please enter dir Path, and output dir Path')
        raise SystemExit(1)
    if not os.path.exists(input_dir):
        print('Please enter valid input path')
        raise SystemExit(1)
    
    TRAIN_OUTPUT_DIR = os.path.join(output_dir, 'training_bins')
    TEST_OUTPUT_DIR = os.path.join(output_dir, 'testing_bins')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(TRAIN_OUTPUT_DIR):
        os.makedirs(TRAIN_OUTPUT_DIR)
    if not os.path.exists(TEST_OUTPUT_DIR):
        os.makedirs(TEST_OUTPUT_DIR)


    allLines = []
    for file in os.listdir(input_dir):
        filePath = os.path.join(input_dir, file)
        with open(filePath, mode='r', encoding='utf-8')as f:
            allLines += f.readlines()

    if train_test_split is None:
        category = os.path.basename(input_dir)
        output_file = os.path.join(TRAIN_OUTPUT_DIR, category, 'training.bin')
        makeIntoBinary(allLines, output_file)

    else:
        split = int(len(allLines) * train_test_split)
        random.shuffle(allLines)
        train_data = allLines[:split]
        test_data = allLines[split:]
        category = os.path.basename(input_dir)
        output_file_train = os.path.join(TRAIN_OUTPUT_DIR, category + '_train_data.bin')
        output_file_test = os.path.join(TEST_OUTPUT_DIR, category + '_test_data.bin')
        makeIntoBinary(train_data, output_file_train, category)
        makeIntoBinary(test_data, output_file_test, category)


def makeIntoBinary(lines, output_file, entity_name):
    convertedLines = []
    for line in lines:
        spacyFormatLine = convertLineToSpacyFormat(line, entity_name)
        convertedLines.append(spacyFormatLine)
    if len(convertedLines) > 0:

        with open(output_file, mode='wb')as f:
            pickle.dump(convertedLines, f)
    else:
        print('emtpy')


if __name__ == '__main__':
    plac.call(main)
    # main(ARCHITECTURE_CAT_PATH, OUTPUTPATH, 0.0)
    # main(ACTIVATION_CAT_PATH, OUTPUTPATH, 0.0)

    # print(convertLineToSpacyFormat('An Effective Support Vector Machines( {SVMs} )','entitet'))
