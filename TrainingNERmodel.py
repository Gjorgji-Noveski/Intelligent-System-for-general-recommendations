#!/usr/bin/env python
# coding: utf8
# Training additional entity types using spaCy
from __future__ import unicode_literals, print_function
import pickle
import plac
import random
import os.path
import spacy
from pathlib import Path
from spacy.util import minibatch, compounding
from spacy.util import decaying
# correct spacy version needs to be installed and cuda[on your own]
# spacy.require_gpu()

@plac.annotations(
    model=("Model name. Defaults to blank 'en' model.", "positional"),
    new_model_name=("New model name for model meta.", "positional"),
    n_iter=("Number of training iterations", "positional", None, int),
    input_binaries_dir=('Input directory where all the binary training files are.', 'positional'),
    output_models_dir=("Output directory where all the trained NER models will be for each entity category.", "positional"))
def main(model=None, new_model_name='new_model', n_iter=100, input_binaries_dir=None, output_models_dir=None, ):
    """
    This script gets as input a directory containing training data for the Spacy NER pipeline (input_binaries_dir).
    The training data must be in the correct format, as such:

    TRAIN_DATA = [
    ("Who is Shaka Khan?", {"entities": [(7, 17, "PERSON")]}),
    ("I like London and Berlin.", {"entities": [(7, 13, "LOC"), (18, 24, "LOC")]}),
    ]

    The output_models_dir parameter specifies where each epoch the trained model is saved to disk so it can be used for
    evaluation.
    """
    if output_models_dir is None:
        print('Output directory not specified.')
        raise SystemExit(1)
    if input_binaries_dir is None:
        print('Input directory with binary training data not specified.')
        raise SystemExit(1)
    if not os.path.exists(output_models_dir):
        os.makedirs(output_models_dir)
    for file in os.listdir(input_binaries_dir):
        with open(os.path.join(input_binaries_dir, file), 'rb') as f:
            TRAIN_DATA = pickle.load(f)
        categoryOutputDir = os.path.join(output_models_dir, file.split('.')[0])
        print(categoryOutputDir)
        if not os.path.exists(categoryOutputDir):
            os.makedirs(categoryOutputDir)
        trainSingleModel(model, new_model_name, categoryOutputDir, n_iter, TRAIN_DATA)


def trainSingleModel(model, new_model_name, output_dir, n_iter, train_data):
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

    # add labels
    for _, annotations in train_data:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    if model is None:
        optimizer = nlp.begin_training()
    else:
        optimizer = nlp.resume_training()

    # Get names of other pipes to disable them during training to train only NER
    pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]
    dropout = decaying(0.3, 0.25, 0.00003)

    for itn in range(1, n_iter + 1):
        disabled = nlp.disable_pipes(*other_pipes)  # only train NER

        random.shuffle(train_data)
        losses = {}
        batches = minibatch(train_data, size=compounding(32, 128, 1.001))
        for batch in batches:
            texts, annotations = zip(*batch)
            nlp.update(texts, annotations, sgd=optimizer, drop=next(dropout),
                       losses=losses)
        print('Losses', losses)

        # Save model
        file_name = '%s epochs' % itn
        if output_dir is not None:
            output_dir = Path(output_dir)
            if not output_dir.exists():
                output_dir.mkdir()
            nlp.meta['name'] = new_model_name  # rename model
            final_file_path = os.path.join(output_dir, file_name)
            disabled.restore()
            nlp.to_disk(final_file_path)
            # print("Saved model to", final_file_path, '\n')


if __name__ == '__main__':
    plac.call(main)
