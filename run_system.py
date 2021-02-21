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
    # completed_process = subprocess.run([sys.executable, 'EvaluatingAModel.py',
    #                                     r'NEWNERmodels/general',
    #                                     r'training_and_testing_data/deep_learning_model/testing_bins/deep learning model.bin'],
    #                                    capture_output=True, text=True)
    #Extract entity sentences from PDFs
    #completed_process = subprocess.run([sys.executable, 'GettingEntitySents.py', '123'], capture_output=True, text=True)
    #annotate extracted sentences using WordSetAndMappings
    #print('Annotating sentences for spacialized NER')
    #completed_process = subprocess.run([sys.executable, 'AnnotatingEntSents.py', 'EntitySents', 'corpora/annotated'], capture_output=True, text=True)
    # convert those annotations to training/testing set for SPECIALIZED NER
    """
    print('Converting to train/test for specialized NER')
    completed_process = subprocess.run([sys.executable, r'MakingDataIntoSpacyFormat/convertToTrainingDataDirectly.py',
                                        r'corpora/annotated/activation function model',
                                        r"training_and_testing_data/specialized_models",
                                        '0.75'], capture_output=True, text=True)
    print(completed_process.stdout)
    print(completed_process.stderr)


    completed_process = subprocess.run([sys.executable, r'MakingDataIntoSpacyFormat/convertToTrainingDataDirectly.py',
                                                        r'corpora/annotated/architecture type model',
                                        r"training_and_testing_data/specialized_models",
                                        '0.75'], capture_output=True, text=True)
    print(completed_process.stdout)
    print(completed_process.stderr)
    completed_process = subprocess.run([sys.executable, r'MakingDataIntoSpacyFormat/convertToTrainingDataDirectly.py',
                                                        r'corpora/annotated/building blocks model',
                                        r"training_and_testing_data/specialized_models",
                                        '0.75'], capture_output=True, text=True)
    print(completed_process.stdout)
    print(completed_process.stderr)
    
    print('Training Ner models')
    # train SPECIALIZED NERs
    completed_process = subprocess.run([sys.executable, 'TrainingNERmodel.py',
                                        'en_core_web_sm',
                                        'new_model',
                                        '100',
                                        r'training_and_testing_data/specialized_models/training_bins',
                                        r'NEWNERmodels/specialized'], capture_output=True, text=True)
    print(completed_process.stdout)
    print(completed_process.stderr)
    # evaluate SPECIALIZED NERs
    completed_process = subprocess.run([sys.executable, 'EvaluatingAModel.py',
                                        r'NEWNERmodels/specialized/activation function model',
                                        r'training_and_testing_data/specialized_models/testing_bins/activation function model.bin'],
                                       capture_output=True, text=True)
    print(completed_process.stdout)
    print(completed_process.stderr)
    best_act_model_path = completed_process.stdout.strip()
    completed_process = subprocess.run([sys.executable, 'EvaluatingAModel.py',
                                        'NEWNERmodels/specialized/architecture type model',
                                        'training_and_testing_data/specialized_models/testing_bins/architecture type model.bin'],
                                       capture_output=True, text=True)
    print(completed_process.stdout)
    print(completed_process.stderr)
    best_arch_model_path = completed_process.stdout.strip()
    completed_process = subprocess.run([sys.executable, 'EvaluatingAModel.py',
                                        r'NEWNERmodels/specialized/building blocks model',
                                        r'training_and_testing_data/specialized_models/testing_bins/building blocks model.bin'],
                                       capture_output=True, text=True)
    print(completed_process.stdout)
    print(completed_process.stderr)
    best_build_model_path = completed_process.stdout.strip()
    """

    best_arch_model_path = r'C:\\Users\\Gjorgji Noveski\\PycharmProjects\\PDFtoDatabase\\NEWNERmodels\\specialized\\architecture type model\\88 epochs'
    best_act_model_path = r'C:\\Users\\Gjorgji Noveski\\PycharmProjects\\PDFtoDatabase\\NEWNERmodels\\specialized\\activation function model\\95 epochs'
    best_build_model_path = r'C:\\Users\\Gjorgji Noveski\\PycharmProjects\\PDFtoDatabase\\NEWNERmodels\\specialized\\building blocks model\\93 epochs'
    #using MakingoutputVecotrs.py extract all the keywords from the PDFS
    print('started')
    completed_process = subprocess.run([sys.executable, 'MakingOutputVectors.py',
                                        r'C:\Users\Gjorgji Noveski\PycharmProjects\SciBooksCrawler\SciBooks\Downloaded PDFs VtorPat',
                                        r'NEWkeywords',
                                        best_arch_model_path,
                                        best_act_model_path,
                                        best_build_model_path])
    print('finish, baraj vo NEWKeywords i vo NEWoutput')

    print(completed_process.stdout)
    print(completed_process.stderr)

    #Reccomender system
