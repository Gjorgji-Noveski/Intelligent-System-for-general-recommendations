import fitz
import re
import os
from pathlib import Path

fileNames = []
pdfPathNames = {}


# OVDE potrebna ni e kategorijata od sekoj fajl, zatoa mora for ciklusov, za da znaeme od koja kategorija pripagja
def makeVectorForPDF(pdf):
    # Getting table of content titles
    # Mozhno podobruvanje, baraj go naslovot samo na stranata koja e navedeno
    # mnogu poedinechni sluchaevi ima shto nekoi tekst da se chisti/sredi

    tocTitles = [element[1] for element in pdf.getToC()]
    wholePdfText = ''
    keyWords = []
    for page in pdf:

        """
        Filters any line from a page that starts with "Fig." or "Table " because usually those word indicate annotation for a figure/table.
        Also filters empty or lines filled with whitespace.
        """

        pageText = re.sub("-\n", "", page.getText().replace('\xa0', ' '))
        pageTextInLines = pageText.split("\n")
        pageTextInLines = [line.strip() for line in pageTextInLines if
                           not line.isspace() and line != '' and line[:4] != 'Fig.' and line[:6] != 'Table ']

        # checking if the first 2 sentences contain the "et al." part so it can be removed
        if len(pageTextInLines) > 1:
            if 'et al' in pageTextInLines[0]:
                pageTextInLines.remove(pageTextInLines[0])
            elif 'et al' in pageTextInLines[1]:
                pageTextInLines.remove(pageTextInLines[1])

        """
        Deletes the first 2 sentences of a page if they contain the title of that chapter that is found in Table of Contents
        and also if one of the sentences is numeric (a.k.a, page number)
        """
        for tocTitle in tocTitles:
            if len(pageTextInLines) > 2:
                tocTitle = tocTitle.strip()
                if tocTitle in pageTextInLines[0]:
                    pageTextInLines.remove(pageTextInLines[0])

                elif tocTitle in pageTextInLines[1]:
                    pageTextInLines.remove(pageTextInLines[1])

                if pageTextInLines[0].isnumeric():
                    pageTextInLines.remove(pageTextInLines[0])

                elif pageTextInLines[1].isnumeric():
                    pageTextInLines.remove(pageTextInLines[1])

        wholePdfText += ' '.join(pageTextInLines) + ' '
        keyWords += getPaperKeywords(pageTextInLines)
    # gi vrakjam site keywords so mali bukvi, trgnati prazni mesta na pochetokot i na krajot
    return [keyword.strip().lower() for keyword in keyWords if keyword.strip() != '']


"""
1.gleda dali pishuva "Abstract" na stranata (na pochetok na rechenica)
2. ako ima gleda dali pishuva "Keywords" ili "Key words" na stranata ( na pochetok na rechenica)
3. ako ima gleda dali ima zborchinja posle Zborot Keywords/key words, dali toa bilo vo ist red so zborot Keywords/key words ili posle vo naredniot red
4 ako ima gi zema niv se dodeka ne dojde do linija kade shto pishuva 1 Introduction, deka ako ja vidima taa znachi deka sme gi zele site zborchinja koi oznachuvaat keywords.
5 Note: zema po 2 linii keywords, deka ako zeme povishe, ima shansa da nema 1 Introduction i da zeme tekst shto ne e keywords.
"""
def getPaperKeywords(pageTextInLines):
    # if the word "abstract" is found at the beggiing of the line we can be more sure that it's the first page of the scientific research paper
    foundAbstract = False
    foundKeyWordLines = []

    for line in pageTextInLines:
        if line[:8].lower() == 'abstract':
            foundAbstract = True
            break
    if foundAbstract:
        # proveruva od koj red pochnuva Zborot Keywords/Key words za mozhe posle da pochne od tamu da gi zema se dodeka ne sretne string '1'
        # deka obichno posle keywords postojat rechenicite 1 Introduction, pa zatoa.
        idxNumForKeyW = -1
        for idx, line in enumerate(pageTextInLines):
            if line[:8] == 'Keywords' or line[:9] == 'Key words':
                # ova gi zema zborovite shto se posle Keywords zborot, i processNlines mu vika da j procesira samo narednata linija, deka vishe prvata posle Keywords zborot ima drugi zborovi i vishe gi apendnavme
                if len(line[9:]) > 3:
                    foundKeyWordLines.append(line[9:])
                    idxNumForKeyW = idx + 1
                    processNlines = 1
                    break
                # ova gi zema zborovite shto se posle Keywords zborot ako se pod nego, processNlines mu kazhuva da gi procesira narednite 2 linii, bidejki prvata Keywords e prazna, to est samo so toa Keywords zborot
                else:
                    idxNumForKeyW = idx + 1
                    processNlines = 2
                    break
        # ako sme nashle redicata kade pishuva Keywords
        if idxNumForKeyW != -1:
            # odime se dodeka ne pomineme 2 linii ili stigneme do 1 Introduction, Ova e tuka za sluchajna ako imame 1 Introduction linija da ja fati i da prestane, za da ne zememe neshto shto ne e keyword
            for idx in range(idxNumForKeyW, idxNumForKeyW + processNlines):

                if (len(pageTextInLines[idx]) > 0 and pageTextInLines[idx].strip()[0] == '1') or 'Introduction' in \
                        pageTextInLines[idx].strip():
                    break
                else:
                    foundKeyWordLines.append(pageTextInLines[idx])
    if len(foundKeyWordLines) != 0:
        joinedKeywords = ' '.join(foundKeyWordLines)
        # koristi ovoj regex se dodeka ne nauchish kako da gi odbirash site interpunkciski znaci od posebni unicode blokovi, deka mojata tastatura nema apostrov kako shto ima angliskata primer
        keyWords = re.split(r'[^a-zA-Z0-9\-\.\(\)’\–\- ]', joinedKeywords)
        return keyWords
    return foundKeyWordLines

"""

Vo ovaa skripta gi sobiram site keywords shto mozham da gi najdam vo kategeroijata vo sekoj pdf i vo sekoj trud vo pdf-to

"""
def processCategory(cat_path):
    global fileNames, pdfPathNames
    keyWords = set()
    for countFile, file in enumerate(os.listdir(cat_path), 1):
        if file[-4:] != '.pdf':
            continue
        # Checks if file is already processed by file name file size (sometimes 2 different pdfs have same name)
        PDF_PATH = os.path.join(cat_path, file)
        if file not in fileNames:
            fileNames.append(file)
            pdfPathNames[file] = PDF_PATH
        elif Path(pdfPathNames[file]).stat().st_size == Path(PDF_PATH).stat().st_size:
            print('Info: Found duplicate file, skipping processing it')
            continue

        pdf = fitz.open(PDF_PATH)
        # pdf = fitz.open(r'C:\Users\Gjorgji Noveski\PycharmProjects\SciBooksCrawler\SciBooks\Downloaded PDFs\chemoinformatics\Chemoinformaticsandcomputationalchemicalbiology.pdf')
        print(file)
        keyWordsFromPdf = makeVectorForPDF(pdf)
        for keyWord in keyWordsFromPdf:
            if keyWord in keyWords:
                print('Duplikat -> %s' %keyWord)
            keyWords.add(keyWord)
    print(keyWords)
    print(len(keyWords))


processCategory(r'C:\Users\Gjorgji Noveski\PycharmProjects\SciBooksCrawler\SciBooks\Downloaded PDFs\biostatistics')