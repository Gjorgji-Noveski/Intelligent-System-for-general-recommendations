# Database creation pipeline for creating an intelligent system for general recommendations
## The what
This repository provides code that creates a database which is used in creating an
**intelligent system for general recommendations of deep learning architectures and 
hyperparameters**.

The system, in which a user only has to provide keywords that represent the problem domain,
can provide a general recommendation of which deep learning architecture
type, which activation function and which building blocks should be used to create 
a well performing machine learning model.

This code is only for the database creation pipeline and not the creation of the 
intelligent system.

## The how
The whole proccess consists of several steps, which are:
- **Choosing optimal sentences**: This means sentences from various research papers
  are collected and annotated manually with named entities from the field of deep learning,
  ex: CNN, hyperparameters, accuracy, input data, early stopping, neurons, etc. The sentences are
  already provided here.
- **Training a "general" NER model**: A NER model called the "general" NER model is trained
and saved on each epoch that seeks to extract the named entities supplied from the previous optimal sentences.
- **Evaluating the "general" NER model**: The model is evaluated for each epoch and the best performing
one based on f1-score, is returned.
- **Extracting named entities**: The "general" NER model is run on a corpus of scientific papers
and from each paper sentences which contain the "general" deep learning entiteis are saved.
- **Annotating sentences**: The sentences are annotated according to certain words that can
be found in WordSetAndMappings.py. These annotated sentences will be used to train three
separate NER models, called "specialized" NER models.
- **Training "specialized" NER  models**: These three NER models are trained to capture
the deep learning architecture types, activation functions and building blocks used in a research paper.
- **Evaluating "specialized" NER models**: Just as before, each epoch of each model is evaluated
and each corresponding best performing model is returned.
- **Extracting keywords**: Each scientific paper is processed in order to find keywords from
it's "Keywords" section, if it has any. This is done in order to build a binary encoded vector
for each paper in which the features will represent all the distinct keywords and the values represent
if that keyword is present in the paper or not.
- **Extracting named entities**: Finally, each "specialized" NER model is run on the whole
corpus, and when it finds a named entity it builds a similar binary encoded vector representing
the found named entities.
  
In the end, we have 4 sets of binary encoded vectors, one representing the presence of keywords
in the research paper(input, X), others for the architecture type, activation functions and building blocks
used in the paper(output, Y). This input and output will be used by the intelligent system
in order to give good recommendations.

```
                   physics, markov chain, electricity, NLP ...
Keywords vector = [   0   ,       1     ,      0     ,  1  ...]



                            feed forward,   CNN,  LSTM,  SVM  ...
Architecture type vector = [      0     ,    0 ,    0 ,   1   ...]

                              Softmax,  ReLU,  GeLU,  Sigmoid ...
Activation function vector = [   0   ,    1 ,    0 ,      1   ...]

                         Recurrent layer,  pooling layer, dropout layer, fully connected layer ...
Building blocks vector = [        0     ,         1     ,        0     ,            1          ...]
```
The whole list of entities for these models can be found in the **WordSetAndMappings.py** script.

## The why
The benefit of this pipeline is that by only supplying different starting sentences
and annotations, it is able to train NER models for other problem domains instead of the
default, deep learning entities.

Furthermore, it deals with preprocessing the PDF text, since extracting text from PDF
is not perfect, various titles, page numbers, picture annotations are returned as part of 
the text, which corrupt the meaning of nearby sentences. The pipeline aims to filter this
as much as possible in order to retain the original meaning of the sentences, so the NER models
will perform better.

 ## Folder explanations
- research_papers - > Folder containing subfolders of research paper categories. For instance, it
  may contain 3 folders named, Medicine, Physics, Bioinformatics, and inside each of these folders will
  be the corresponding scientific papers for that given category. Some scientific papers are already provided
  to be used as an example.
  
- training_and_testing_data - > Contains binary files that will be used to train and evaluate the NER models.
These binary files are created using the convertToTrainTestData.py script.
  
- trained_ner_models - > The trained NER models are stored here for every epoch, alongside with the evaluation
results in a .csv format, when EvaluatingAModel.py is executed.
  
- entity_sents - > Contains the sentences extracted using the NER models, which have named entities in them
  from each scientific paper (unannotated). The sentences may appear to not contain the named entities that
  were supplied during training since no NER model is 100% accurate.
  
- annotated_corpora - > contains .txt files of every research paper with sentences that have named
  entities that are annotated for their respectful NER model and will be converted to a binary file
  in order to train the NER model.
  
- Datasets - > folder given for convenience containing each of the binary encoded vectors for each model
  after they were run on a corpus of 19,868 scientific papers.

- final_vectors - > folder where the final binary encoded vectors will be stored.
  
- keywords - > contains .txt files that contain all the found keywords from the category of scientific papers.
  The name of the .txt file will correspond to the name of the category from the research_papers folder.
  
- temp - > used for storing an intermediate result, that is the first page of every research paper.
The result is used for extracting the title of the scientific paper.

## Requirements
To install the dependencies, please run:
`pip install -r requirements.txt`
After that to have the starting spacy model for fine-tuning, install it by
`python -m spacy download en_core_web_sm`
  
Improvements are wholeheartedly welcomed. If you think something can be improved, drop a pull request.
