import re

entities = set()
taggedCorpus = open("C:/Users/Gjorgji Noveski/Desktop/Files for my Spacy work/Files for evaluating a model/new sentences, after sentence 850+.csv", mode='w', encoding='UTF-8')
with open("C:/Users/Gjorgji Noveski/Desktop/Files for my Spacy work/Files for evaluating a model/new sentences, after sentence 850+.txt",
          mode='r', encoding='UTF-8') as sentFile:
    lines = sentFile.readlines()
for line in lines:
    words = line.split(" ")
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
        word = re.sub("[,();`“”]", "", word)

        if idx == len(words):
            word = re.sub("[.\n]", "", word)
        if len(word) == 0:
            continue

        # checking to see if the word is a reference to another research, {} brackets are used in AllSents.txt
        # instead of []
        if word[0] == '{':
            taggedCorpus.write("[,O\n")
            word = re.sub("[{]", "", word)

        # Ako e samo eden zbor vo entitetot
        if word.find("[") != -1 and word.find("]") != -1:
            cleanWord = re.sub("[\[\]]", "", word)
            taggedCorpus.write(cleanWord + ",B-DeepLearning\n")

        # ako e pochetniot zbor vo entitetot
        elif word.find("[") != -1:
            cleanWord = re.sub("[\[\]]", "", word)
            taggedCorpus.write(cleanWord + "," + "B-DeepLearning\n")
            foundStartBracket = True

        # ako e krajniot zbor vo entitetot
        elif word.find("]") != -1:
            cleanWord = re.sub("[\[\]]", "", word)
            taggedCorpus.write(cleanWord + "," + "I-DeepLearning\n")
            foundStartBracket = False

        # ako e vnatreshen zbor vo entitetot
        elif foundStartBracket:
            taggedCorpus.write(word + "," + "I-DeepLearning\n")
        #
        elif word[-1] == '}':
            word = re.sub("[}]", "", word)
            taggedCorpus.write(word + "," + "O\n")
            taggedCorpus.write("],O\n")
        else:
            taggedCorpus.write(word + "," + "O\n")
        if hasComma:
            taggedCorpus.write(',' + ',' + "O\n")
    taggedCorpus.write(".,O\n")
taggedCorpus.close()
