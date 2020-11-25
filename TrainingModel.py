#!/usr/bin/env python
# coding: utf8
# Training additional entity types using spaCy
from __future__ import unicode_literals, print_function
import pickle
import plac
import random
from pathlib import Path
import spacy
from spacy.util import minibatch, compounding
import os.path
from spacy.util import decaying
spacy.require_gpu()
# New entity labels
# Specify the new entity labels which you want to add here
LABEL = ['B-DeepLearning', 'I-DeepLearning', 'O']
# Loading training data
with open(
        'C:/Users/Gjorgji Noveski/Desktop/Files for my Spacy work/NLP models and bin training data/850sentsTrainingData.bin',
        'rb') as fp:
    TRAIN_DATA = pickle.load(fp)


# TODO: Treniraj so pomalce epohi, 20ish, i treniraj i pos pipeline
# TODO: Namesti decaying dropout rate, deka za mali mnozhestva taka trebalo
TRAIN_SENTS_AMOUNT = 850

@plac.annotations(
    model=("Model name. Defaults to blank 'en' model.", "option", "m", str),
    new_model_name=("New model name for model meta.", "option", "nm", str),
    output_dir=("Optional output directory", "option", "o", Path),
    n_iter=("Number of training iterations", "option", "n", int))

def main(model=None, new_model_name='new_model', output_dir=None, n_iter=10):
    """Setting up the pipeline and entity recognizer, and training the new entity."""
    if model is not None:
        nlp = spacy.load(model)  # load existing spacy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank('en')  # create blank Language class
        print("Created blank 'en' model")
    if 'ner' not in nlp.pipe_names:
        ner = nlp.create_pipe('ner')
        nlp.add_pipe(ner)
    else:
        ner = nlp.get_pipe('ner')

    for i in LABEL:
        ner.add_label(i)  # Add new entity labels to entity recognizer

    if model is None:
        optimizer = nlp.begin_training()
    else:
        optimizer = nlp.resume_training()

    # Get names of other pipes to disable them during training to train only NER
    pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]
    dropout = decaying(0.6, 0.35, 0.00009)
    with nlp.disable_pipes(*other_pipes):  # only train NER

        for itn in range(1, n_iter+1):
            p = 0
            random.shuffle(TRAIN_DATA)
            losses = {}
            batches = minibatch(TRAIN_DATA, size=compounding(32., 128., 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                p = next(dropout)
                nlp.update(texts, annotations, sgd=optimizer, drop=p,
                           losses=losses)
            print('Losses', losses)

            # Save model
            file_name = '%s epochs on %s sents' % (itn, TRAIN_SENTS_AMOUNT)
            if output_dir is not None:
                output_dir = Path(output_dir)
                if not output_dir.exists():
                    output_dir.mkdir()
                nlp.meta['name'] = new_model_name  # rename model
                final_file_path = os.path.join(output_dir, file_name)
                nlp.to_disk(final_file_path)
                print("Saved model to", final_file_path,'\n')
                print("Dropout after this epoch %s" % p)



if __name__ == '__main__':
    plac.call(main)
