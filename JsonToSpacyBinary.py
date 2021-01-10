import plac
import json
import pickle
import random
import os


@plac.annotations(input_file=("Input file", "option", "i", str),
                  output_dir=("Output directory", "option", "o", str),
                  train_test_split=(
                  'Real value from 0.0 - 1.0  to represent how much of the json data to be used for training.'
                  ' Eg. -split 0.6, will write 2 bin files, first one will have 60% of the content of the json file,'
                  ' and the second will get the remainder.', 'option', 'split', float))
def main(input_file=None, output_dir=None, train_test_split=None):
    if not os.path.isfile(input_file):
        print('Please specify an input file')
        raise SystemExit(1)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    if train_test_split is None:
        outputFileName = os.path.basename(input_file).split('.')[0] + '.bin'
        convert(lines, os.path.join(output_dir, outputFileName))

    else:
        split = int(len(lines) * train_test_split)
        random.shuffle(lines)
        train_data = lines[:split]
        test_data = lines[split:]
        convert(train_data, os.path.join(output_dir, 'train_data.bin'))
        convert(test_data, os.path.join(output_dir, 'test_data.bin'))


def convert(lines, output_file):
    training_data = []
    for line in lines:
        data = json.loads(line)
        text = data['content']
        entities = []

        for annotation in data['annotation']:
            points = annotation['points']
            label = annotation['label'][0]
            if not isinstance(points, list):
                points = [points]
            for point in points:
                entities.append((point['start'], point['end'] + 1, label))

        training_data.append((text, {"entities": entities}))

    with open(output_file, 'wb') as fp:
        pickle.dump(training_data, fp)



if __name__ == '__main__':
    plac.call(main)


