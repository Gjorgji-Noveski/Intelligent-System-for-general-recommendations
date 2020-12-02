import spacy
import os
import os.path
import fitz

NLP_MODEL_PATH = r'C:\Users\Gjorgji Noveski\Desktop\Files for my Spacy work\NLP models and bin training ' \
                 r'data\Incremental epochs,850sents, decaying dropout(0.4,0.3,0.001),Whole batch passed,ischisteni ' \
                 r'sents\16 epochs on 850 sents'

nlp = spacy.load(NLP_MODEL_PATH)
nlp.add_pipe(nlp.create_pipe('sentencizer'))
nlp.max_length = 1300000
DOWNLOADED_PDFS_PATH = r"C:\Users\Gjorgji Noveski\PycharmProjects\SciBooksCrawler\SciBooks\Downloaded PDFs"
import sys


def extractEntitySents(pdfs_path):
    for countFolder, folder in enumerate(os.listdir(pdfs_path), 1):
        FILE_CATEGORY_PATH = os.path.join(pdfs_path, folder)
        print(countFolder, folder)

        for countFile, file in enumerate(os.listdir(FILE_CATEGORY_PATH), 1):
            if file == 'debug.log' or file[-4:] != '.pdf':
                continue
            PDF_PATH = os.path.join(FILE_CATEGORY_PATH, file)

            doc = fitz.open(PDF_PATH)

            # Getting table of content titles
            # Mozhno podobruvanje, baraj go naslovot samo na stranata koja e navedeno
            # mnogu poedinechni sluchaevi ima shto nekoi tekst da se chisti/sredi
            tocTitles = [element[1] for element in doc.getToC()]
            print(PDF_PATH)
            for idx, page in enumerate(doc):
                pageText = page.getText()
                pageText = pageText.replace('\xa0', ' ')
                pageTextInLines = pageText.split("\n")

                pageTextInLines = [line.strip() for line in pageTextInLines if not line.isspace() and line != '']
                # Proveruva ako Naslovot od Table of contents e ist so naslovot na pochetokot na stranata, ako e ist go brishe
                # Za da mozhe rechenicata od proshlata strana da se spoi so rechenica od narednata
                # isto taka go brishe i brojot na stranata ako go najde na pochetokot od stranata
                # celta e otstranuvanje nepotrebni povtoruvanja na zaglavjeto na stranata i kako shto kazhav spojuvanje so rechenica od

                for tocTitle in tocTitles:

                    tocTitle = tocTitle.strip()

                    if tocTitle in pageTextInLines[0]:
                        pageTextInLines.remove(pageTextInLines[0])

                    elif tocTitle in pageTextInLines[1]:
                        pageTextInLines.remove(pageTextInLines[1])

                    if pageTextInLines[0].isnumeric():
                        print("Brisham borj")
                        pageTextInLines.remove(pageTextInLines[0])


extractEntitySents(DOWNLOADED_PDFS_PATH)
