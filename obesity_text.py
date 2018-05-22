import xml.etree.ElementTree as et
import xml.dom.minidom as Dom
import sys
import os
import numpy as np
from keras.preprocessing import text

import random
import pickle as pk
from collections import Counter


#from cnews_loader import *

def save_obj(obj, name ):
    with open(name + '.pkl', 'wb') as f:
        pk.dump(obj, f, pk.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open( name + '.pkl' , 'rb') as f:
        return pk.load(f)
    

def create_corpus(corp_name,
                  word_file):
    f = open(corp_name,'r')
    content = f.read()
    f.close()
    corpus_file = open(word_file,'w')
    records = content.strip().split('RECORD #')
    corpus = {}
    for record in records:       
        if(record.find('[report_end]') != -1):
            id = int(record[:record.find('\n')])
            content = record[record.find('\n') + 1: record.find('[report_end]')].strip()
            content = expand_abbr(content)
            content = content.replace('\'s', " 's").replace("'d", " 'd")
            content = content.replace("'s", " 's")
            content = content.replace("can't", "can not")
            content = content.replace("couldn't", "could not")
            content = content.replace("won't", "will not")
            content = content.replace("wasn't", "was not")
            content = content.replace("hasn't", "has not")
            content = content.replace("don't", "do not")
            content = content.replace("didn't", "did not")
            content = content.replace("doesn't", "does not")

            word_list = text.text_to_word_sequence(content, lower=True, split=" ", filters='"#$%&()*+/<=>@[\\]^_`{|}~\t\n')
            #word_list = text.text_to_word_sequence(content, lower=True, split=" ")
            word_list = clean_wds(word_list)
            #filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n'
            str_to_write = ' '.join(word_list)
            corpus[id]=word_list
            corpus_file.write(str_to_write + '\n')
    print(len(corpus))
    corpus_file.close()
    
    save_obj(corpus, word_file)
    return corpus

def entity_corpus(filename='CUIs_text.txt'):
    f = open(filename,'r')
    content = f.read()
    f.close()
    record = content.strip().split('\n')
    corpus = {i+1:record[i].split() for i in range(len(record))}
    return corpus

def get_dic(xmlfile):
    #get dict from xml
    train_labels = et.parse(xmlfile)
    root = train_labels.getroot()
    dic = {}
    for child in root:
        key = child.attrib['source']
        sub_dic = {}
        for sub_child in child:
            sub_key =  sub_child.attrib['name']
            sub_sub_dic = {}
            for sub_sub_child in sub_child:
                sub_sub_dic[int(sub_sub_child.attrib['id'])]=sub_sub_child.attrib['judgment']
            sub_dic[sub_key]= sub_sub_dic
        dic[key] = sub_dic    
    return dic

def dic2xml(dic,savename):
    doc = Dom.Document() 
    root_node = doc.createElement("diseaseset")
    doc.appendChild(root_node) 
    for t in dic:
        source_node = doc.createElement("diseases")
        source_node.setAttribute("source", t)
        root_node.appendChild(source_node)
        for d in dic[t]:
            disease_node = doc.createElement("disease")
            disease_node.setAttribute("name", d)
            source_node.appendChild(disease_node)
            for c in dic[t][d]:
                doc_node = doc.createElement("doc")
                doc_node.setAttribute("id", str(c))
                doc_node.setAttribute("judgment", dic[t][d][c])
                disease_node.appendChild(doc_node) 
    f = open(savename, "wb+") 
    f.write(doc.toprettyxml(indent = "", newl = "\n", encoding = "utf-8")) 
    f.close() 


def build_vocab_words(corpus, vocab_dir, vocab_size=10000):
    ct=Counter()
    for i in corpus:
        ct = ct + Counter(corpus[i])
    count_pairs = ct.most_common(vocab_size-1)
    words = list(zip(*count_pairs))[0]
    
    words = ['<PAD>'] + list(words)
    f = open_file(vocab_dir, mode='w')
    f.write('\n'.join(words) + '\n')
    f.close()
    word_to_id = dict(zip(words, range(len(words))))
    return words, word_to_id

def get_sub_embedding(word_vector_map, words, vocab_size, embedding_dim):
    sub_embedding = np.random.uniform(-0.0, 0.0, (vocab_size , embedding_dim))
    for i in range(vocab_size):
        if words[i] in word_vector_map:
            sub_embedding[i] = word_vector_map[words[i]]
    return sub_embedding

def pad_corpus_id(corpus,word_to_id, max_length =5000):
    id_corpus={}
    for k in corpus:
        data_id = [word_to_id[x] for x in corpus[k] if x in word_to_id]
        id_corpus[k]=kr.preprocessing.sequence.pad_sequences([data_id], max_length,padding='post', truncating='post')[0]
    return id_corpus

def get_input(data_dic, id_corpus, cat_to_id):
    ids=[]
    labels=[]
    record_id=[]
    for s in data_dic:
        ids.append(id_corpus[s])
        labels.append(kr.utils.to_categorical(cat_to_id[data_dic[s]], num_classes=len(cat_to_id))[0])
        record_id.append(s)
    return np.array(ids), np.array(labels),record_id
        
    
def coverNQ(pred_xml,true_xml):
    true_dic = get_dic(true_xml)
    pred_dic = get_dic(pred_xml)
    for t in true_dic:
        for ds in true_dic[t]:
            for c in true_dic[t][ds]:
                if t=='intuitive' and true_dic[t][ds][c]=='Q':
                    pred_dic[t][ds][c]='Q'
                if t=='textual' and true_dic[t][ds][c] in 'QN':
                    pred_dic[t][ds][c]=true_dic[t][ds][c]
    dic2xml(pred_dic,pred_xml[:-4]+'_cover.xml')            
    return pred_dic

    
    

