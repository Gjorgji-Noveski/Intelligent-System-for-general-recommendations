import spacy
import os
import os.path
import fitz
import re
from pathlib import Path

NLP_MODEL_PATH = r'C:\Users\Gjorgji Noveski\Desktop\Files for my Spacy work\NLP models and bin training ' \
                 r'data\Incremental epochs,850sents, decaying dropout(0.6,0.35,0.00003),batch compounding(32,128,1.001),ischisteni sents' \
                 r'\65 epochs on 850 sents'
NLP_MODEL_PATH_PARSER = r'C:\Users\Gjorgji Noveski\Desktop\65 epochs on 850 sents'

MODEL_NAME = NLP_MODEL_PATH.split(os.path.sep)[-2] + ' ' + NLP_MODEL_PATH.split(os.path.sep)[-1]

nlp = spacy.load(NLP_MODEL_PATH_PARSER)
nlp.add_pipe(nlp.create_pipe('sentencizer'))
nlp.max_length = 1200000

DOWNLOADED_PDFS_PATH = r"C:\Users\Gjorgji Noveski\PycharmProjects\SciBooksCrawler\SciBooks\Downloaded PDFs"
OUTPUT_FOLDER = r'C:\Users\Gjorgji Noveski\Desktop\Files for my Spacy work\Extracted Entity Sents'
fileNames = []
pdfPathNames = {}
''' ------------------------ '''

# TODO: OTFRLI RECHENICI SHTO SE MNOGU DOLGI, NEKOGASH IMA ENT.SENT SHOT E PREGOLEM PORADI NEMANJE TOCKA

''' ------------------------ '''



def extractEntitySents(pdfs_path, output_folder):
    global fileNames, pdfPathNames
    # with open(os.path.join(OUTPUT_FOLDER, "Model used here.txt"), mode='w', encoding='utf-8')as mf:
    #     mf.write(MODEL_NAME)
    for countFolder, folder in enumerate(os.listdir(pdfs_path), 1):
        FILE_CATEGORY_PATH = os.path.join(pdfs_path, folder)
        for countFile, file in enumerate(os.listdir(FILE_CATEGORY_PATH), 1):
            if file[-4:] != '.pdf':
                continue
            PDF_PATH = os.path.join(FILE_CATEGORY_PATH, file)
            pdf = fitz.open(PDF_PATH)
            # Getting table of content titles
            # Mozhno podobruvanje, baraj go naslovot samo na stranata koja e navedeno
            # mnogu poedinechni sluchaevi ima shto nekoi tekst da se chisti/sredi

            tocTitles = [element[1] for element in pdf.getToC()]

            EXTRACTED_ENTITY_SENTS_PATH = os.path.join(output_folder,
                                                       str(countFolder) + '00' + str(countFile) + '_' + file[
                                                                                                        :5] + '_' + file[
                                                                                                                    -15:-4] + '.txt')
            # Checks if file is already processed by file name file size (sometimes 2 different pdfs have same name)
            if file not in fileNames:
                fileNames.append(file)
                pdfPathNames[file] = PDF_PATH
            elif Path(pdfPathNames[file]).stat().st_size == Path(PDF_PATH).stat().st_size:
                print(PDF_PATH)
                continue

            continue
            wholePdfText = ''
            # with open(EXTRACTED_ENTITY_SENTS_PATH, mode='a', encoding='UTF-8') as entFile:
            for idx, page in enumerate(pdf):
                pageText = re.sub("-\n", "", page.getText().replace('\xa0', ' '))

                pageTextInLines = pageText.split("\n")
                pageTextInLines = [line.strip() for line in pageTextInLines if not line.isspace() and line != '']

                # Proveruva ako Naslovot od Table of contents e ist so naslovot na pochetokot na stranata, ako e ist go brishe
                # Za da mozhe rechenicata od proshlata strana da se spoi so rechenica od narednata
                # isto taka go brishe i brojot na stranata ako go najde na pochetokot od stranata
                # celta e otstranuvanje nepotrebni povtoruvanja na zaglavjeto na stranata i kako shto kazhav spojuvanje so rechenica od

                # checking if the first 2 sentences contain the "et al." part so it can be removed
                if len(pageTextInLines) > 1:
                    if 'et al' in pageTextInLines[0]:
                        pageTextInLines.remove(pageTextInLines[0])

                    elif 'et al' in pageTextInLines[1]:
                        pageTextInLines.remove(pageTextInLines[1])

                # checking if some ToC titles are in the first 2 sentences returned
                for tocTitle in tocTitles:
                    if len(pageTextInLines) <= 2:
                        break
                    tocTitle = tocTitle.strip()
                    if tocTitle in pageTextInLines[0]:
                        pageTextInLines.remove(pageTextInLines[0])

                    elif tocTitle in pageTextInLines[1]:
                        pageTextInLines.remove(pageTextInLines[1])

                    if pageTextInLines[0].isnumeric():
                        pageTextInLines.remove(pageTextInLines[0])

                wholePdfText += ' '.join(pageTextInLines) + ' '
            # Poradi toa shto Imam 8GB RAM, moram da go secham dokumentot koj mu go davam na spacy
            # inache mozhno e da imam allocation error
            # 100,000 karakteri = 1GB za spacy, ama go zgolemiv malce pojshe

            # splitPdfDocument = [wholePdfText[i:i + 1100000] for i in range(0, len(wholePdfText), 1100000)]
            # del wholePdfText
            # entitySents = set()
            doc = nlp(wholePdfText)
            entities = []
            for sent in doc.sents:
                print(sent.text)
            # entitiesRemoveDuplicate = []
            # [entitiesRemoveDuplicate.append(ele) for ele in entities if ele not in entitiesRemoveDuplicate]
            # displacy.serve(doc, style='ent')
            # with open("C:/Users/Gjorgji Noveski/Desktop/DobieniOdParser.txt", mode='a', encoding='utf-8')as fw:
            #     fw.writelines('\n'.join(entitiesRemoveDuplicate))
            # for chunk in splitPdfDocument:
            #     doc = nlp(chunk)

            # for ent in doc.ents:
            #     entitySents.add(ent.sent.text)

            # entFile.writelines('\n'.join(entitySents))


extractEntitySents(DOWNLOADED_PDFS_PATH, OUTPUT_FOLDER)
