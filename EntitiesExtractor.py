import re
import plac
import os

# This is a convenience script. It is not used in the database creation pipeline
def extract_entities(file_path):
    entities = list()
    with open(file_path, mode='r', encoding='UTF-8') as sentFile:
        lines = sentFile.readlines()
        for line in lines:
            openingBracketIter = re.finditer("\{", line)
            closingBracketIter = re.finditer("\}", line)
            for m1, m2 in zip(openingBracketIter, closingBracketIter):
                entities.append(str(line[m1.end():m2.start()]).lower())

    return entities


@plac.annotations(
    input_dir=('Directory containing .txt files to be turned into binary files used in training/testing an NLP model.',
               'positional'),
    output_dir=('Directory where the training/testing binaries will be located.', 'positional')
)
def main(input_dir=None, output_dir=None):
    if input_dir is None:
        print('Please enter dir Path')
        raise SystemExit(1)
    if output_dir is None or not os.path.exists(output_dir):
        os.makedirs(output_dir)

    entities = list()
    for file in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file)
        entities += (extract_entities(file_path))
    output_file = os.path.join(output_dir, 'all_entities.csv')
    with open(output_file, encoding='utf-8', mode='a') as f:
        f.writelines(','.join(entities))


if __name__ == '__main__':
    plac.call(main)
