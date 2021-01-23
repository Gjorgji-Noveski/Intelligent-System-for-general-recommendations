import spacy
import fitz
import re
import os
from pathlib import Path
from WordSetAndMappings import features, mappings

fileNames = []
pdfPathNames = {}

def addOccurrence(ent, feature_value):
    # checking if the entity is plular, then slicing it so we take it as singular and search that in the features
    ent = ent.strip().lower()
    if ent[-1] == 's':
        ent = ent[:-1]
    if ent in features:
        if ent in mappings:
            feature = mappings[ent]
        else:
            feature = ent
        feature_value[feature] = 1


# OVDE potrebna ni e kategorijata od sekoj fajl, zatoa mora for ciklusov, za da znaeme od koja kategorija pripagja
def makeVectorForPDF(pdf, nlp):
    # Getting table of content titles
    # Mozhno podobruvanje, baraj go naslovot samo na stranata koja e navedeno
    # mnogu poedinechni sluchaevi ima shto nekoi tekst da se chisti/sredi

    feature_value = dict.fromkeys(features, 0)
    tocTitles = [element[1] for element in pdf.getToC()]
    wholePdfText = ''
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
    # Poradi toa shto Imam 8GB RAM, moram da go secham dokumentot koj mu go davam na spacy
    # inache mozhno e da imam allocation error
    # 100,000 karakteri = 1GB za spacy, ama go zgolemiv malce pojshe
    splitPdfDocument = [wholePdfText[i:i + 1100000] for i in range(0, len(wholePdfText), 1100000)]
    del wholePdfText
    for chunk in splitPdfDocument:
        doc = nlp(chunk)
        for ent in doc.ents:
            addOccurrence(ent.text, feature_value)
    return feature_value


# najdobri se, act - 98, arc -77, building-87, dataset- 94 epochs
act_model = r'C:\Users\Gjorgji Noveski\Desktop\nov spacy test\specialized models\activation function model\95 epochs'
arc_model = r'C:\Users\Gjorgji Noveski\Desktop\nov spacy test\specialized models\architecture type model\95 epochs'
building_blocks_model = r'C:\Users\Gjorgji Noveski\Desktop\nov spacy test\specialized models\building blocks model\95 epochs'
dataset_model = r'C:\Users\Gjorgji Noveski\Desktop\nov spacy test\specialized models\dataset model\95 epochs'

pdfs_path = r'C:\Users\Gjorgji Noveski\Desktop\small pdfs'
model_list = [act_model, arc_model, building_blocks_model, dataset_model]

testPdf = r'C:\Users\Gjorgji Noveski\PycharmProjects\SciBooksCrawler\SciBooks\Downloaded PDFs\proteins\IntrinsicallyDisorderedProteinsStudiedbyNMRSpectroscopy.pdf'
nlp = spacy.load(model_list[0])
testPdf = fitz.open(testPdf)
nlp.max_length = 1300000
makeVectorForPDF(testPdf, nlp)

# for countFolder, field in enumerate(os.listdir(pdfs_path), 1):
#     FILE_CATEGORY_PATH = os.path.join(pdfs_path, field)
#     for countFile, file in enumerate(os.listdir(FILE_CATEGORY_PATH), 1):
#         if file[-4:] != '.pdf':
#             continue
#         outputText = 'field: %s\n' % field
#         for model in model_list:
#             nlp = spacy.load(model)
#             nlp.max_length = 1200000
#             PDF_PATH = os.path.join(FILE_CATEGORY_PATH, file)
#             pdf = fitz.open(PDF_PATH)
#             model_vector = makeVectorForPDF(pdf, nlp)
#             outputText +='%s vector -> %s\n\n' %(model.split('\\')[-2], model_vector)
#         outputText+='\n'
#         with open(r'C:\Users\Gjorgji Noveski\Desktop\output vectors.txt', mode='a', encoding='utf-8')as f:
#             f.write(outputText)
