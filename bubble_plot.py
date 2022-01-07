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
    def produce_plot_weight(self,filename,num=3,label=''):
        tmp_dir='static/tmp/'
        sort_name='Percentage'
        file_name=tmp_dir+filename.split('.')[0]+'.csv'
        E,S,G = list(),list(),list()
        df = pd.DataFrame()
        tmp = pd.read_csv(file_name)
        tmp = tmp.sort_values(sort_name,ascending=False).groupby('Pillar').head(num)
        df = pd.concat([df,tmp],axis=0,ignore_index=True)
        MinMaxScaler=df['MinMaxScaler'].to_list()
        Year=label
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
    def bubble_weight_single(self,filename,label,num=3):
        if not self.is_csv_exist(filename):
            self.produce_csv(filename)
        return self.produce_plot_weight(filename,num,label=label)
    def getcompanyfiles(self,comapny_name):
        tmp_dir='static/tmp/'
        files=list()
        for filename in os.listdir(tmp_dir):
            if comapny_name in filename and '.csv' in filename:
                files.append(filename)
        return files
    def get_year(self,name):
        for i in range(len(name)-3):
            if name[i:i+4].isdigit() and int(name[i:i+4]) > 2000:
                return name[i:i+4]
        return ''
    def bubble_weight_multi(self,comapny_name,num=3):
        comapny_name='TSMC'#正式接好就把這一行刪了
        files=self.getcompanyfiles(comapny_name)
        E, S, G = list(),list(),list()
        for filename in files:
            #year=filename.split('-')[1]
            year=self.get_year(filename.split('.')[0])
            tmp_E,tmp_S,tmp_G = self.bubble_weight_single(filename,label=year)
            E+=tmp_E
            S+=tmp_S
            G+=tmp_G
        return E,S,G
    