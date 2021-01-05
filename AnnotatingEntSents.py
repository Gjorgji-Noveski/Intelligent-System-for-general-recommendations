import os
EXTRACTED_ENT_SENTS_PATH = r'C:\Users\Gjorgji Noveski\Desktop\Files for my Spacy work\Extracted Entity Sents, cleaned fig,Table,et al'
ANNOTATED_ENT_SENTS_PATH = r'C:\Users\Gjorgji Noveski\Desktop\Files for my Spacy work\Annotated dataset for different NER models,NO DUPLI'
import re
"""
Probaj namesto site variacii na auto encoder, samo autoencoder da anotirash, deka ako zborot e variational auto encoder, a bara za auto encoder, toj ednash ke go anotira so auto encoder, a posle koga ke bara za variational pak za nego ke go anotira.
Mozhno da se desi i slednovo:
bla bla [Variational [auto encoder]] bla bla
i da vide vaka anotirano.
Mozhe samo da barame za auto encoder pa posle da izvlecheme ako zborot pred nego e denoising, variational itn.
istoto mozhe i za neural network da bide, primer samo neural network da barame i posle da izvlecheme 
"""
DATASET = ['number', 'subjects', 'dataset', 'patients', 'images', 'analyzed', 'downloaded', 'retrieved', 'created', 'corpus', 'files']
ARCHITECTURE_TYPE = ['perceptron', 'feed forward', 'radial basis network', 'recurrent neural network', 'long short-term memory', 'gated recurrent unit', 'auto encoder', 'markov chain', 'hopfield network', 'boltzman machine', 'restricted boltzman machine', 'deep belief network', 'convolutional neural network', 'deconvolutional neural network', 'convolutional inverse graphics network', 'probabilistic neural network', 'generative adversarial network', 'liquid state machine', 'extreme learning machine', 'echo state network', 'deep residual network', 'kohonen network', 'support vector machine', 'neural turing machine', 'rnn', 'lstm', 'gru', 'rbm', 'gan', 'lsm', 'elm', 'esn', 'drn', 'svm', 'ntm']
ACTIVATION_FUNC = ['linear activation function', 'rectified linear unit', 'sigmoid', 'gaussian error linear units', 'softmax', 'hyperbolic tangent function', 'softsign function', 'exponential linear unit', 'linear activation function', 'leaky rectified linear unit', 'relu', 'gelu', 'tanh', 'elu', 'lrelu', 'leaky relu']
BUILDING_BLOCKS = ['fully connected layer', 'fully-connected layer', 'recurrent layer', 'pooling layer', 'convolutional layer', 'convolution layer', 'deconvolutional layer', 'deconvolution layer', 'dropout layer', 'softmax layer', 'subsampling layer', 'gru layer']
CATEGORIES = {'dataset model': DATASET, 'architecture type model': ARCHITECTURE_TYPE, 'activation function model': ACTIVATION_FUNC, 'building blocks model': BUILDING_BLOCKS}
#######################
# Prvichno odime so ideja, na sekoja linija deka mozhe da ima povekje od 1 entitet

# PUSHTI GETTING ENTITY SENTS PAK, ZAFRKANV EDEN IZBRISHAV MOZHNO DA E POREMETEN EDEN FAJL RADI APPEND

# matchnuvame 'rnn' no ne i '(rnn)' da napravime nekako da se gleda word boundary da e empty space I '( )'

# isto taka proveruvaj koga ke gi anotirash rechenicite da ne ima duplikati, za da ne dojdesh do nebalansiram dataset za spacy modelite

# TODO: proveri koga pravis BIO scheme dali stava tocka na kraj od rechenicata sam, i dali ako najde tocka ja smeta za tocka, deka mozhe da najde tocka i da ne e kraj na rechenicata.
# TODO: proveri koga pravis BIO scheme dali stava tocka na kraj od rechenicata sam, i dali ako najde tocka ja smeta za tocka, deka mozhe da najde tocka i da ne e kraj na rechenicata.
# TODO: vidi dali match.group() ke ti dade dali matchnale za number ili numbers da mozhes pravilno da go anotirash ako e mnozhina
# TODO: Pushti sve od pochetok, zafrkna neshto, i GettingEntitySents.py i ova pushti go
#######################

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
                with open(annotatedFile, encoding='utf-8', mode='a')as fw:
                    sentences = set()
                    for line in allLines:
                        line = line.replace('{', '').replace('}', '').lower()
                        # Extracting only the sentences that i managed to annotate
                        annotatedAnEntity = False
                        for entity in CATEGORIES[category]:
                            regex = r'(?<=\()' + entity + r's?(?=\))|\b' + entity + r's?' + r'\b'

                            # Using regex to search for singular and plural of entities and if they also appear in '( )' brackets.
                            matchObjIter = re.finditer(regex, line)
                            for counter, match in enumerate(matchObjIter):
                                annotatedAnEntity = True

                                # PROBLEMOT e vo match.start()/end(), deka koga endash ke anotira, drugiot match()/end() broevi si ostanuvaat isti i zatoa losho ja seche rechenicata
                                line = line[:match.start()+(2*counter)] + '{' + match.group() + '}' + line[match.end()+(2*counter):]
                        if annotatedAnEntity:
                            sentences.add(line)
                    fw.writelines(sentences)
                print("Extracted " + category + ' - ' + file)



annotateByCategory(EXTRACTED_ENT_SENTS_PATH,ANNOTATED_ENT_SENTS_PATH)