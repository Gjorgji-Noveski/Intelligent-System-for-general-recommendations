writeFile = open("C:/Users/Gjorgji Noveski/Desktop/Files for my Spacy work/Files for evaluating a model/new sentences, after sentence 850+.tsv", encoding='utf-8', mode='w')

with open("C:/Users/Gjorgji Noveski/Desktop/Files for my Spacy work/Files for evaluating a model/new sentences, after sentence 850+.csv", mode='r', encoding='UTF-8') as f:
    allLines = f.readlines()
    for line in allLines:
        if line[0] == ',':
            writeFile.write(',\tO\n')
        else:
            words = line.split(",")
            writeFile.write(words[0] + "\t" + words[1])

writeFile.close()