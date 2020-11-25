import json
import logging
nnn=1
def tsv_to_json_format(input_path, output_path, unknown_label):
    global nnn
    try:
        f = open(input_path, 'r')  # input file
        #fp = open(output_path, 'w')  # output file
        fw = open("C:/Users/Gjorgji Noveski/Desktop/Files for my Spacy work/Corpora - text with annotated , { }/sents for evaluation a model.txt",'w')
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
                content = s

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
                # ('I like London and Berlin.',
                #      [(7, 13, 'LOC'), (18, 24, 'LOC')])
                data_dict['annotation'] = annotations
                THEREALstartlistendlist= []
                for tmp in data_dict['annotation']:
                    ent = tmp['label'][0]
                    startEndList = []
                    for lblDic in tmp['points']:
                        THESTART = lblDic['start']
                        THEEND = lblDic['end']
                        startEndList.append((THESTART,THEEND,ent))
                    THEREALstartlistendlist.extend(startEndList)
                print((content,THEREALstartlistendlist))

                print("\n\n\n")
                annotations = []
                #json.dump(data_dict, fp)
                #fp.write('\n')
                data_dict = {}
                start = 0
                label_dict = {}
    except Exception as e:
        logging.exception("Unable to process file" + "\n" + "error = " + str(e))
        return None


tsv_to_json_format("C:/Users/Gjorgji Noveski/Desktop/Files for my Spacy work/Corpora - text with annotated , { }/taggedCorpus.tsv",
                   'C:/Users/Gjorgji Noveski/Desktop/Files for my Spacy work/Corpora - text with annotated , { }/taggedCorpus.json', 'abc')