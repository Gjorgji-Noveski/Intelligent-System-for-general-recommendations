import fitz
import re
import os
import spacy
import subprocess
from pathlib import Path
from Preprocessing import preprocessSinglePdfPage, makePaperID
from WordSetAndMappings import ACTIVATION_FUNC as ACT_FUNC_SEARCH_WORDS, ARCHITECTURE_TYPE as ARC_TYPE_SEARCH_WORDS, \
    BUILDING_BLOCKS as BUILD_BL_SEARCH_WORDS, ACTIVATION_FUNC_NO_ABBREVIATION as ACT_FUNC_KYW, ARCHITECTURE_TYPE_NO_ABBREVIATION as ARC_TYPE_KYW,\
    BUILDING_BLOCKS_NO_ABBREVIATION as BUILD_BLOCK_KYW, mappings

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

keyWordPath = r''
###
arcModelEnts = set()
actModelEnts = set()
buildBlockModelEnts = set()
# Format:
# id,
# paper Title,
# keywords vector,
# architecture type entities,
# activation function entities,
# building blocks entities
GENERAL_PAPER_VECTOR = {'ID': [], 'paper title': [], 'keywords vector': [], 'arcModelEntsVector': [],
                        'actModelEntsVector': [], 'buildBlockModelEntsVector': []}
paperIDcounter = 1
allPapersOutputPath = r'D:\Opshto Desktop\dispozable.txt'
testingOutput = open(allPapersOutputPath, mode='a', encoding='UTF-8')

###

# OVDE potrebna ni e kategorijata od sekoj fajl, zatoa mora for ciklusov, za da znaeme od koja kategorija pripagja
def makeVectorForPDF(pdf, all_keywords, catIdx, fileIdx,cat_name):
    global GENERAL_PAPER_VECTOR, paperIDcounter
    # Getting table of content titles
    # Mozhno podobruvanje, baraj go naslovot samo na stranata koja e navedeno
    # mnogu poedinechni sluchaevi ima shto nekoi tekst da se chisti/sredi
    pdfToc = pdf.getToC()
    # getting all the ToC titles, except the word References, because it is needed for finding the end of a research paper
    tocTitlesNoReferences = [element[1].strip() for element in pdfToc if element[1].strip() != 'References']
    GENERAL_PAPER_VECTOR['keywords vector'] = dict.fromkeys(all_keywords, 0)
    paperIDcounter = 1
    allKeywords = []
    for pageNm, page in enumerate(pdf, 1):

        pageTextInLines = preprocessSinglePdfPage(page, tocTitlesNoReferences)
        tryGetPageKeywords(pageNm, pageTextInLines, pdf, pdfToc)

        keywords, paperTitle = pageKeywordsTESTbyGETTEXTBLOCKS(page, pageNm, pdf, pdfToc)
        # specializedNERvectors mora da bide posle tryGetPageKeywords, deka tamu setiram globalnata foundAbstract
        # otkako ke se najde References, taa funckija ima raboti da go vrati generalniot vektor kako shto beshe originalno
        # tryMakeEntityVector(pageTextInLines, pageNm, catIdx, fileIdx)

        # check if the whole vector is full

        # if GENERAL_PAPER_VECTOR['ID']:
        #     # print('PAPER TITLE ->', GENERAL_PAPER_VECTOR['paper title'])
        #     # print('PAPER ID ->', GENERAL_PAPER_VECTOR['ID'])
        #     # print(GENERAL_PAPER_VECTOR)
        #     testingOutput.write(cat_name+'\n')
        #     for key, value in GENERAL_PAPER_VECTOR.items():
        #         testingOutput.write(key+'\n')
        #         testingOutput.write(str(value)+'\n\n')
        #     testingOutput.write('-' * 80 + 'END OF PAPER' + '-' * 80 +'\n\n\n')
        #     testingOutput.flush()
        #     reInitializeVector(all_keywords)
        allKeywords += keywords
    # gi vrakjam site keywords so mali bukvi, trgnati prazni mesta na pochetokot i na krajot

    return allKeywords


"""
1.gleda dali pishuva "Abstract" na stranata (na pochetok na rechenica)
2. ako ima gleda dali pishuva "Keywords" ili "Key words" na stranata ( na pochetok na rechenica)
3. ako ima gleda dali ima zborchinja posle Zborot Keywords/key words, dali toa bilo vo ist red so zborot Keywords/key words ili posle vo naredniot red
4 ako ima gi zema niv se dodeka ne dojde do linija kade shto pishuva 1 Introduction, deka ako ja vidime taa znachi deka sme gi zele site zborchinja koi oznachuvaat keywords.
5 Note: zema po 2 linii keywords, deka ako zeme povishe, ima shansa da nema 1 Introduction i da zeme tekst shto ne e keywords.
"""


def tryGetPageKeywords(pageNm, pageTextInLines, pdf, pdfToc):
    global foundAbstract, foundBeginning, GENERAL_PAPER_VECTOR
    # if the word "abstract" is found at the beggiing of the line we can be more sure that it's the first page of the scientific research paper
    foundAbstract = False
    foundKeyWordLines = []
    paperTitle = 'Not found'
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
                # ova kazhuva za drugata funckija, za modelite od spacy deka e vo trudot
                foundBeginning = True
                paperTitle = extractTitle(pdf, pageNm)
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
    if len(foundKeyWordLines) != 0:
        joinedKeywords = ' '.join(foundKeyWordLines)
        # koristi ovoj regex se dodeka ne nauchish kako da gi odbirash site interpunkciski znaci od posebni unicode blokovi, deka mojata tastatura nema apostrov kako shto ima angliskata primer
        keywords = re.split(r'[^a-zA-Z0-9\-\.\(\)’\–\- ]', joinedKeywords)
        keywords = [keyword.strip().lower().rstrip('.') for keyword in keywords]
        for keyword in keywords:
            if keyword in GENERAL_PAPER_VECTOR['keywords vector']:
                GENERAL_PAPER_VECTOR['keywords vector'][keyword] = 1
            else:
                print('Keyword not found in set of keywords: %s' % keyword)
        if paperTitle == '':
            # if PDFTITLE fails to find title, we try with the ToC
            for element in pdfToc:
                if element[2] == pageNm:
                    paperTitle = element[1]
                    break

        GENERAL_PAPER_VECTOR['paper title'] = paperTitle


def extractTitle(pdf, titlePageNm):
    titlePageNm -= 1
    tmp = fitz.open()
    tmp.insertPDF(pdf, from_page=titlePageNm, to_page=titlePageNm)  # make a 1-page PDF of it
    tmp.save("Temp/paperTitle.pdf")
    completed_process = subprocess.run(['pdftitle', '-p', 'Temp/paperTitle.pdf'], capture_output=True, text=True,
                                       encoding='UTF-8')
    return completed_process.stdout.strip()

def pageKeywordsTESTbyGETTEXTBLOCKS(page, pageNm, pdf, pdfToc):
    global foundAbstract, foundBeginning
    blocks = page.getText('blocks')
    textBlocks = [block[4].replace('-\n', '').replace('\xa0', ' ').replace('\n', ' ') for block in blocks]
    foundAbstract = False
    keywords = ''
    paperTitle = 'Not found'
    for paragraph in textBlocks:
        if paragraph[:8].lower() == 'abstract':
            foundAbstract = True
            break
    if foundAbstract:
        for paragraph in textBlocks:
            if paragraph[:8] == 'Keywords' or paragraph[:9] == 'Key words':
                foundBeginning = True
                paperTitle = extractTitle(pdf, pageNm)
                keywords += paragraph[9:]
    if keywords != '':
        keywords = re.split(r'[^a-zA-Z0-9\-\.\(\)’\–\- ]', keywords)
        keywords = [re.sub(r'\s{2,}', ' ', keyword.strip().lower().rstrip('.')) for keyword in keywords if not keyword.strip().rstrip('.').isspace() and keyword.strip().rstrip('.') != '']
        for keyword in keywords:
            if keyword in GENERAL_PAPER_VECTOR['keywords vector']:
                GENERAL_PAPER_VECTOR['keywords vector'][keyword] = 1
            else:
                print('Keyword not found in set of keywords: %s' % keyword)
    else:
        keywords = []
    if paperTitle == '':
        # if PDFTITLE fails to find title, we try with the ToC
        for element in pdfToc:
            if element[2] == pageNm:
                paperTitle = element[1]
                break

    GENERAL_PAPER_VECTOR['paper title'] = paperTitle
    return keywords, paperTitle



def updateCategoryVectors(arcModelEnts, actModelEnts, buildBlockModelEnts):
    global GENERAL_PAPER_VECTOR
    arcModelVec = getVectorFromCategory(arcModelEnts, ARC_TYPE_SEARCH_WORDS, ARC_TYPE_KYW)
    actModelVec = getVectorFromCategory(actModelEnts, ACT_FUNC_SEARCH_WORDS, ACT_FUNC_KYW)
    buildBlockModelVec = getVectorFromCategory(buildBlockModelEnts, BUILD_BL_SEARCH_WORDS, BUILD_BLOCK_KYW)
    GENERAL_PAPER_VECTOR['arcModelEntsVector'] = arcModelVec
    GENERAL_PAPER_VECTOR['actModelEntsVector'] = actModelVec
    GENERAL_PAPER_VECTOR['buildBlockModelEntsVector'] = buildBlockModelVec


def reInitializeVector(all_keywords):
    global GENERAL_PAPER_VECTOR
    GENERAL_PAPER_VECTOR = {'ID': [], 'paper title': [], 'keywords vector': [], 'arcModelEntsVector': [],
                            'actModelEntsVector': [], 'buildBlockModelEntsVector': []}
    GENERAL_PAPER_VECTOR['keywords vector'] = dict.fromkeys(all_keywords, 0)


def tryMakeEntityVector(pageTextInLines, pageNm, catIdx, fileIdx):
    global foundBeginning, paperText, insidePaper, actModelEnts, arcModelEnts, buildBlockModelEnts, GENERAL_PAPER_VECTOR, paperIDcounter

    if foundBeginning:
        if paperText != '':
            print('NEFINISHIRAN TEKST')

            arcModelEnts = [ent.text for ent in nlp_arc(paperText).ents]
            actModelEnts = [ent.text for ent in nlp_act(paperText).ents]
            buildBlockModelEnts = [ent.text for ent in nlp_build(paperText).ents]

            updateCategoryVectors(arcModelEnts, actModelEnts, buildBlockModelEnts)
            GENERAL_PAPER_VECTOR['ID'] = makePaperID(catIdx, fileIdx, paperIDcounter)
            paperIDcounter = paperIDcounter + 1
            paperText = ''

        foundBeginning = False
        insidePaper = True
        paperText = ''.join(pageTextInLines) + ' '
    elif insidePaper:
        for line in pageTextInLines:
            if line[0:10] == 'References':
                arcModelEnts = [ent.text for ent in nlp_arc(paperText).ents]
                actModelEnts = [ent.text for ent in nlp_act(paperText).ents]
                buildBlockModelEnts = [ent.text for ent in nlp_build(paperText).ents]

                updateCategoryVectors(arcModelEnts, actModelEnts, buildBlockModelEnts)
                GENERAL_PAPER_VECTOR['ID'] = makePaperID(catIdx, fileIdx, paperIDcounter)
                paperIDcounter += 1
                insidePaper = False
                paperText = ''
                return

        else:
            paperText += ' '.join(pageTextInLines) + ' '


def addAllEnts(extractedArcEnts, extractedActEnts, extractedBuildBlockEnts):
    global arcModelEnts, actModelEnts, buildBlockModelEnts
    for ent in extractedArcEnts:
        arcModelEnts.add(ent)
    for ent in extractedActEnts:
        actModelEnts.add(ent)
    for ent in extractedBuildBlockEnts:
        buildBlockModelEnts.add(ent)


# mu davas entiteti, i mu davash od koja kategorija zborovite da gi bara
# primer cat = architecture type, i gi bara samo vo niv, za da vrati vektor od zborovi samo za taa kategorija posle ke gi appendirash site za da go dobiesh krajniot dolg vektor
def getVectorFromCategory(ents, category_search_words, category_kyw):
    category_kyw_values = dict.fromkeys(category_kyw, 0)
    # checking if the entity is plural, then slicing it so we take it as singular and search that in the features
    for ent in ents:
        ent = ent.strip().lower()
        if ent[-1] == 's':
            ent = ent[:-1]
        if ent in category_search_words:
            if ent in mappings:
                feature = mappings[ent]
            else:
                feature = ent
            category_kyw_values[feature] = 1
    return category_kyw_values


"""

Vo ovaa skripta gi sobiram site keywords shto mozham da gi najdam vo kategeroijata vo sekoj pdf i vo sekoj trud vo pdf-to

"""


def processCategory(cat_path, all_keywords, catIdx, keyWordPath=None):
    global fileNames, pdfPathNames
    keyWords = set()
    for fileIdx, file in enumerate(os.listdir(cat_path), 1):
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
        # pdf = fitz.open(r'C:\Users\Gjorgji Noveski\PycharmProjects\SciBooksCrawler\SciBooks\Downloaded PDFs\bioinformatics\ApplicationofClinicalBioinformatics.pdf')
        print(file)
        keyWordsFromPdf = makeVectorForPDF(pdf, all_keywords, catIdx, fileIdx, os.path.basename(cat_path))
        if keyWordPath:
            for keyWord in keyWordsFromPdf:
                keyWords.add(keyWord)
            with open(keyWordPath, mode='a', encoding='UTF-8')as f:
                f.write(','.join(keyWords))


# ovde smeniv namesto da pushta kategorija po kategorija da procesira fajlovite, site vektori od SITE KATEGORII DA GI SPOI I da gi prati
def processEveryCategory(cats_path, keyWordDirPath=None):
    allKeywords = []
    for cat in os.listdir(cats_path):
        with open('C:\\Users\\Gjorgji Noveski\\Desktop\\nov spacy test\\Keyword Vectors\\%s.txt' % cat, mode='r',
                  encoding='UTF-8')as kw:
            words = kw.read().split(',')
            allKeywords += words

    for catIdx, cat in enumerate(os.listdir(cats_path), 1):
        cat_path = os.path.join(cats_path, cat)
        if keyWordDirPath:
            categoryName = os.path.basename(cat_path)
            keyWordFilePath = os.path.join(keyWordDirPath, '%s.txt' % categoryName)
            processCategory(cat_path, allKeywords, catIdx, keyWordFilePath)
        else:
            processCategory(cat_path, allKeywords, catIdx)

    testingOutput.close()


# processCategory(r'C:\Users\Gjorgji Noveski\PycharmProjects\SciBooksCrawler\SciBooks\Downloaded PDFs')
processEveryCategory(r'C:\Users\Gjorgji Noveski\PycharmProjects\SciBooksCrawler\SciBooks\Downloaded PDFs')
