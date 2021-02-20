import subprocess
import argparse
import sys
if __name__ == '__main__':
    # Convert sentences into training/testing set for training GENERAL NER
    """
    completed_process = subprocess.run([sys.executable, 'MakingDataIntoSpacyFormat/convertToTrainingDataDirectly.py',
                                         'corpora/annotated/AllSents - ischisteni nekoi entiteti.txt',
                                         'training_and_testing_data/deep_learning_model',
                                         '0.75'], capture_output=True, text=True)
"""
    #Train general NER
    ###
    #evaluate general NER
    # zemi ovde od stdout patekata ke ja dade na najdobriot model
    #Extract entity sentences from PDFs
    completed_process = subprocess.run([sys.executable, 'GettingEntitySents.py', '123'], capture_output=True, text=True)
    #annotate extracted sentences using WordSetAndMappings
    completed_process = subprocess.run([sys.executable, 'AnnotatingEntSents.py', 'EntitySents', 'corpora/annotated'], capture_output=True, text=True)
    # convert those annotations to training/testing set for SPECIALIZED NER
    completed_process = subprocess.run([sys.executable, 'MakingDataIntoSpacyFormat/convertTotrainingDataDirectly.py'
                                        'corpora/annotated/activation function model',
                                        "training_and_testing_data/specialized_models"], capture_output=True, text=True)
    completed_process = subprocess.run([sys.executable, 'MakingDataIntoSpacyFormat/convertTotrainingDataDirectly.py'
                                                        'corpora/annotated/architecture type model',
                                        "training_and_testing_data/specialized_models"], capture_output=True, text=True)
    completed_process = subprocess.run([sys.executable, 'MakingDataIntoSpacyFormat/convertTotrainingDataDirectly.py'
                                                        'corpora/annotated/building blocks model',
                                        "training_and_testing_data/specialized_models"], capture_output=True, text=True)

    # train SPECIALIZED NERs
    completed_process = subprocess.run([sys.executable, 'TrainingNERmodel.py',
                                        'en_core_web_sm',
                                        'new_model',
                                        '100',
                                        'training_and_testing_data/specialized_models/training_bins',
                                        'training_and_testing_data/specialized_models/testing_bins'], capture_output=True, text=True)
    # evaluate SPECIALIZED NERs
    #using MakingoutputVecotrs.py extract all the keywords from the PDFS

    # then run it again to extract all the needed output vectors

    #Reccomender system
