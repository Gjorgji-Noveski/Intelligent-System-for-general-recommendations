import fitz
import re
import os
import spacy
from pathlib import Path
from Preprocessing import preprocessSinglePdfPage
fileNames = []
pdfPathNames = {}
paperText = ''
foundAbstract = False
foundBeginning = False
insidePaper = False
act_model = r'C:\Users\Gjorgji Noveski\Desktop\nov spacy test\specialized models\activation function model\98 epochs'
arc_model = r'C:\Users\Gjorgji Noveski\Desktop\nov spacy test\specialized models\architecture type model\77 epochs'
building_blocks_model = r'C:\Users\Gjorgji Noveski\Desktop\nov spacy test\specialized models\building blocks model\87 epochs'
nlp_act = spacy.load(act_model)
nlp_arc = spacy.load(arc_model)
nlp_build = spacy.load(building_blocks_model)

# OVDE potrebna ni e kategorijata od sekoj fajl, zatoa mora for ciklusov, za da znaeme od koja kategorija pripagja
def makeVectorForPDF(pdf, all_keywords):
    # Getting table of content titles
    # Mozhno podobruvanje, baraj go naslovot samo na stranata koja e navedeno
    # mnogu poedinechni sluchaevi ima shto nekoi tekst da se chisti/sredi
    pdfToc = pdf.getToC()
    # getting all the ToC titles, except the word References, because it is needed for finding the end of a research paper
    tocTitlesNoReferences = [element[1].strip() for element in pdfToc if element[1].strip() != 'References']
    wholePdfText = ''
    keyWords = []
    for pageNm, page in enumerate(pdf, 1):
        pageTextInLines = preprocessSinglePdfPage(page, tocTitlesNoReferences)
        wholePdfText += ' '.join(pageTextInLines) + ' '
        pageKeywords = getPageKeywords(pageNm, pageTextInLines, pdfToc)
        # specializedNERvectors mora da bide posle getPageKeywords, deka tamu setiram globalnata foundAbstract
        specialzedNERVectors = getSpecializedNERVector(pageTextInLines,pageNm)


        if len(pageKeywords) != 0:
            all_keywords = dict.fromkeys(all_keywords, 0)
            # print(pageKeywords)
            for keyword in pageKeywords:
                if keyword in all_keywords:
                    all_keywords[keyword] = 1
            # print('Paper vector of keywords %s->' % all_keywords)
        keyWords += pageKeywords
    # gi vrakjam site keywords so mali bukvi, trgnati prazni mesta na pochetokot i na krajot
    return [keyword.strip().lower() for keyword in keyWords if keyword.strip() != '']


"""
1.gleda dali pishuva "Abstract" na stranata (na pochetok na rechenica)
2. ako ima gleda dali pishuva "Keywords" ili "Key words" na stranata ( na pochetok na rechenica)
3. ako ima gleda dali ima zborchinja posle Zborot Keywords/key words, dali toa bilo vo ist red so zborot Keywords/key words ili posle vo naredniot red
4 ako ima gi zema niv se dodeka ne dojde do linija kade shto pishuva 1 Introduction, deka ako ja vidime taa znachi deka sme gi zele site zborchinja koi oznachuvaat keywords.
5 Note: zema po 2 linii keywords, deka ako zeme povishe, ima shansa da nema 1 Introduction i da zeme tekst shto ne e keywords.
"""
def getPageKeywords(pageNm, pageTextInLines, pdfToc):
    global foundAbstract, foundBeginning
    # if the word "abstract" is found at the beggiing of the line we can be more sure that it's the first page of the scientific research paper
    foundAbstract = False
    foundKeyWordLines = []
    paperTitle = 'None'
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
                #ova kazhuva za drugata funckija, za modelite od spacy deka e vo trudot
                foundBeginning = True
                #ovde barame naslovot na trudot, bara vo table of contents ako ima ist broj na strana kade shto se momentalno najdeni keywords go zema prviot
                for element in pdfToc:
                    if element[2] == pageNm:
                        paperTitle = element[1]
                        break
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
                if idx < len(pageTextInLines):

                    if (len(pageTextInLines[idx]) > 0 and pageTextInLines[idx].strip()[0] == '1') or 'Introduction' in \
                            pageTextInLines[idx].strip():
                        break
                    else:
                        foundKeyWordLines.append(pageTextInLines[idx])
    keywords = []
    if paperTitle !='None':
        print(paperTitle)
    if len(foundKeyWordLines) != 0:
        joinedKeywords = ' '.join(foundKeyWordLines)
        # koristi ovoj regex se dodeka ne nauchish kako da gi odbirash site interpunkciski znaci od posebni unicode blokovi, deka mojata tastatura nema apostrov kako shto ima angliskata primer
        keywords = re.split(r'[^a-zA-Z0-9\-\.\(\)’\–\- ]', joinedKeywords)
        return [keyword.strip().lower() for keyword in keywords]
    return [keyword.strip().lower() for keyword in keywords]

# samo za debagiranje mi e pageNm
def getSpecializedNERVector(pageTextInLines, pageNm):
    global foundBeginning, paperText, insidePaper

    if foundBeginning:
        print('found new beginning' + str(pageNm))
        # stavi inside flag = 1 za da mozhesh da vidish ako PAK najdesh abstract a ne se se otarasil preku references
        if paperText != '':
            print('NEFINISHIRAN TEKST')
            print('najdeni NEFINISHIRANI entiteti: ')
            print('nefinishiran tekst:' + paperText)
            arcModelEnts = [ent.text for ent in nlp_arc(paperText).ents]
            print(arcModelEnts)
            print(''.join(arcModelEnts))
        foundBeginning = False
        insidePaper = True
        paperText = ''.join(pageTextInLines) + ' '
    elif insidePaper:
        print('inside paper' + str(pageNm))
        for line in pageTextInLines:
            if line[0:10] == 'References':
                print('najdeni entiteti: ')
                arcModelEnts = [ent.text for ent in nlp_arc(paperText).ents]
                print(''.join(arcModelEnts))
                insidePaper = False
                print('exiting paper')
                paperText = ''
                break
        else:
            paperText += ' '.join(pageTextInLines) + ' '

"""

Vo ovaa skripta gi sobiram site keywords shto mozham da gi najdam vo kategeroijata vo sekoj pdf i vo sekoj trud vo pdf-to

"""
def processCategory(cat_path,all_keywords):
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
        keyWordsFromPdf = makeVectorForPDF(pdf, all_keywords)
        for keyWord in keyWordsFromPdf:
            keyWords.add(keyWord)
    categoryName = os.path.basename(cat_path)
    # with open(r'C:\Users\Gjorgji Noveski\Desktop\nov spacy test\Keyword Vectors\%s.txt' % categoryName, mode='w', encoding='UTF-8')as f:
    #     f.write(','.join(keyWords))

def processEveryCategory(cats_path):
    for cat in os.listdir(cats_path):
        with open('C:\\Users\\Gjorgji Noveski\\Desktop\\nov spacy test\\Keyword Vectors\\%s.txt' % cat, mode='r', encoding='UTF-8')as kw:
            allKeywords = kw.read().split(',')
        cat_path = os.path.join(cats_path, cat)
        processCategory(cat_path, allKeywords)



# processCategory(r'C:\Users\Gjorgji Noveski\PycharmProjects\SciBooksCrawler\SciBooks\Downloaded PDFs')
processEveryCategory(r'C:\Users\Gjorgji Noveski\PycharmProjects\SciBooksCrawler\SciBooks\Downloaded PDFs')

