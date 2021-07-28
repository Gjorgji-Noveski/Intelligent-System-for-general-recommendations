from spacy.gold import GoldParse
from spacy.scorer import Scorer
from os import path
from os.path import join
import os.path
import pickle
import plac
import spacy
import re
import pandas as pd


@plac.annotations(
    models_dir=('Path to a directory where spacy NER_models will be used for evaluation', 'positional'),
    input_file=('An input spacy binary file from which evaluation sentences are taken from', 'positional')
)
def main(models_dir=None, input_file=None):
    """
    This script writes evaluation results only for the NER pipeline of the model.
    It takes a directory containing sub directiories of many Spacy models and saves the evaluation results inside the
    models directory.
    The binary input file is specified so the script knows on which sentences to evaluate.
    """
    if not os.path.isdir(models_dir):
        print('Please specify a directory to spacy NER_models')
        raise SystemExit(1)
    if not os.path.isfile(input_file):
        print('Please specify an input file')
        raise SystemExit(1)
    evalSents = makingEvaluationSents(input_file)
    unsortedModels = dict()
    header = 'epoch,ents_p,ents_r,ents_f\n'
    for model in os.listdir(models_dir):
        spacy_model = spacy.load(os.path.join(models_dir, model))
        results = evaluate(spacy_model, evalSents)
        model = re.search(r'\d+', model).group()
        results = '{epoch},{ents_p:.2f},{ents_r:.2f},{ents_f:.2f}\n'.format(epoch=model, ents_p=results['ents_p'],
                                                                            ents_r=results['ents_r'],
                                                                            ents_f=results['ents_f'])
        unsortedModels[model] = results
        # print("Evaluated %s" % model)

    # getting a sorted list so i can print the results in natural order
    sortedFileIdx = sorted(unsortedModels, key=int)
    outputFile = os.path.join(models_dir, "Evaluation results.csv")
    with open(outputFile, mode='a', encoding='utf-8') as wf:
        wf.write(header)
        tus = [unsortedModels[i] for i in sortedFileIdx]
        wf.writelines(tus)
    df = pd.read_csv(outputFile)
    bestEpochNm = str(int(df.iloc[df['ents_f'].argmax()][0]))
    for model in os.listdir(models_dir):
        if model.startswith(bestEpochNm):
            print(path.abspath(join(models_dir, model)))
            break


def makingEvaluationSents(input_bin):
    with open(input_bin, 'rb') as binary:
        data = pickle.load(binary)
    evalSents = []
    [evalSents.append((line[0], line[1].get('entities'))) for line in data]
    return evalSents


def evaluate(ner_model, examples):
    scorer = Scorer()
    for input_, annot in examples:
        doc_gold_text = ner_model.make_doc(input_)
        gold = GoldParse(doc_gold_text, entities=annot)
        pred_value = ner_model(input_)
        scorer.score(pred_value, gold)
    return scorer.scores


if __name__ == '__main__':
    plac.call(main)
