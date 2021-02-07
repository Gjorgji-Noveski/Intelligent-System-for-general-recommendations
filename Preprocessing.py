import re
from pathlib import Path

FILE_NAMES = []
PDF_PATHS = {}


def preprocessSinglePdfPage(page, tocTitles):
    """
    Filters any line from a page that starts with "Fig." or "Table " because usually those word indicate annotation for a figure/table.
    Also filters empty or lines filled with whitespace.
    """

    pageText = re.sub(r'-\n', '', page.getText().replace('\xa0', ' '))
    pageTextInLines = pageText.split('\n')
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

    return pageTextInLines


def makePaperID(catIdx, fileIdx, paperIdx):
    filler = '00'
    return str(catIdx) + filler + str(fileIdx) + filler + str(paperIdx)


def checkAlreadyProcessedFile(pdfPath, fileName):
    # Checks if file is already processed by file name and file size (sometimes 2 different pdfs have same name)
    if fileName not in FILE_NAMES:
        FILE_NAMES.append(fileName)
        PDF_PATHS[fileName] = pdfPath
    elif Path(PDF_PATHS[fileName]).stat().st_size == Path(pdfPath).stat().st_size:
        print('Found duplicate file, skipping processing it')
        return True
    return False
