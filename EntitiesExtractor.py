import re
entities = set()
taggedCorpus = open("C:\\Users\\Gjorgji Noveski\\Desktop\\taggedCorpus.txt", mode='a', encoding='UTF-8')
with open("C:\\Users\\Gjorgji Noveski\\Desktop\\AllSents.txt", mode='r', encoding='UTF-8') as sentFile:
    lines = sentFile.readlines()
    for line in lines:
        words = line.split(" ")

        openingBracketIter = re.finditer("\[", line)
        closingBracketIter = re.finditer("\]", line)

        for m1,m2 in zip(openingBracketIter,closingBracketIter):
            entities.add(str(line[m1.end():m2.start()]).lower())
    writeFile = open("./Entities.txt",mode='w')
    for entity in entities:
        writeFile.write(entity+"\n")
    writeFile.close()