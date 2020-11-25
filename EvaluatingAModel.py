import spacy
from spacy.gold import GoldParse
from spacy.scorer import Scorer
import logging
import os.path


# TODO: Careful NOT to evaluate a model on the SAME sentences it was trained
# With this function i'm making sentences in the format
#     examples = [
#     ('Who is Shaka Khan?',
#      [(7, 17, 'PERSON')]),
#     ('I like London and Berlin.',
#      [(7, 13, 'LOC'), (18, 24, 'LOC')])
# ]
# so i can get NER precision/recall/fscore of the model using the Scorer.score function

def makingEvaluationSents(input_path, unknown_label):
    allLines = []
    try:
        f = open(input_path, 'r')  # input file
        data_dict = {}
        annotations = []
        label_dict = {}
        s = ''
        start = 0
        for line in f:
            # if its NOT the end of the sentence
            if line[0:len(line) - 1] != '.\tO':
                word, entity = line.split('\t')
                s += word + " "
                entity = entity[:len(entity) - 1]
                if entity != unknown_label:
                    if len(entity) != 1:
                        d = {}
                        d['text'] = word
                        d['start'] = start
                        d['end'] = start + len(word) - 1
                        try:
                            label_dict[entity].append(d)
                        except:
                            label_dict[entity] = []
                            label_dict[entity].append(d)
                start += len(word) + 1


            else:
                data_dict['content'] = s
                content = s
                s = ''
                label_list = []
                for ents in list(label_dict.keys()):
                    for i in range(len(label_dict[ents])):
                        if (label_dict[ents][i]['text'] != ''):
                            l = [ents, label_dict[ents][i]]
                            for j in range(i + 1, len(label_dict[ents])):
                                if (label_dict[ents][i]['text'] == label_dict[ents][j]['text']):
                                    di = {}
                                    di['start'] = label_dict[ents][j]['start']
                                    di['end'] = label_dict[ents][j]['end']
                                    di['text'] = label_dict[ents][i]['text']
                                    l.append(di)
                                    label_dict[ents][j]['text'] = ''
                            label_list.append(l)

                for entities in label_list:
                    label = {}
                    label['label'] = [entities[0]]
                    label['points'] = entities[1:]

                    annotations.append(label)
                # ('I like London and Berlin.',
                #      [(7, 13, 'LOC'), (18, 24, 'LOC')])
                data_dict['annotation'] = annotations
                THEREALstartlistendlist = []
                for tmp in data_dict['annotation']:
                    ent = tmp['label'][0]
                    startEndList = []
                    for lblDic in tmp['points']:
                        THESTART = lblDic['start']
                        THEEND = lblDic['end'] + 1
                        startEndList.append((THESTART, THEEND, ent))
                    THEREALstartlistendlist.extend(startEndList)
                allLines.append((content, THEREALstartlistendlist))

                annotations = []
                data_dict = {}
                start = 0
                label_dict = {}
        # print(allLines)
        return allLines
    except Exception as e:
        logging.exception("Unable to process file" + "\n" + "error = " + str(e))
        return None


evalSents = makingEvaluationSents(
    "C:/Users/Gjorgji Noveski/Desktop/Files for my Spacy work/Files for evaluating a model/new sentences, after sentence 850+.tsv",
    'abc')


def evaluate(ner_model, examples):
    scorer = Scorer()
    for input_, annot in examples:
        doc_gold_text = ner_model.make_doc(input_)
        gold = GoldParse(doc_gold_text, entities=annot)
        pred_value = ner_model(input_)
        scorer.score(pred_value, gold)
    return scorer.scores


def writeResults():
    pass


for i in range(1, 101):
    model_path = "C:/Users/Gjorgji Noveski/Desktop/Files for my Spacy work/NLP models and bin training data/Incremental epochs models, 850 sents, with decaying dropout(0.6,0.35,0.00009) batch_compouding(32,128,1.001)/" + str(i) + " epochs on 850 sents"
    print(model_path)
    nlp = spacy.load(model_path)
    results = evaluate(nlp, evalSents)
    with open(
            "C:/Users/Gjorgji Noveski/Desktop/Files for my Spacy work/NLP models and bin training data/Incremental epochs models, 850 sents, with decaying dropout(0.6,0.35,0.00009) batch_compouding(32,128,1.001)/Evaluation data.txt",
            mode='a', encoding='UTF-8')as wf:
        modelStr = 'Model: %s\n' % os.path.basename(model_path)
        trainingDataStr = 'Trained on: 850 sents, no dropout decay, tagger and parser NOT saved\n'
        resultsStr = 'Results:\n\t ents_p:%s\n\tents_r:%s\n\tents_f:%s\n\tents_per_type:%s\n\n' % (
            results['ents_p'], results['ents_r'], results['ents_f'], results['ents_per_type'])
        wf.write(modelStr+trainingDataStr+resultsStr)
        print("WROTE")