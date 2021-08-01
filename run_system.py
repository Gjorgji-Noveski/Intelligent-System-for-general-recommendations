import subprocess
import sys


def create_required_folders():
    import os
    if not os.path.exists('keywords'):
        os.makedirs('keywords')
    if not os.path.exists('entity_sents'):
        os.makedirs('entity_sents')
    if not os.path.exists('temp'):
        os.makedirs('temp')
    if not os.path.exists('trained_ner_models'):
        os.makedirs('trained_ner_models')
    if not os.path.exists('training_and_testing_data'):
        os.makedirs('training_and_testing_data')
    if not os.path.exists('final_vectors'):
        os.makedirs('final_vectors')


if __name__ == '__main__':
    create_required_folders()
    # Converting the optimal DL sentences to binary files, used in training/testing the general NER model
    print('Making binary files')
    completed_process = subprocess.run([sys.executable, 'convertToTrainTestData.py',
                                        'annotated_corpora/general_ner_model',
                                        'training_and_testing_data/general_ner_model',
                                        '0.75'], capture_output=True, text=True)
    print(f'Error output:{completed_process.stderr}\n')
    print(f'Standard output:{completed_process.stdout}\n')
    if len(completed_process.stderr) > 0:
        exit(1)
    # ---------------------------------------------------------------------- #

    # Training the general NER model
    print('Training general NER model')
    completed_process = subprocess.run([sys.executable, 'TrainingNERmodel.py',
                                        'en_core_web_sm',
                                        'new_model',
                                        '20',
                                        r'training_and_testing_data/general_ner_model/training_bins',
                                        r'trained_ner_models'], capture_output=True, text=True)
    print(f'Error output:{completed_process.stderr}\n')
    print(f'Standard output:{completed_process.stdout}\n')
    if len(completed_process.stderr) > 0:
        exit(1)
    # ---------------------------------------------------------------------- #

    # Evaluating the general NER model
    print('Evaluating general NER')
    completed_process = subprocess.run([sys.executable, 'EvaluatingAModel.py',
                                        r'trained_ner_models/general_ner_model',
                                        r'training_and_testing_data/general_ner_model/testing_bins/general_ner_model.bin'],
                                       capture_output=True, text=True)

    best_general_ner_model_path = completed_process.stdout.strip()
    print(f'Error output:{completed_process.stderr}\n')
    print(f'Standard output:{completed_process.stdout}\n')
    if len(completed_process.stderr) > 0:
        exit(1)
    # ---------------------------------------------------------------------- #

    # Using the best performing general NER model to extract sentences that contain named entities (field of DL)
    print('Extracting sentences containing names entities')
    completed_process = subprocess.run(
        [sys.executable, 'GettingEntitySents.py', best_general_ner_model_path, r'research_papers', 'entity_sents'],
        capture_output=True, text=True)
    print(f'Error output:{completed_process.stderr}\n')
    print(f'Standard output:{completed_process.stdout}\n')
    if len(completed_process.stderr) > 0:
        exit(1)
    # ---------------------------------------------------------------------- #

    # Annotate the sentences
    print('Annotating sentences')
    completed_process = subprocess.run([sys.executable, 'AnnotatingEntSents.py', 'entity_sents', 'annotated_corpora'],
                                       capture_output=True, text=True)
    print(f'Error output:{completed_process.stderr}\n')
    print(f'Standard output:{completed_process.stdout}\n')
    if len(completed_process.stderr) > 0:
        exit(1)
    # ---------------------------------------------------------------------- #

    # Use the annotated sentences for making binary files for training/testing the specialized NER models
    print('Making binary files, activation function model')
    completed_process = subprocess.run([sys.executable, r'convertToTrainTestData.py',
                                        r'annotated_corpora/activation function model',
                                        r"training_and_testing_data/specialized_ner_models",
                                        '0.75'], capture_output=True, text=True)
    print(f'Error output:{completed_process.stderr}\n')
    print(f'Standard output:{completed_process.stdout}\n')
    if len(completed_process.stderr) > 0:
        exit(1)
    print('Making binary files, architecture type model')
    completed_process = subprocess.run([sys.executable, r'convertToTrainTestData.py',
                                        r'annotated_corpora/architecture type model',
                                        r"training_and_testing_data/specialized_ner_models",
                                        '0.75'], capture_output=True, text=True)
    print(f'Error output:{completed_process.stderr}\n')
    print(f'Standard output:{completed_process.stdout}\n')
    if len(completed_process.stderr) > 0:
        exit(1)
    print('Making binary files, building blocks model')
    completed_process = subprocess.run([sys.executable, r'convertToTrainTestData.py',
                                        r'annotated_corpora/building blocks model',
                                        r"training_and_testing_data/specialized_ner_models",
                                        '0.75'], capture_output=True, text=True)
    print(f'Error output:{completed_process.stderr}\n')
    print(f'Standard output:{completed_process.stdout}\n')
    if len(completed_process.stderr) > 0:
        exit(1)
    # ---------------------------------------------------------------------- #

    # train SPECIALIZED NERs
    print('Training specialized NER models')
    completed_process = subprocess.run([sys.executable, 'TrainingNERmodel.py',
                                        'en_core_web_sm',
                                        'new_model',
                                        '20',
                                        r'training_and_testing_data/specialized_ner_models/training_bins',
                                        r'trained_ner_models/specialized'], capture_output=True, text=True)
    print(f'Error output:{completed_process.stderr}\n')
    print(f'Standard output:{completed_process.stdout}\n')
    if len(completed_process.stderr) > 0:
        exit(1)
    # ---------------------------------------------------------------------- #

    # evaluate specialized NER models
    print('Evaluating specialized NER models')
    completed_process = subprocess.run([sys.executable, 'EvaluatingAModel.py',
                                        r'trained_ner_models/specialized/activation function model',
                                        r'training_and_testing_data/specialized_ner_models/testing_bins/activation function model.bin'],
                                       capture_output=True, text=True)

    best_act_model_path = completed_process.stdout.strip()
    print(f'Error output:{completed_process.stderr}\n')
    print(f'Standard output:{completed_process.stdout}\n')
    if len(completed_process.stderr) > 0:
        exit(1)
    completed_process = subprocess.run([sys.executable, 'EvaluatingAModel.py',
                                        'trained_ner_models/specialized/architecture type model',
                                        'training_and_testing_data/specialized_ner_models/testing_bins/architecture type model.bin'],
                                       capture_output=True, text=True)
    best_arch_model_path = completed_process.stdout.strip()

    print(f'Error output:{completed_process.stderr}\n')
    print(f'Standard output:{completed_process.stdout}\n')
    if len(completed_process.stderr) > 0:
        exit(1)
    completed_process = subprocess.run([sys.executable, 'EvaluatingAModel.py',
                                        r'trained_ner_models/specialized/building blocks model',
                                        r'training_and_testing_data/specialized_ner_models/testing_bins/building blocks model.bin'],
                                       capture_output=True, text=True)

    best_build_model_path = completed_process.stdout.strip()
    print(f'Error output:{completed_process.stderr}\n')
    print(f'Standard output:{completed_process.stdout}\n')
    if len(completed_process.stderr) > 0:
        exit(1)
    # ---------------------------------------------------------------------- #

    # using MakingoutputVecotrs.py extract all the keywords from the PDFS
    print('Creating database for recommender system')
    completed_process = subprocess.run([sys.executable, 'MakingOutputVectors.py',
                                        r'research_papers',
                                        r'keywords',
                                        best_arch_model_path,
                                        best_act_model_path,
                                        best_build_model_path])

    print(f'Error output:{completed_process.stderr}\n')
    print(f'Standard output:{completed_process.stdout}\n')
