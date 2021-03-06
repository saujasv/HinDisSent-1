# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import os
import numpy as np
import torch


def get_batch(batch, word_vec, emb_dim=300):
    # sent in batch in decreasing order of lengths (bsize, max_len, word_dim)
    lengths = np.array([len(x) for x in batch])
    max_len = np.max(lengths)
    embed = np.zeros((max_len, len(batch), emb_dim))
    word_vec['<s>'] = np.mean(np.stack(word_vec.values(), axis=0), axis=0)
    word_vec['</s>'] = np.mean(np.stack(word_vec.values(), axis=0), axis=0)
    
    for i in range(len(batch)):
        for j in range(len(batch[i])):
            
            try:
                embed[j, i, :] = word_vec[batch[i][j]]
            except Exception as e:
                print("e",e)
                pass
    return torch.from_numpy(embed).float(), lengths


def get_word_dict(sentences):
    # create vocab of words
    word_dict = {}
    for sent in sentences:
        for word in sent.split():
            if word not in word_dict:
                word_dict[word] = ''
    word_dict['<s>'] = ''
    word_dict['</s>'] = ''
    word_dict['<p>'] = ''
    return word_dict


def get_glove(word_dict, glove_path):
    # create word_vec with glove vectors
    word_vec = {}
    with open(glove_path) as f:
        for line in f:
            word, vec = line.split(' ', 1)
            if word in word_dict:
                word_vec[word] = np.array(list(map(float, vec.split())))
    print('Found {0}(/{1}) words with glove vectors'.format(
                len(word_vec), len(word_dict)))
    return word_vec


def build_vocab(sentences, glove_path):
    word_dict = get_word_dict(sentences)
    word_vec = get_glove(word_dict, glove_path)
    print('Vocab size : {0}'.format(len(word_vec)))
    return word_vec


def get_nli(data_path, disc_markers):
    s1 = {}
    s2 = {}
    target = {}

    dico_label = {line.rstrip(): i for i, line in enumerate(open(os.path.join(data_path, disc_markers)))}

    for data_type in ['train', 'dev', 'test']:
        s1[data_type], s2[data_type], target[data_type] = {}, {}, {}
        s1[data_type]['path'] = os.path.join(data_path, 's1.' + data_type)
        s2[data_type]['path'] = os.path.join(data_path, 's2.' + data_type)
        target[data_type]['path'] = os.path.join(data_path,
                                                 'labels.' + data_type)
        markers = [line.rstrip() for line in open(os.path.join(data_path,disc_markers), 'r')]
        
        idx = [True if line.rstrip() in markers else False for i, line in enumerate(open(target[data_type]['path'], 'r'))]

        
        
        s1_list = [line.rstrip() for i, line
                in enumerate(open(s1[data_type]['path'], 'r')) if idx[i]]
        
        s2_list = [line.rstrip() for i, line in
                                 enumerate(open(s2[data_type]['path'], 'r'))  if idx[i]]
        
        target_list = np.array([dico_label[line.rstrip('\n')]
                for i, line in enumerate(open(target[data_type]['path'], 'r')) if idx[i]])

        assert len(s1_list) == len(s2_list) == \
            len(target_list)
        
        s1[data_type]['sent'] = list()
        s2[data_type]['sent'] = list()
        target[data_type]['data'] = list()

        MIN_LEN = 3
        for i in range(len(s1_list)):
            if len(s1_list[i].split()) > MIN_LEN and len(s2_list[i].split()) > MIN_LEN:
                s1[data_type]['sent'].append(s1_list[i])
                s2[data_type]['sent'].append(s2_list[i])
                target[data_type]['data'].append(target_list[i])

        target[data_type]['data'] = np.array(target[data_type]['data'])

        print('** {0} DATA : Found {1} pairs of {2} sentences.'.format(
                data_type.upper(), len(s1[data_type]['sent']), data_type))

    train = {'s1': s1['train']['sent'], 's2': s2['train']['sent'],
             'label': target['train']['data']}
    dev = {'s1': s1['dev']['sent'], 's2': s2['dev']['sent'],
           'label': target['dev']['data']}
    test = {'s1': s1['test']['sent'], 's2': s2['test']['sent'],
            'label': target['test']['data']}
    return train, dev, test
