import fitz
import re
import os
import spacy
import subprocess
import plac
from pathlib import Path
from Preprocessing import preprocessSinglePdfPage, makePaperID
from WordSetAndMappings import ACTIVATION_FUNC as ACT_FUNC_SEARCH_WORDS, ARCHITECTURE_TYPE as ARC_TYPE_SEARCH_WORDS, \
    BUILDING_BLOCKS as BUILD_BL_SEARCH_WORDS, ACTIVATION_FUNC_NO_ABBREVIATION as ACT_FUNC_KYW, \
    ARCHITECTURE_TYPE_NO_ABBREVIATION as ARC_TYPE_KYW, \
    BUILDING_BLOCKS_NO_ABBREVIATION as BUILD_BLOCK_KYW, mappings

fileNames = []
pdfPathNames = {}
paperText = ''
foundBeginning = False
insidePaper = False
nlp_act = None
nlp_arc = None
nlp_build = None
arcModelEnts = set()
actModelEnts = set()
buildBlockModelEnts = set()
GENERAL_PAPER_VECTOR = {'ID': [], 'paper title': [], 'keywords vector': [], 'arcModelEntsVector': [],
                        'actModelEntsVector': [], 'buildBlockModelEntsVector': []}
paperIDcounter = 1
paperCount = 0
keywordsFile = open(r'NEWoutput\keywordVectors.csv', mode='a', encoding='UTF-8')
arcEntsFile = open(r'NEWoutput\arcEntsVector.csv', mode='a', encoding='UTF-8')
actEntsFile = open(r'NEWoutput\actEntsVector.csv', mode='a', encoding='UTF-8')
buildBlocksFile = open(r'NEWoutput\buildBlocksVector.csv', mode='a', encoding='UTF-8')
nlp = spacy.load('en_core_web_sm')
nlp.max_length = 1100000
"""
    Explanation on how the script works:
    It has 3 input parameters:
    CATEGORY_DIR_PATH (required) -> dir path which contains folders labeled by their pdf category, and inside each of those
    category folders are PDF files
    INPUT_KEYWORDS_BY_CATEGORY_PATH (optional) -> similar as before, a path to a folder which contains categories, and inside them
    .csv files containing keywords with a comma separator
    OUTPUT_KEYWORDS_PATH -> a path where the found keywords from every pdf will be written, in the format CATEGORY_NAME.csv
"""


# OVDE potrebna ni e kategorijata od sekoj fajl, zatoa mora for ciklusov, za da znaeme od koja kategorija pripagja
def makeVectorForPDF(pdf, all_keywords, catIdx, fileIdx, cat_name):
    global GENERAL_PAPER_VECTOR, paperIDcounter, paperCount
    # Getting table of content titles
    # Mozhno podobruvanje, baraj go naslovot samo na stranata koja e navedeno
    # mnogu poedinechni sluchaevi ima shto nekoi tekst da se chisti/sredi
    pdfToc = pdf.getToC()
    # getting all the ToC titles, except the word References, because it is needed for finding the end of a research paper
    tocTitlesNoReferences = [element[1].strip() for element in pdfToc if element[1].strip() != 'References']
    if all_keywords is not None:
        GENERAL_PAPER_VECTOR['keywords vector'] = dict.fromkeys(all_keywords, 0)
    paperIDcounter = 1
    foundKeywords = []
    for pageNm, page in enumerate(pdf, 1):

        pageTextInLines = preprocessSinglePdfPage(page, tocTitlesNoReferences)
        #kewords ke bide prazno skoro za sekoja strana, trgni gi deka ti samo na edna ke ti bide polna ova
        keywords, paperTitle = pageKeywordsTESTbyGETTEXTBLOCKS(page, pageNm, pdf, pdfToc, catIdx, fileIdx, all_keywords)

        # otkako ke se najde References, taa funckija ima raboti da go vrati generalniot vektor kako shto beshe originalno
        if all_keywords is not None:
            # isto i za ovie dole vazhi deka pogolemiot del ke ti vracha prazni, kade e gi iskoristis ? nigde
            arcModelVec, actModelVec, buildBlockModelVec = tryMakeEntityVector(pageTextInLines, catIdx, fileIdx)

        # ID is set when we finish finding all vectors for the paper, so if it's present, it means all other vectors are present
        if GENERAL_PAPER_VECTOR['ID']:
            print(GENERAL_PAPER_VECTOR['ID'])
            paperCount += 1
            writeVectors(GENERAL_PAPER_VECTOR['ID'])
            reInitializeVector(all_keywords)
        foundKeywords += keywords
    # gi vrakjam site keywords so mali bukvi, trgnati prazni mesta na pochetokot i na krajot
    return foundKeywords


"""
1.gleda dali pishuva "Abstract" na stranata (na pochetok na rechenica)
2. ako ima gleda dali pishuva "Keywords" ili "Key words" na stranata ( na pochetok na rechenica)
3. ako ima gleda dali ima zborchinja posle Zborot Keywords/key words, dali toa bilo vo ist red so zborot Keywords/key words ili posle vo naredniot red
4 ako ima gi zema niv se dodeka ne dojde do linija kade shto pishuva 1 Introduction, deka ako ja vidime taa znachi deka sme gi zele site zborchinja koi oznachuvaat keywords.
5 Note: zema po 2 linii keywords, deka ako zeme povishe, ima shansa da nema 1 Introduction i da zeme tekst shto ne e keywords.
"""


def writeVectorHeaders(keywordsSet):
    keywordsFile.write('ID,' + ','.join(keywordsSet))
    keywordsFile.write('\n')

    arcEntsFile.write('ID,' + ','.join(ARC_TYPE_KYW))
    arcEntsFile.write('\n')

    actEntsFile.write('ID,' + ','.join(ACT_FUNC_KYW))
    actEntsFile.write('\n')

    buildBlocksFile.write('ID,' + ','.join(BUILD_BLOCK_KYW))
    buildBlocksFile.write('\n')


def writeVectors(paperID):
    keywordsFile.write('%s,' % paperID + ','.join(map(str, GENERAL_PAPER_VECTOR['keywords vector'].values())) + '\n')
    arcEntsFile.write('%s,' % paperID + ','.join(map(str, GENERAL_PAPER_VECTOR['arcModelEntsVector'].values())) + '\n')
    actEntsFile.write('%s,' % paperID + ','.join(map(str, GENERAL_PAPER_VECTOR['actModelEntsVector'].values())) + '\n')
    buildBlocksFile.write(
        '%s,' % paperID + ','.join(map(str, GENERAL_PAPER_VECTOR['buildBlockModelEntsVector'].values())) + '\n')
    keywordsFile.flush()
    arcEntsFile.flush()
    actEntsFile.flush()
    buildBlocksFile.flush()


def extractTitle(pdf, titlePageNm):
    titlePageNm -= 1
    tmp = fitz.open()
    tmp.insertPDF(pdf, from_page=titlePageNm, to_page=titlePageNm)  # make a 1-page PDF of it
    tmp.save("Temp/paperTitle.pdf")
    tmp.close()
    completed_process = subprocess.run(['pdftitle', '-p', 'Temp/paperTitle.pdf'], capture_output=True, text=True, encoding='UTF-8')
    return completed_process.stdout.strip()


# split keywords by conjunction, so we can have more specialized keywords and less general ones
def splitByConjunction(keywords):
    conjunctionSplitKeyW = []
    for keywordPhrase in keywords:
        doc = nlp(keywordPhrase)
        for token in doc:
            if 'conj' in token.pos_.lower():
                conjunctionSplitKeyW += keywordPhrase.split(token.text)
                break
        else:
            conjunctionSplitKeyW.append(keywordPhrase)
    return [keyword.strip() for keyword in conjunctionSplitKeyW if keyword != '' and not keyword.isspace()]


def pageKeywordsTESTbyGETTEXTBLOCKS(page, pageNm, pdf, pdfToc, catIdx, fileIdx, allKeywords):
    global foundBeginning, paperText, paperIDcounter, GENERAL_PAPER_VECTOR, paperCount
    blocks = page.getText('blocks')
    textBlocks = [block[4].replace('-\n', '').replace('\xa0', ' ').replace('\n', ' ').strip() for block in blocks]
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
        if paperText != '':
            print('NEFINISHIRAN TEKST')
            # ovde zapishuvam trud ako predhodno ne doprel kaj References
            #mozhesh da go stavish vo edna funkcija.
            arcModelEnts = [ent.text for ent in nlp_arc(paperText).ents]
            actModelEnts = [ent.text for ent in nlp_act(paperText).ents]
            buildBlockModelEnts = [ent.text for ent in nlp_build(paperText).ents]
            arcModelVec, actModelVec, buildBlockModelVec = updateCategoryVectors(arcModelEnts, actModelEnts,
                                                                                 buildBlockModelEnts)
            GENERAL_PAPER_VECTOR['arcModelEntsVector'] = arcModelVec
            GENERAL_PAPER_VECTOR['actModelEntsVector'] = actModelVec
            GENERAL_PAPER_VECTOR['buildBlockModelEntsVector'] = buildBlockModelVec
            GENERAL_PAPER_VECTOR['ID'] = makePaperID(catIdx, fileIdx, paperIDcounter)
            paperIDcounter = paperIDcounter + 1
            paperText = ''
            paperCount += 1
            writeVectors(GENERAL_PAPER_VECTOR['ID'])
            print('Go zapishuvam so ID: %s' % GENERAL_PAPER_VECTOR['ID'])
            reInitializeVector(allKeywords)
            # the end
        keywords = re.split(r'[^a-zA-Z0-9\-\.\(\)’\–\- ]', keywords)
        keywords = [re.sub(r'\s{2,}', ' ', keyword.strip().lower().rstrip('.')) for keyword in keywords if
                    not keyword.strip().rstrip('.').isspace() and keyword.strip().rstrip('.') != '']
        keywords = splitByConjunction(keywords)
        for keyword in keywords:
            if not GENERAL_PAPER_VECTOR['keywords vector']:
                break
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
        paperTitle = paperTitle.replace('\n', '').replace('\r', ' ')
        GENERAL_PAPER_VECTOR['paper title'] = paperTitle
    else:
        keywords = []
    return keywords, paperTitle


def updateCategoryVectors(arcModelEnts, actModelEnts, buildBlockModelEnts):
    global GENERAL_PAPER_VECTOR
    arcModelVec = getVectorFromCategory(arcModelEnts, ARC_TYPE_SEARCH_WORDS, ARC_TYPE_KYW)
    actModelVec = getVectorFromCategory(actModelEnts, ACT_FUNC_SEARCH_WORDS, ACT_FUNC_KYW)
    buildBlockModelVec = getVectorFromCategory(buildBlockModelEnts, BUILD_BL_SEARCH_WORDS, BUILD_BLOCK_KYW)

    return arcModelVec, actModelVec, buildBlockModelVec


def reInitializeVector(all_keywords):
    global GENERAL_PAPER_VECTOR
    GENERAL_PAPER_VECTOR = {'ID': [], 'paper title': [], 'keywords vector': [], 'arcModelEntsVector': [],
                            'actModelEntsVector': [], 'buildBlockModelEntsVector': []}
    GENERAL_PAPER_VECTOR['keywords vector'] = dict.fromkeys(all_keywords, 0)


def tryMakeEntityVector(pageTextInLines, catIdx, fileIdx):
    global foundBeginning, paperText, insidePaper, actModelEnts, arcModelEnts, buildBlockModelEnts, GENERAL_PAPER_VECTOR, paperIDcounter
    arcModelVec, actModelVec, buildBlockModelVec = None, None, None
    if foundBeginning:
        # if paperText != '':
            # print('NEFINISHIRAN TEKST')
            #
            # arcModelEnts = [ent.text for ent in nlp_arc(paperText).ents]
            # actModelEnts = [ent.text for ent in nlp_act(paperText).ents]
            # buildBlockModelEnts = [ent.text for ent in nlp_build(paperText).ents]
            # arcModelVec, actModelVec, buildBlockModelVec = updateCategoryVectors(arcModelEnts, actModelEnts,
            #                                                                      buildBlockModelEnts)
            # GENERAL_PAPER_VECTOR['arcModelEntsVector'] = arcModelVec
            # GENERAL_PAPER_VECTOR['actModelEntsVector'] = actModelVec
            # GENERAL_PAPER_VECTOR['buildBlockModelEntsVector'] = buildBlockModelVec
            # GENERAL_PAPER_VECTOR['ID'] = makePaperID(catIdx, fileIdx, paperIDcounter)
            # paperIDcounter = paperIDcounter + 1
            # paperText = ''

        foundBeginning = False
        insidePaper = True
        paperText = ''.join(pageTextInLines) + ' '
        return arcModelVec, actModelVec, buildBlockModelVec
    elif insidePaper:
        for line in pageTextInLines:
            if line[0:10] == 'References' or line[0:9] == 'Refrences':
                arcModelEnts = [ent.text for ent in nlp_arc(paperText).ents]
                actModelEnts = [ent.text for ent in nlp_act(paperText).ents]
                buildBlockModelEnts = [ent.text for ent in nlp_build(paperText).ents]
                arcModelVec, actModelVec, buildBlockModelVec = updateCategoryVectors(arcModelEnts, actModelEnts,
                                                                                     buildBlockModelEnts)
                GENERAL_PAPER_VECTOR['arcModelEntsVector'] = arcModelVec
                GENERAL_PAPER_VECTOR['actModelEntsVector'] = actModelVec
                GENERAL_PAPER_VECTOR['buildBlockModelEntsVector'] = buildBlockModelVec
                GENERAL_PAPER_VECTOR['ID'] = makePaperID(catIdx, fileIdx, paperIDcounter)
                paperIDcounter += 1

                insidePaper = False
                paperText = ''
                return arcModelVec, actModelVec, buildBlockModelVec
        else:
            paperText += ' '.join(pageTextInLines) + ' '
    return arcModelVec, actModelVec, buildBlockModelVec


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


def processCategory(cat_path, catIdx, keywordsSet, keywordOutputPath=None):
    global fileNames, pdfPathNames

    if keywordOutputPath:
        writeFile = open(keywordOutputPath, mode='a', encoding='UTF-8')

    for fileIdx, file in enumerate(os.listdir(cat_path), 1):
        keyWords = set()
        print(file)
        # Checks if file is already processed by file name file size (sometimes 2 different pdfs have same name)
        PDF_PATH = os.path.join(cat_path, file)
        if file not in fileNames:
            fileNames.append(file)
            pdfPathNames[file] = PDF_PATH
        elif Path(pdfPathNames[file]).stat().st_size == Path(PDF_PATH).stat().st_size:
            print('Info: Found duplicate file, skipping processing it')
            continue
        pdf = fitz.open(PDF_PATH)

        keyWordsFromPdf = makeVectorForPDF(pdf, keywordsSet, catIdx, fileIdx, os.path.basename(cat_path))
        if keywordOutputPath and keyWordsFromPdf:
            for keyWord in keyWordsFromPdf:
                keyWords.add(keyWord)
            writeFile.write(','.join(keyWords) + ',')
    if keywordOutputPath:
        writeFile.close()


def processEveryCategory(cats_path, keywordInputDir=None, keywordOutputDir=None):
    global fileNames, pdfPathNames
    fileNames = []
    pdfPathNames = {}
    # nema potreba od pravenje vo set, deka posle vo drugata funckija pravish dict.fromKeys() i toa gi trga duplikatite, so sepak
    keywordsSet = None
    if keywordInputDir:
        keywordsSet = set()
        for keywordFile in os.listdir(keywordInputDir):
            with open(os.path.join(keywordInputDir, keywordFile), mode='r', encoding='UTF-8')as kw:
                words = kw.read().split(',')
                for keyword in words:
                    if keyword != '':
                        keywordsSet.add(keyword)
        print(len(keywordsSet))
        writeVectorHeaders(keywordsSet)

    for catIdx, cat in enumerate(os.listdir(cats_path), 1):
        cat_path = os.path.join(cats_path, cat)
        if keywordOutputDir:
            categoryName = os.path.basename(cat_path)
            keyWordFilePath = os.path.join(keywordOutputDir, '%s.csv' % categoryName)
            processCategory(cat_path, catIdx, keywordsSet, keyWordFilePath)
        else:
            processCategory(cat_path, catIdx, keywordsSet)
    print('Paper count %d' % paperCount)

@plac.annotations(
    cats_path=('Path to a directory containing the categories of PDF files, and inside each category are the PDF files.', 'positional'),
    keyword_dir=('Path to a directory where all the keywords will be saved in their respectful category.', 'positional'),
    best_arc_model=('Architecture type model that will be used for extracting entities.', 'positional'),
    best_act_model=('Activation function model that will be used for extracting entities.', 'positional'),
    best_build_model=('Building blocks model that will be used for extracting entities.', 'positional')
)
def main(cats_path, keyword_dir, best_arc_model, best_act_model, best_build_model):
    global nlp_arc, nlp_act, nlp_build
    nlp_arc = spacy.load(best_arc_model)
    nlp_act = spacy.load(best_act_model)
    nlp_build = spacy.load(best_build_model)

    nlp_arc.max_length = 1100000
    nlp_act.max_length = 1100000
    nlp_build.max_length = 1100000

    processEveryCategory(cats_path, keywordOutputDir=keyword_dir)
    processEveryCategory(cats_path, keywordInputDir=keyword_dir)


if __name__ == '__main__':
    plac.call(main)
    # main(r'C:\Users\Gjorgji Noveski\PycharmProjects\SciBooksCrawler\SciBooks\Downloaded PDFs VtorPat', r'NEWkeywords', r'C:\\Users\\Gjorgji Noveski\\PycharmProjects\\PDFtoDatabase\\NEWNERmodels\\specialized\\architecture type model\\88 epochs',
    #      r'C:\\Users\\Gjorgji Noveski\\PycharmProjects\\PDFtoDatabase\\NEWNERmodels\\specialized\\activation function model\\95 epochs', r'C:\\Users\\Gjorgji Noveski\\PycharmProjects\\PDFtoDatabase\\NEWNERmodels\\specialized\\building blocks model\\93 epochs')
