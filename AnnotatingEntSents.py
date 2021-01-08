import os
import re
EXTRACTED_ENT_SENTS_PATH = r'C:\Users\Gjorgji Noveski\Desktop\Files for my Spacy work\Extracted Entity Sents, cleaned fig,Table,et al'
ANNOTATED_ENT_SENTS_PATH = r'C:\Users\Gjorgji Noveski\Desktop\Files for my Spacy work\Annotated dataset for different NER models'


"""
Probaj namesto site variacii na auto encoder, samo autoencoder da anotirash, deka ako zborot e variational auto encoder, a bara za auto encoder, toj ednash ke go anotira so auto encoder, a posle koga ke bara za variational pak za nego ke go anotira.
Mozhno da se desi i slednovo:
bla bla [Variational [auto encoder]] bla bla
i da vide vaka anotirano.
Mozhe samo da barame za auto encoder pa posle da izvlecheme ako zborot pred nego e denoising, variational itn.
istoto mozhe i za neural network da bide, primer samo neural network da barame i posle da izvlecheme i za boltzman machine

Broj na sloevi od sekoj gradben blok ke se dobie so proverka na Building_blocks za sekoj otkrien entitet, ke proveri pred nego sto brojka sedi ako voopshto sedi
"""
DATASET = ['number', 'subjects', 'dataset', 'patients', 'images', 'analyzed', 'downloaded', 'retrieved', 'created', 'corpus', 'corpora', 'files']
ARCHITECTURE_TYPE = ['perceptron', 'feed forward', 'radial basis network', 'recurrent neural network', 'long short-term memory', 'long short term memory', 'long-short term memory', 'long shortterm memory', 'gated recurrent unit', 'auto encoder', 'markov chain', 'hopfield network', 'boltzman machine', 'deep belief network', 'convolutional neural network', 'deconvolutional neural network', 'convolutional inverse graphics network', 'probabilistic neural network', 'generative adversarial network', 'liquid state machine', 'extreme learning machine', 'echo state network', 'deep residual network', 'kohonen network', 'support vector machine', 'neural turing machine', 'rnn', 'lstm', 'gru', 'rbm', 'gan', 'lsm', 'elm', 'esn', 'drn', 'svm', 'ntm']
ACTIVATION_FUNC = ['linear activation function', 'rectified linear unit', 'sigmoid', 'gaussian error linear unit', 'softmax', 'hyperbolic tangent function', 'softsign function', 'exponential linear unit', 'leaky rectified linear unit', 'relu', 'gelu', 'tanh', 'elu', 'lrelu', 'leaky relu']
BUILDING_BLOCKS = ['fully connected layer', 'fully-connected layer', 'recurrent layer', 'pooling layer', 'convolutional layer', 'convolution layer', 'deconvolutional layer', 'deconvolution layer', 'dropout layer', 'softmax layer', 'subsampling layer', 'gru layer']
CATEGORIES = {'dataset model': DATASET, 'architecture type model': ARCHITECTURE_TYPE, 'activation function model': ACTIVATION_FUNC, 'building blocks model': BUILDING_BLOCKS}

"""
Annotates all the corpora and saves them in their dedicated folder (based on entity category, a.k.a model)
"""
def annotateByCategory(inputPath, outputPath):
    global CATEGORIES
    for file in os.listdir(inputPath):
        with open(os.path.abspath(os.path.join(inputPath,file)), mode='r', encoding='utf-8') as entSentFile:
            allLines = entSentFile.readlines()
        for category in CATEGORIES.keys():
            annotatedCategoryPath = os.path.join(outputPath, category)
            annotatedFile = os.path.join(annotatedCategoryPath, file)
            if not os.path.exists(annotatedCategoryPath):
                os.makedirs(annotatedCategoryPath)
            sentences = set()
            for line in allLines:
                line = line.replace('{', '').replace('}', '')
                # Extracting only the sentences that i managed to annotate
                annotatedAnEntity = False
                for entity in CATEGORIES[category]:
                    regex = r'(?<=\()' + entity + r's?(?=\))|\s' + entity + r's?\s'

                    # Using regex to search for singular and plural of entities and if they also appear in '( )' brackets.
                    matchObjIter = re.finditer(regex, line, flags=re.IGNORECASE)
                    for counter, match in enumerate(matchObjIter):
                        annotatedAnEntity = True

                        # using counter so i can annotate more than 1 entity in one sentence, without it the array positions won't be correct for the 2nd annotation
                        line = line[:match.start()+(2*counter)] + '{' + match.group() + '}' + line[match.end()+(2*counter):]
                if annotatedAnEntity:
                    sentences.add(line)
            with open(annotatedFile, encoding='utf-8', mode='a')as fw:
                fw.writelines(sentences)
            print("Extracted " + category + ' - ' + file)


annotateByCategory(EXTRACTED_ENT_SENTS_PATH, ANNOTATED_ENT_SENTS_PATH)