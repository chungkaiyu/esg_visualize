import pandas as pd
import json
import re
import os

from sentence_transformers import SentenceTransformer, util
import torch

this_dir, this_filename = os.path.split(__file__)
ESG_PATH = os.path.join(this_dir, "static", "ESG_Key_Issue.xlsx")
SDG_PATH = os.path.join(this_dir, "static", "SDG_Key_Issues.xlsx")

class BERT_model:
    def __init__(self,text, model = "all-MiniLM-L6-v2", ESG_Key_Issue_file=ESG_PATH):
        regex = re.compile('[^a-zA-Z]')
        text = regex.sub(' ',text)
        text = text.lower() 
        self.document_text = text
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.ESG_Key_Issue_file = ESG_Key_Issue_file
    
    def set_document_text(self, text):
        self.document_text = text

    def word_embedding(self,word_list):
        embedding = self.model.encode(word_list, convert_to_tensor=True)
        
        return embedding

    def read_key_issue(self):
        df = pd.read_excel(self.ESG_Key_Issue_file)
        return df

    def get_issue_keywords(self, top_k=15, show_column=['Count', 'Similarity', 'Embedding'], kp_list = False):
        issue_df = pd.read_excel(self.ESG_Key_Issue_file)
        key_issue_list = list(issue_df['ESG Key Issue'])
        pillar_words = list(issue_df['Pillars'])

        corpus = [w for w in set(self.document_text.split()) if len(w) > 2] # Word List that contain every distinct word that appear in the pdf file
        query = key_issue_list # ESG Key Issue List

        # Transform list data into embeddings
        corpus_embeddings = self.model.encode(corpus, convert_to_tensor=True)
        query_embedding  = self.model.encode(query, convert_to_tensor=True)

        esg_emb_pd = pd.DataFrame(query_embedding.cpu().numpy())
        cor_emb_pd = pd.DataFrame(corpus_embeddings.cpu().numpy())

        # semantic_search can get the most similar n corpus_embeddings for every query_embedding
        data = util.semantic_search(query_embedding, corpus_embeddings, top_k=top_k)

        df = pd.DataFrame(columns=['Key_issue', 'Pillar', 'Doc_word', 'Count', 'Similarity', 'Embedding'])

        for issue_i in range(len(key_issue_list)):
            for word in data[issue_i]:
                df = df.append({'Key_issue': key_issue_list[issue_i], # ESG Key Issue
                        'Pillar': pillar_words[issue_i],
                        'Doc_word': corpus[word['corpus_id']], # words from document that similar to correspond key_issue
                        'Count': self.document_text.count(corpus[word['corpus_id']]), # how many time did doc_word appear in document
                        'Similarity': round(word['score'],4), # Cosine Similarity between key_issue and doc_word
                        'Embedding': cor_emb_pd.loc[word['corpus_id']].values}, ignore_index=True) 

        # output key phrase list
        if kp_list:
            kp_dict={}

            kp_tmp = df.groupby('Pillar')
            for p in kp_tmp.groups.keys():
                kp_dict[p]=list(set(kp_tmp.get_group(p)['Doc_word']))

            with open('key_phrase.txt', 'w', encoding='utf-8') as outfile:
                json.dump(kp_dict, outfile)

        return df[['Key_issue', 'Pillar', 'Doc_word'] + show_column]

    def get_key_issue_weight(self,df,value_list=['Weight', 'Percentage', 'MinMaxScaler']):
        input_df = df[['Pillar', 'Key_issue', 'Count', 'Similarity']]
        input_df['Weight'] = input_df['Count'] * input_df['Similarity']

        k_df = input_df.groupby(['Pillar','Key_issue'])['Weight'].sum()
        p_df = input_df.groupby('Pillar')['Weight'].sum()

        t = []
        for i in range(len(k_df)):
            t.append(k_df[i] / p_df[k_df.index[i][0]])
        weight = pd.DataFrame(k_df).reset_index(level=[0,1])
        weight['Percentage'] = t

        mmstmp = weight.groupby("Pillar")['Weight']
        min_, max_ = mmstmp.transform('min'), mmstmp.transform('max')
        weight['MinMaxScaler'] = (weight['Weight'] - min_) / (max_ - min_)

        return weight[['Pillar', 'Key_issue'] + value_list]
