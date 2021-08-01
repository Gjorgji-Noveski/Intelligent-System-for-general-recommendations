import fitz
import re
import os
import spacy
import subprocess
import plac
from Preprocessing import preprocessSinglePdfPage, makePaperID, checkAlreadyProcessedFile, PDF_PATHS, FILE_NAMES
from WordSetAndMappings import ACTIVATION_FUNC as ACT_FUNC_SEARCH_WORDS, ARCHITECTURE_TYPE as ARC_TYPE_SEARCH_WORDS, \
    BUILDING_BLOCKS as BUILD_BL_SEARCH_WORDS, ACTIVATION_FUNC_NO_ABBREVIATION as ACT_FUNC_KYW, \
    ARCHITECTURE_TYPE_NO_ABBREVIATION as ARC_TYPE_KYW, \
    BUILDING_BLOCKS_NO_ABBREVIATION as BUILD_BLOCK_KYW, mappings

paperText = ''
insidePaper = False
nlp_act = None
nlp_arc = None
nlp_build = None
arcModelEnts = set()
actModelEnts = set()
buildBlockModelEnts = set()
all_keywords = None
GENERAL_PAPER_VECTOR = {'ID': [], 'paper title': [], 'keywords vector': [], 'arcModelEntsVector': [],
                        'actModelEntsVector': [], 'buildBlockModelEntsVector': []}
paperCount = 0
paperIDcounter = 1
keywordsFile = open(r'datasets\intelligent system\keywordVectorsBiggest.csv', mode='a', encoding='UTF-8')
arcEntsFile = open(r'datasets\intelligent system\arcEntsVectorBiggest.csv', mode='a', encoding='UTF-8')
actEntsFile = open(r'datasets\intelligent system\actEntsVectorBiggest.csv', mode='a', encoding='UTF-8')
buildBlocksFile = open(r'datasets\intelligent system\buildBlocksVectorBiggest.csv', mode='a', encoding='UTF-8')
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
def makeVectorForPDF(pdf, catIdx, fileIdx):
    global GENERAL_PAPER_VECTOR, paperText, insidePaper, all_keywords, paperIDcounter
    paperIDcounter = 1
    pdfToc = pdf.getToC()
    # getting all the ToC titles, except the word References, because it is needed for finding the end of a research paper
    tocTitlesNoReferences = [element[1].strip() for element in pdfToc if 'reference' not in element[1].strip().lower()]
    if all_keywords is not None:
        GENERAL_PAPER_VECTOR['keywords vector'] = dict.fromkeys(all_keywords, 0)
    foundKeywords = []
    for pageNm, page in enumerate(pdf, 1):
        pageTextInLines = preprocessSinglePdfPage(page, tocTitlesNoReferences)
        #kewords ke bide prazno skoro za sekoja strana, ama ke ti treba koga ke ja gradish listata so keywords
        keywords, paperTitle = getPageKeywords(page, pageNm, pdf, pdfToc, catIdx, fileIdx)

        if all_keywords is not None:
            tryMakeEntityVector(pageTextInLines, catIdx, fileIdx)

        foundKeywords += keywords
    if paperText != '' and insidePaper:
        populateVectors(catIdx, fileIdx)
        writeVectors(GENERAL_PAPER_VECTOR['ID'])
        reInitializeVector(all_keywords)
    paperText = ''
    insidePaper = False
    # gi vrakjam site keywords so mali bukvi, trgnati prazni mesta na pochetokot i na krajot
    return foundKeywords


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
    print(paperID)
    if 1 in list(GENERAL_PAPER_VECTOR['keywords vector'].values()):
        keywordsFile.write('%s,' % paperID + ','.join(map(str, GENERAL_PAPER_VECTOR['keywords vector'].values())) + '\n')
    else:
        print('Something wrong, found empty keywords vec')
        with open('empty_keyword_vec_log.txt', mode='w', encoding='utf-8')as ff:
            ff.write(f'Paper with id: {paperID} was empty, paper name:{GENERAL_PAPER_VECTOR["paper title"]}\nmozhno e da ima exception frleno i zatoa prazen da e, kaj try catch')
    if 1 in list(GENERAL_PAPER_VECTOR['arcModelEntsVector'].values()):
        arcEntsFile.write('%s,' % paperID + ','.join(map(str, GENERAL_PAPER_VECTOR['arcModelEntsVector'].values())) + '\n')
    if 1 in list(GENERAL_PAPER_VECTOR['actModelEntsVector'].values()):
        actEntsFile.write('%s,' % paperID + ','.join(map(str, GENERAL_PAPER_VECTOR['actModelEntsVector'].values())) + '\n')
    if 1 in list(GENERAL_PAPER_VECTOR['buildBlockModelEntsVector'].values()):
        buildBlocksFile.write('%s,' % paperID + ','.join(map(str, GENERAL_PAPER_VECTOR['buildBlockModelEntsVector'].values())) + '\n')

    # keywordsFile.flush()
    # arcEntsFile.flush()
    # actEntsFile.flush()
    # buildBlocksFile.flush()



def extractTitle(pdf, titlePageNm):
    titlePageNm -= 1
    tmp = fitz.open()
    title = ''
    try:
        tmp.insertPDF(pdf, from_page=titlePageNm, to_page=titlePageNm)  # make a 1-page PDF of it
        tmp.save("Temp/paperTitle.pdf")
        completed_process = subprocess.run(['pdftitle', '-p', 'Temp/paperTitle.pdf'], capture_output=True, text=True,
                                           encoding='UTF-8')
        title = completed_process.stdout.strip()
    except Exception as e:
        print(e)
    finally:
        tmp.close()
        return title


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


def getPageKeywords(page, pageNm, pdf, pdfToc, catIdx, fileIdx):
    global insidePaper, paperText, GENERAL_PAPER_VECTOR, all_keywords#, zeroKeywords
    blocks = page.getText('blocks')
    textBlocks = [block[4].replace('-\n', '').replace('\xa0', ' ').replace('\n', ' ').strip() for block in blocks if not block[4].isspace() and block[4] != '']
    foundAbstract = False
    keywords = ''
    paperTitle = 'Not found'
    for paragraph in textBlocks:
        if paragraph[:8].lower() == 'abstract':
            foundAbstract = True
            break
    if foundAbstract:
        # checking if the word 'keywords' and the keywords are in the same text box, if they are not
        # we take the text of the next text box because we know for sure that's where the keywords are
        # even if they aren't
        for idx, paragraph in enumerate(textBlocks):
            if paragraph.lower() == 'keywords' or paragraph.lower() == 'key words':
                paperTitle = extractTitle(pdf, pageNm)
                keywords += textBlocks[idx+1]
                break
            elif paragraph[:8].lower() == 'keywords' or paragraph[:9].lower() == 'key words':
                paperTitle = extractTitle(pdf, pageNm)
                keywords += paragraph[9:]
                break

    if keywords != '':
        if paperText != '':
            print('Previous paper\'s vectors weren\'t written but found new one, writing old ones vectors...')
            # ovde zapishuvam trud ako predhodno ne doprel kaj References
            #mozhesh da go stavish vo edna funkcija.
            populateVectors(catIdx, fileIdx)
            writeVectors(GENERAL_PAPER_VECTOR['ID'])
            reInitializeVector(all_keywords)
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
                insidePaper = True
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
    GENERAL_PAPER_VECTOR = {'ID': [], 'paper title': [], 'keywords vector': dict.fromkeys(all_keywords, 0),
                            'arcModelEntsVector': [], 'actModelEntsVector': [], 'buildBlockModelEntsVector': []}


def tryMakeEntityVector(pageTextInLines, catIdx, fileIdx):
    global insidePaper, paperText, GENERAL_PAPER_VECTOR, all_keywords
    if insidePaper:
        for line in pageTextInLines:
            if line[0:10].lower() == 'references' or line[0:9].lower() == 'refrences':
                populateVectors(catIdx, fileIdx)
                writeVectors(GENERAL_PAPER_VECTOR['ID'])
                reInitializeVector(all_keywords)
                break
        else:
            paperText += ' '.join(pageTextInLines) + ' '


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

def populateVectors(catIdx, fileIdx):
    global paperText, nlp_arc, nlp_act, nlp_build, insidePaper, paperCount, paperIDcounter
    try:
        arcModelEnts = [ent.text for ent in nlp_arc(paperText).ents]
        actModelEnts = [ent.text for ent in nlp_act(paperText).ents]
        buildBlockModelEnts = [ent.text for ent in nlp_build(paperText).ents]
    except Exception as e:
        print(e)
        insidePaper = False
        paperText = ''
        return
    arcModelVec, actModelVec, buildBlockModelVec = updateCategoryVectors(arcModelEnts, actModelEnts,
                                                                         buildBlockModelEnts)
    GENERAL_PAPER_VECTOR['arcModelEntsVector'] = arcModelVec
    GENERAL_PAPER_VECTOR['actModelEntsVector'] = actModelVec
    GENERAL_PAPER_VECTOR['buildBlockModelEntsVector'] = buildBlockModelVec
    GENERAL_PAPER_VECTOR['ID'] = makePaperID(catIdx, fileIdx, paperIDcounter)
    paperIDcounter += 1
    paperCount += 1
    insidePaper = False
    paperText = ''


def processCategory(cat_path, catIdx, keywordOutputPath=None):
    if keywordOutputPath:
        writeFile = open(keywordOutputPath, mode='a', encoding='UTF-8')

        #spored noviot folder testing sega go pravam ova, izbrishi posle
    for fileIdx, file in enumerate(os.listdir(cat_path), 1):
        keyWords = set()

        print(file)
        # Checks if file is already processed by file name file size (sometimes 2 different pdfs have same name)
        PDF_PATH = os.path.join(cat_path, file)
        if checkAlreadyProcessedFile(PDF_PATH, file):
            continue
        try:
            with fitz.open(PDF_PATH) as pdf:
                keyWordsFromPdf = makeVectorForPDF(pdf, catIdx, fileIdx)
        except Exception as e:
            continue
        if keywordOutputPath and keyWordsFromPdf:
            for keyWord in keyWordsFromPdf:
                keyWords.add(keyWord)
            writeFile.write(','.join(keyWords) + ',')
    if keywordOutputPath:
        writeFile.close()


def processEveryCategory(cats_path, keywordInputDir=None, keywordOutputDir=None):
    global all_keywords
    PDF_PATHS.clear()
    FILE_NAMES.clear()
    # nema potreba od pravenje vo set, deka posle vo drugata funckija pravish dict.fromKeys() i toa gi trga duplikatite, so sepak
    if keywordInputDir:
        keywordsSet = set()
        for keywordFile in os.listdir(keywordInputDir):
            with open(os.path.join(keywordInputDir, keywordFile), mode='r', encoding='UTF-8')as kw:
                words = kw.read().split(',')
                for keyword in words:
                    if keyword != '':
                        keywordsSet.add(keyword)
        print(len(keywordsSet))
        all_keywords = keywordsSet
        writeVectorHeaders(keywordsSet)

    for catIdx, cat in enumerate(os.listdir(cats_path), 1):
        cat_path = os.path.join(cats_path, cat)
        if keywordOutputDir:
            categoryName = os.path.basename(cat_path)
            keyWordFilePath = os.path.join(keywordOutputDir, '%s.csv' % categoryName)
            processCategory(cat_path, catIdx, keyWordFilePath)
        else:
            processCategory(cat_path, catIdx)
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
    keywordsFile.close()
    arcEntsFile.close()
    actEntsFile.close()
    buildBlocksFile.close()



if __name__ == '__main__':
    plac.call(main)
