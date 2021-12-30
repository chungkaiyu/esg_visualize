import pandas as pd
import numpy as np
import os
from esg_evaluator import *

class bubble_plot:
    def __init__(self) -> None:
        pass
    def is_csv_exist(self,filename):
        tmp_dir='static/tmp/'
        if os.path.isfile(tmp_dir+filename.split('.')[0]+'.csv'):
            return True
        return False
    def produce_csv(self,filename):
        tmp_dir='static/tmp/'
        input_dir='static/input/'
        dp = DocProcessor()
        print(filename, end=' => ')
        text = dp.get_file_text(input_dir+filename)
        btm = BERT_model(text)
        df = btm.get_issue_keywords(kp_list=True)
        weight = btm.get_key_issue_weight(df)
        file_name = filename.split(".")[0]
        weight.to_csv(tmp_dir+file_name+".csv")
    def produce_plot_weight(self,filename,num):
        tmp_dir='static/tmp/'
        sort_name='Percentage'
        file_name=tmp_dir+filename.split('.')[0]+'.csv'
        E,S,G = list(),list(),list()
        df = pd.DataFrame()
        tmp = pd.read_csv(file_name)
        tmp = tmp.sort_values(sort_name,ascending=False).groupby('Pillar').head(num)
        df = pd.concat([df,tmp],axis=0,ignore_index=True)
        MinMaxScaler=df['MinMaxScaler'].to_list()
        Year=2018
        Weight=df['Weight'].to_list()
        Pillar=df['Pillar'].to_list()
        Key_issue=df['Key_issue'].to_list()
        for i in range(len(MinMaxScaler)):
            tmp=[Year,MinMaxScaler[i],Weight[i],Key_issue[i]]
            if Pillar[i]=='Environment':
                E.append(tmp)
            elif Pillar[i]=='Social':
                S.append(tmp)
            else:
                G.append(tmp)
        return E, S, G
    def bubble_weight(self,filename,num=3):
        if not self.is_csv_exist(filename):
            self.produce_csv(filename)
        return self.produce_plot_weight(filename,num)