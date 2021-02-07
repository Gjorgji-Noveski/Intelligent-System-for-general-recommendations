import spacy
import os
import os.path
import fitz
import plac
from Preprocessing import preprocessSinglePdfPage, checkAlreadyProcessedFile

NLP_MODEL_PATH_PARSER = r'C:\Users\Gjorgji Noveski\Desktop\nov spacy test\22 epochs on 850 sents 77fscore'

DOWNLOADED_PDFS_PATH = r"C:\Users\Gjorgji Noveski\PycharmProjects\SciBooksCrawler\SciBooks\Downloaded PDFs"
OUTPUT_FOLDER = r'C:\Users\Gjorgji Noveski\Desktop\nov spacy test\Extracted Entity Sents, one phrase entity'

''' ------------------------ '''

# TODO: OTFRLI RECHENICI SHTO SE MNOGU DOLGI, NEKOGASH IMA ENT.SENT SHOT E PREGOLEM PORADI NEMANJE TOCKA

''' ------------------------ '''


def extractEntitySents(pdf, outputDir, countFolder, countFile, file, characterLimit, nlp):
    # Getting table of content titles
    # Mozhno podobruvanje, baraj go naslovot samo na stranata koja e navedeno
    tocTitles = [element[1] for element in pdf.getToC()]
    extractedEntSentFileName = str(countFolder) + '00' + str(countFile) + '_' + file[:5] + '_' + file[-15:-4] + '.txt'
    EXTRACTED_ENTITY_SENTS_PATH = os.path.join(outputDir, extractedEntSentFileName)
    wholePdfText = ''
    for page in pdf:

        pageTextInLines = preprocessSinglePdfPage(page, tocTitles)

        wholePdfText += ' '.join(pageTextInLines) + ' '

    # Poradi toa shto Imam 8GB RAM, moram da go secham dokumentot koj mu go davam na spacy
    # inache mozhno e da imam allocation error
    # 100,000 karakteri = 1GB za spacy, ama go zgolemiv malce pojshe
    splitPdfDocument = [wholePdfText[i:i + characterLimit] for i in range(0, len(wholePdfText), characterLimit)]
    del wholePdfText
    entitySents = set()
    with open(EXTRACTED_ENTITY_SENTS_PATH, mode='a', encoding='UTF-8') as entSentFile:
        for chunk in splitPdfDocument:
            doc = nlp(chunk)
            for ent in doc.ents:
                entitySents.add(ent.sent.text)
        entSentFile.writelines('\n'.join(entitySents))
    print('Extracted: ' + extractedEntSentFileName)

@plac.annotations(
    model_path=('Path to a Spacy model that will be used for extracting named entities', 'option', 'm', str),
    pdfs_path=('Directory containing categories and inside each category are PDF files.', 'option', 'i', str),
    output_dir=('Output directory where all the extracted sentences that contain an entity will be saved.', 'option', 'o', str),
    character_limit=('Maximum number of characters a single preprocessed pdf chunk will have.', 'option', 'l', int)
)
def main(model_path, pdfs_path, output_dir, character_limit=3000000):
    """
    This script takes as input a directory that contains other directories labeled by the category of PDFs
    that are inside them.
    Ex. Medicine_category -> contains PDFs related to the field of medicine
    Engineering_category -> contains PDFs related to field of engineering

    After processing the PDF files using a Spacy model it extracts the sentences that contain named entities.
    It saves the found sentences in .txt from each PDF file to the path set by the output_folder parameter.

    The character_limit parameter is used to check the number of characters of a PDF file after it has been preprocessed.
    This is because Spacy's NER needs around 1GB of memory for every 100,000 characters and someone might have less
    memory required to process a whole PDF file. So this parameter adds the option to split the preprocessed PDF
    into parts that are <= character_limit. Default value is 3,000,000, suitable for any large PDF file you may find
    in the wild.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    nlp = spacy.load(model_path)
    nlp.max_length = 3000000
    for countFolder, folder in enumerate(os.listdir(pdfs_path), 1):
        FILE_CATEGORY_PATH = os.path.join(pdfs_path, folder)
        print(folder)
        for countFile, file in enumerate(os.listdir(FILE_CATEGORY_PATH), 1):
            if file[-4:] != '.pdf':
                continue
            PDF_PATH = os.path.join(FILE_CATEGORY_PATH, file)
            if checkAlreadyProcessedFile(PDF_PATH, file):
                continue
            pdf = fitz.open(PDF_PATH)
            extractEntitySents(pdf, output_dir, countFolder, countFile, file, character_limit, nlp)


if __name__ == '__main__':
    plac.call(main)