import json
import logging


def tsv_to_json_format(input_path, output_path, unknown_label):
    try:
        f = open(input_path, 'r', encoding='utf-8')  # input file
        fp = open(output_path, 'w', encoding='utf-8')  # output file
        data_dict = {}
        annotations = []
        label_dict = {}
        s = ''
        start = 0
        for line in f:
            # if its NOT the end of the sentence
            if line[0:len(line) - 1] != '.\tO':
                word, entity = line.split('\t')
                s += word + " "
                entity = entity[:len(entity) - 1]
                if entity != unknown_label:
                    if len(entity) != 1:
                        d = {}
                        d['text'] = word
                        d['start'] = start
                        d['end'] = start + len(word) - 1
                        try:
                            label_dict[entity].append(d)
                        except:
                            label_dict[entity] = []
                            label_dict[entity].append(d)
                start += len(word) + 1

            else:
                data_dict['content'] = s
                s = ''
                label_list = []
                for ents in list(label_dict.keys()):
                    for i in range(len(label_dict[ents])):
                        if (label_dict[ents][i]['text'] != ''):
                            l = [ents, label_dict[ents][i]]
                            for j in range(i + 1, len(label_dict[ents])):
                                if (label_dict[ents][i]['text'] == label_dict[ents][j]['text']):
                                    di = {}
                                    di['start'] = label_dict[ents][j]['start']
                                    di['end'] = label_dict[ents][j]['end']
                                    di['text'] = label_dict[ents][i]['text']
                                    l.append(di)
                                    label_dict[ents][j]['text'] = ''
                            label_list.append(l)

                for entities in label_list:
                    label = {}
                    label['label'] = [entities[0]]
                    label['points'] = entities[1:]
                    annotations.append(label)
                data_dict['annotation'] = annotations
                annotations = []
                json.dump(data_dict, fp)
                fp.write('\n')
                data_dict = {}
                start = 0
                label_dict = {}
    except Exception as e:
        logging.exception("Unable to process file" + "\n" + "error = " + str(e))
        return None


tsv_to_json_format(
    r"C:\Users\Gjorgji Noveski\Desktop\test\activation function model\activation function model.tsv",
    r"C:\Users\Gjorgji Noveski\Desktop\test\activation function model\activation function model.json",
    'abc')
tsv_to_json_format(
    r"C:\Users\Gjorgji Noveski\Desktop\test\architecture type model\architecture type model.tsv",
    r"C:\Users\Gjorgji Noveski\Desktop\test\architecture type model\architecture type model.json",
    'abc')
tsv_to_json_format(
    r"C:\Users\Gjorgji Noveski\Desktop\test\building blocks model\building blocks model.tsv",
    r"C:\Users\Gjorgji Noveski\Desktop\test\building blocks model\building blocks model.json",
    'abc')
tsv_to_json_format(
    r"C:\Users\Gjorgji Noveski\Desktop\test\dataset model\dataset model.tsv",
    r"C:\Users\Gjorgji Noveski\Desktop\test\dataset model\dataset model.json",
    'abc')