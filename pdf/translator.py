# standard libraries
import argparse
import time

# installed libraries
import pdftotext
from google_trans_new import google_translator

argparser = argparse.ArgumentParser()
argparser.add_argument("fileinput", help="Enter the PDF file name containing the text to translate")
argparser.add_argument("target", help="Enter the target language to which the text should be translated")
argparser.add_argument("fileoutput", help="Enter the file name for the translated results")


def getListOfTextFromPdf(fileinput):
    with open(fileinput, "rb") as f:
        pagesAsListOfText = pdftotext.PDF(f)
    return pagesAsListOfText


def translateEachTextToTarget(pagesOfText, target, outputfile):
    start = time.time()
    index = 1
    total = 0
    result_file = open(outputfile, "w")
    translator = google_translator(timeout=20)
    for text in pagesOfText:
        chars = len(text)
        total += chars
        if total >= 100000:
            end = time.time()
            elapsed = end - start
            diff = 100 - elapsed
            if diff > 0:
                time.sleep(diff)
                start = time.time()
                total = 0
        raw_dict = translator.translate(text, lang_tgt=target)

        result_file.write("Page {}".format(index))
        result_file.write("\n---------\n")
        result_file.write(u"{}".format(raw_dict))
        result_file.write("\n\n")

        index += 1

    result_file.close()


if __name__ == "__main__":
    args = argparser.parse_args()
    pagesOfText = getListOfTextFromPdf(args.fileinput)
    translateEachTextToTarget(pagesOfText, args.target, args.fileoutput)
