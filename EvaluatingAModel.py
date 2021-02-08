from spacy.gold import GoldParse
from spacy.scorer import Scorer
import os.path
import pickle
import plac
import spacy

# TODO: Careful NOT to evaluate a model on the SAME sentences it was trained
# With this function i'm making sentences in the format
#     examples = [
#     ('Who is Shaka Khan?',
#      [(7, 17, 'PERSON')]),
#     ('I like London and Berlin.',
#      [(7, 13, 'LOC'), (18, 24, 'LOC')])
# ]

@plac.annotations(
    models_dir=('Path to a directory where spacy NER_models will be used for evaluation', 'option', 'm', str),
    input_file=('An input spacy binary file from which evaluation sentences are taken from', 'option', 'i', str)
)
def main(models_dir=None, input_file=None):
    """
    This script writes evaluation results only for the NER pipeline of the model.
    It takes a directory containing sub directiories of many Spacy models and saves the evaluation results inside the
    models directory.
    The binary input file is specified so the script know on which sentences to evaluate.
    """
    if not os.path.isdir(models_dir):
        print('Please specify a directory to spacy NER_models')
        raise SystemExit(1)
    if not os.path.isfile(input_file):
        print('Please specify an input file')
        raise SystemExit(1)
    evalSents = makingEvaluationSents(input_file)
    outputFile = os.path.join(models_dir, "Evaluation results.txt")
    sortedFiles = dict()
    for model in os.listdir(models_dir):
        spacy_model = spacy.load(os.path.join(models_dir, model))
        results = evaluate(spacy_model, evalSents)
        resultsStr = 'Model: %s\nResults:\n\tents_p:%s\n\tents_r:%s\n\tents_f:%s\n\tents_per_type:%s\n\n' % (
            model, results['ents_p'], results['ents_r'], results['ents_f'], results['ents_per_type'])
        b = model.split(' ')[0]
        sortedFiles[b] = resultsStr
        print("Evaluated %s" % model)
    # getting a sorted list so i can print the results in natural order
    sortedFileIdx = sorted(sortedFiles, key=int)
    with open(outputFile, mode='a', encoding='utf-8') as wf:
        for idx in sortedFileIdx:
            wf.write(sortedFiles[idx])


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
    # plac.call(main)
    """
    pravilno povikuvanje (go zachuvuva rezultatot vo models dir)
    python EvaluatingAModel -m "NER_models/general" -i "training_and_testing_data/deep_learning_model/testing.bin"
    ili
    python EvaluatingAModel -m "NER_models/specialized/activation funciton models" -i "training_and_testing_data/specialized_models/testing.bin"

    """
