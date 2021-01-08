import re
import plac
import os
from pathlib import Path

DELIMITER = '\t'
FILE_EXTENSION = '.tsv'


@plac.annotations(
    inputFileOrDir=(
    "The input text file or dir where category dirs are, to be converted into a BIO scheme", "option", "i", Path),
    outputDir=("Output path dir.", "option", "o", Path))
def main(inputFileOrDir=None, outputDir=None):
    global DELIMITER, FILE_EXTENSION
    if inputFileOrDir is None or outputDir is None:
        print('Please enter txt-file/dir Path, and outputDir Path')
        raise SystemExit(1)
    if not os.path.exists(inputFileOrDir):
        print('Please enter valid input path')
        raise SystemExit(1)
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)

    if os.path.isdir(inputFileOrDir):
        for cat in os.listdir(inputFileOrDir):
            allLine = []
            entCat = os.path.join(inputFileOrDir, cat)
            for sentFile in os.listdir(entCat):
                allLine += getLines(os.path.join(entCat, sentFile))
            outputCatDir = os.path.join(outputDir, cat)
            if not os.path.exists(outputCatDir):
                os.makedirs(outputCatDir)
            outputFile = os.path.join(outputCatDir, cat + FILE_EXTENSION)
            entityName = cat.replace('model', '').replace(' ', '_')
            convert(allLine, outputFile, entityName)
            print('Converted %s annotated dataset to %s' % (cat, FILE_EXTENSION))
    else:
        outputFile = os.path.join(outputDir, os.path.basename(inputFileOrDir)[:-4] + FILE_EXTENSION)
        convert(inputFileOrDir, outputFile)
        print('Converted %s to %s' % (os.path.basename(inputFileOrDir), os.path.basename(outputFile)))


def getLines(inputFile):
    with open(inputFile, mode='r', encoding='utf-8')as f:
        lines = f.readlines()
    return lines


def convert(inputFileOrDir, outputDir, entityName):
    global DELIMITER
    if not type(inputFileOrDir) is list:
        with open(inputFileOrDir, mode='r', encoding='UTF-8') as sentFile:
            lines = sentFile.readlines()
    else:
        lines = inputFileOrDir
    with open(outputDir, mode='w', encoding='UTF-8') as taggedCorpus:
        for line in lines:
            # za da ne dobijam prazni rechenici vo krajniot json, zatoa brisham prazno_mestoTOCKAprazno_Mesto

            words = re.sub(r'\W\.\W', '', line).replace('\t', ' ').split(' ')
            foundStartBracket = False
            if words[-1] == '':
                words = words[:-1]
            for idx, word in enumerate(words, 1):
                hasComma = False

                # checking to see if the word has a coma
                if word.isspace() or word == '':
                    continue
                if word[-1] == ',':
                    hasComma = True
                # ako koristam \W za se shto ne e zbor, ke mi se trgnat i bitnite raboti kako , . [] {}. Ne znam kako da napravam regex iskluchok za niv
                word = re.sub(r'[,();`“”]', '', word)

                if idx == len(words):
                    word = re.sub(r'[\.\n]', '', word)

                if len(word) == 0:
                    continue

                # References in text are in '[ ]' brackets, our entities will be in '{ }' brackets
                if word[0] == '[':
                    taggedCorpus.write('[' + DELIMITER + 'O\n')
                    word = re.sub(r'[\[]', '', word)

                if len(word) == 0:
                    continue

                # Nekogas mozhe i vakvo da primi: {perceptron}-based, ke gi trgne zagradite i posle dvata zbora ke bidat kako eden entitet.
                # Ako e samo eden zbor vo entitetot
                if word.find('{') != -1 and word.find('}') != -1:
                    cleanWord = re.sub(r'[{}]', '', word)
                    taggedCorpus.write(cleanWord + DELIMITER + 'B-%s\n' % entityName)

                # ako e pochetniot zbor vo entitetot
                elif word.find('{') != -1:
                    cleanWord = re.sub(r'[{]', '', word)
                    taggedCorpus.write(cleanWord + DELIMITER + 'B-%s\n' % entityName)
                    foundStartBracket = True

                # ako e krajniot zbor vo entitetot
                elif word.find('}') != -1:
                    cleanWord = re.sub(r'[}]', '', word)
                    taggedCorpus.write(cleanWord + DELIMITER + 'I-%s\n' % entityName)
                    foundStartBracket = False

                # ako e vnatreshen zbor vo entitetot
                elif foundStartBracket:
                    taggedCorpus.write(word + DELIMITER + 'I-%s\n' % entityName)
                #
                elif word[-1] == ']':
                    word = re.sub(r'[\]]', '', word)
                    taggedCorpus.write(word + DELIMITER + 'O\n')
                    taggedCorpus.write(']' + DELIMITER + 'O\n')
                else:
                    taggedCorpus.write(word + DELIMITER + 'O\n')
                if hasComma:
                    taggedCorpus.write(',' + DELIMITER + 'O\n')
            taggedCorpus.write('.' + DELIMITER + 'O\n')


if __name__ == '__main__':
    # plac.call(main)
    main(r'C:\Users\Gjorgji Noveski\Desktop\Files for my Spacy work\Annotated dataset for different NER models', r'C:\Users\Gjorgji Noveski\Desktop\test')
