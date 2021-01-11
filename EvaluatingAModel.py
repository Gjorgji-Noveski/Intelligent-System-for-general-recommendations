from spacy.gold import GoldParse
from spacy.scorer import Scorer
import os.path
import pickle
import plac

# TODO: Careful NOT to evaluate a model on the SAME sentences it was trained
# With this function i'm making sentences in the format
#     examples = [
#     ('Who is Shaka Khan?',
#      [(7, 17, 'PERSON')]),
#     ('I like London and Berlin.',
#      [(7, 13, 'LOC'), (18, 24, 'LOC')])
# ]
# so i can get NER precision/recall/fscore of the model using the Scorer.score function

"""
This script writes evaluation results only for the entity recognizer
"""


@plac.annotations(
    models_dir=('Path to a directory where spacy models will be used for evaluation', 'option', 'm', str),
    input_file=('An input spacy binary file from which evaluation sentences are taken from', 'option', 'i', str),
    output_dir=(
    "Output directory where a .txt file containing entity evaluation results will be written", "option", "o", str))
def main(models_dir=None, input_file=None, output_dir=None):
    if not os.path.isdir(models_dir):
        print('Please specify a directory to spacy models')
        raise SystemExit(1)
    if not os.path.isfile(input_file):
        print('Please specify an input file')
        raise SystemExit(1)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    evalSents = makingEvaluationSents(input_file)
    outputFile = os.path.join(output_dir, "Evaluation results.txt")
    with open(outputFile, mode='a', encoding='utf-8') as wf:
        for model in models_dir:
            results = evaluate(os.path.join(models_dir, model), evalSents)
            resultsStr = 'Model: %s\nResults:\n\tents_p:%s\n\tents_r:%s\n\tents_f:%s\n\tents_per_type:%s\n\n' % (
                    model, results['ents_p'], results['ents_r'], results['ents_f'], results['ents_per_type'])
            wf.write(resultsStr)
            print("Evaluated %s" % model)


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